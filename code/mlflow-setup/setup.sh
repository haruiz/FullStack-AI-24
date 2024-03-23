PERFORM_RESET=0
RECREATE_KEY_FILE=0
PROJECT_ID="uao-mlflow-intro"
PROJECT_DESCRIPTION="UAO MLFlow Intro"
DEFAULT_REGION="us-central1"
DEFAULT_ZONE="us-central1-a"

# reset gcloud settings
if [ $PERFORM_RESET -eq 1 ]; then
    echo "Resetting gcloud"
    rm -rf ~/.config/gcloud
    gcloud auth login
fi

# 1. create project
gcloud projects list | grep $PROJECT_ID
if [ $? -eq 0 ]; then
    echo "Project $PROJECT_ID already exists"
else
    echo "Creating project $PROJECT_ID"
    gcloud projects create $PROJECT_ID --name="$PROJECT_DESCRIPTION" --set-as-default --enable-cloud-apis
fi

gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com


# 2. set the create project as the default
gcloud config set project $PROJECT_ID

# 3. enable billing
gcloud alpha billing accounts list
if [ $? -eq 0 ]; then
    echo "Billing account already exists"
else
    echo "Creating billing account"
    gcloud alpha billing accounts create --display-name=$PROJECT_ID-billing
fi
BILLING_ACCOUNT_ID=$(gcloud alpha billing accounts list --format=json | jq -r '.[0].name' | cut -d'/' -f2)
echo "BILLING_ACCOUNT_ID: $BILLING_ACCOUNT_ID"
# link the billing account to the project
gcloud alpha billing projects link $PROJECT_ID --billing-account="$BILLING_ACCOUNT_ID"

# 4. create service accounts
SERVICE_ACCOUNT_ID=sa-$PROJECT_ID
SERVICE_ACCOUNT_EMAIL=$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com
SERVICE_ACCOUNT_DISPLAY_NAME="MLFlow deployment service account"
SERVICE_ACCOUNT_DESCRIPTION="This service account is used to deploy the mlflow backend"

gcloud iam service-accounts list | grep $SERVICE_ACCOUNT_ID
if [ $? -eq 0 ]; then
    echo "Service account $SERVICE_ACCOUNT_ID already exists"
else
    echo "Creating service account $SERVICE_ACCOUNT_ID"
    gcloud iam service-accounts create $SERVICE_ACCOUNT_ID \
        --description="$SERVICE_ACCOUNT_DESCRIPTION" \
        --display-name="$SERVICE_ACCOUNT_DISPLAY_NAME" \
        --quiet
fi


# 6. grant the service account the roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/owner"


# 7. create key file for the service account
KEY_FILE=./secrets/$SERVICE_ACCOUNT_ID.json
if [ $RECREATE_KEY_FILE -eq 1 ]; then
    # delete all keys
    gcloud iam service-accounts keys list --iam-account=$SERVICE_ACCOUNT_EMAIL | grep $SERVICE_ACCOUNT_EMAIL
    if [ $? -eq 0 ]; then
        echo "Deleting all keys for service account $SERVICE_ACCOUNT_ID"
        gcloud iam service-accounts keys list --iam-account=$SERVICE_ACCOUNT_EMAIL --format=json | jq -r '.[].name' | while read key; do
            gcloud iam service-accounts keys delete $key --iam-account=$SERVICE_ACCOUNT_EMAIL --quiet
        done
    fi
    # create key file
    gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com
fi


# set key as environment variable
export GOOGLE_APPLICATION_CREDENTIALS=$KEY_FILE

# 8. create MLflow database
INSTANCE_NAME=mlflow-postgres
DATABASE_VERSION=POSTGRES_13
NUMBER_CPUS=1
MEMORY=3840MiB
STORAGE_TYPE=SSD
INSTANCE_PASSWORD="mlflow"

gcloud sql instances list | grep $INSTANCE_NAME
if [ $? -eq 0 ]; then
    echo "Cloud SQL instance $INSTANCE_NAME already exists"
else
    echo "Creating Cloud SQL instance $INSTANCE_NAME"
    gcloud sql instances create $INSTANCE_NAME \
        --database-version=$DATABASE_VERSION \
        --cpu=$NUMBER_CPUS \
        --memory=$MEMORY \
        --region=$DEFAULT_REGION \
        --storage-type=$STORAGE_TYPE

    #create password for the instance
    gcloud sql users set-password postgres \
      --instance=$INSTANCE_NAME \
      --password=$INSTANCE_PASSWORD
fi

# 9. create MLflow database
DATABASE_NAME=mlflow-db
DATABASE_USER=mlflow-usr
DATABASE_USER_PASSWORD=mlflow-pass

gcloud sql databases list --instance=$INSTANCE_NAME | grep $DATABASE_NAME
if [ $? -eq 0 ]; then
    echo "Database $DATABASE_NAME already exists"
else
    echo "Creating database $DATABASE_NAME"
    gcloud sql databases create $DATABASE_NAME --instance=$INSTANCE_NAME
    # create user for the database
    gcloud sql users create $DATABASE_USER \
        --instance=$INSTANCE_NAME \
        --password=$DATABASE_USER_PASSWORD
fi

# create client certificate
CERT_NAME=mlflow-client-cert
CLIENT_KEY_FILE=./secrets/client-key.pem
CLIENT_CERT_FILE=./secrets/client-cert.pem
SERVER_CA_FILE=./secrets/server-ca.pem

gcloud sql ssl client-certs list --instance=$INSTANCE_NAME | grep $CERT_NAME
if [ $? -eq 0 ]; then
    echo "Client certificate $CERT_NAME already exists"
else
    echo "Creating client certificate $CERT_NAME"
    gcloud sql ssl client-certs create $CERT_NAME $CLIENT_KEY_FILE \
    --instance=$INSTANCE_NAME

    echo "Downloading client certificate $CERT_NAME"
    gcloud sql ssl client-certs describe $CERT_NAME \
    --instance=$INSTANCE_NAME \
    --format="value(cert)" > $CLIENT_CERT_FILE

    echo "Downloading client certificate key $CERT_NAME"
    gcloud sql instances describe $INSTANCE_NAME \
    --format="value(serverCaCert.cert)" > $SERVER_CA_FILE
fi

# 10. create bucket for MLflow artifacts
BUCKET_NAME=$PROJECT_ID-mlflow-artifacts
gcloud storage buckets list | grep $BUCKET_NAME
if [ $? -eq 0 ]; then
    echo "Bucket $BUCKET_NAME already exists"
else
    echo "Creating bucket $BUCKET_NAME"
    gsutil mb -l $DEFAULT_REGION gs://$BUCKET_NAME
fi

# secret manager
MLFlow_ARTIFACT_URI="gs://$BUCKET_NAME"
MLFlow_DATABASE_CONN_STR="postgresql+pg8000://$DATABASE_USER:$DATABASE_USER_PASSWORD@//?unix_sock=/cloudsql/$PROJECT_ID:$DEFAULT_REGION:$INSTANCE_NAME"
MLFlow_TRACKING_USERNAME="mlflow"
MLFlow_TRACKING_PASSWORD="mlflow"

echo $MLFlow_ARTIFACT_URI | gcloud secrets create mlflow_artifact_url --data-file=- --replication-policy=automatic
echo $MLFlow_DATABASE_CONN_STR | gcloud secrets create mlflow_database_url --data-file=- --replication-policy=automatic
echo $MLFlow_TRACKING_USERNAME | gcloud secrets create mlflow_tracking_username --data-file=- --replication-policy=automatic
echo $MLFlow_TRACKING_PASSWORD | gcloud secrets create mlflow_tracking_password --data-file=- --replication-policy=automatic
