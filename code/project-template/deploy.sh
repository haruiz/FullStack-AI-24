PROJECT_ID="uao-course-model-garden-prj"
PROJECT_NAME="Model Garden"
REGION="us-central1"
PERFORM_RESET=0
FRONTEND_IMAGE="gcr.io/model-garden-frontend:latest"
BACKEND_IMAGE="gcr.io/model-garden-backend:latest"

# reset gcloud settings
if [ $PERFORM_RESET -eq 1 ]; then
    echo "Resetting gcloud"
    rm -rf ~/.config/gcloud
    gcloud auth login
fi

# create project
gcloud projects list | grep $PROJECT_ID
if [ $? -eq 0 ]; then
    echo "Project $PROJECT_ID already exists"
else
    echo "Creating project $PROJECT_ID"
    gcloud projects create $PROJECT_ID --name=$PROJECT_NAME --set-as-default --enable-cloud-apis
fi

# set project
gcloud config set project $PROJECT_ID
# enable billing
gcloud alpha billing accounts list
if [ $? -eq 0 ]; then
    echo "Billing account already exists"
else
    echo "Creating billing account"
    gcloud alpha billing accounts create --display-name=$PROJECT_ID-billing
fi

BILLING_ACCOUNT_ID=$(gcloud alpha billing accounts list --format=json | jq -r '.[0].name' | cut -d'/' -f2)
gcloud alpha billing projects link $PROJECT_ID --billing-account="$BILLING_ACCOUNT_ID"


