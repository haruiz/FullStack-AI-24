MODEL_NAME=iris-classification-model
MODEL_ALIAS="production"
#MODEL_VERSION=1

export MLFLOW_TRACKING_URI=http://0.0.0.0:4001
mlflow models serve --model-uri models:/$MODEL_NAME@$MODEL_ALIAS -p 8081 --no-conda
#mlflow models serve --model-uri models:/$MODEL_NAME/$MODEL_VERSION -p 8081 --no-conda
