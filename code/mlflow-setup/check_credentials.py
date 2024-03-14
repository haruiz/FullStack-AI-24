from google.cloud import secretmanager
from dotenv import load_dotenv

load_dotenv()

project_id = "uao-mlflow-intro"
version = "latest"
secrets = [
    "mlflow_artifact_url",
    "mlflow_database_url",
    "mlflow_tracking_username",
    "mlflow_tracking_password"
]
client = secretmanager.SecretManagerServiceClient()
if __name__ == '__main__':
    print("Checking secrets...")
    for secret_id in secrets:
        response = client.access_secret_version(
            request={"name": f"projects/{project_id}/secrets/{secret_id}/versions/{version}"}
        )
        payload = response.payload.data
        print(payload)