IMAGE_NAME="model-garden-frontend:latest"
CONTAINER_NAME="model-garden-web"
RUN_INTERACTIVE=TRUE    
PORT=8501
API_URL="http://localhost:8000"
# list all running containers
#docker ps -a

if docker inspect -f '{{.Config.Image}}' $CONTAINER_NAME >/dev/null 2>&1; then
    echo "Stopping running containers..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# check if image exists and remove it
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" != "" ]]; then
  echo "Image $IMAGE_NAME exists. Removing image..."
  docker rmi $IMAGE_NAME
fi

# create docker image
docker build -t $IMAGE_NAME .

# run the container
if $RUN_INTERACTIVE; then
  echo "Running container in interactive mode..."
  docker run -it --name $CONTAINER_NAME -v $(pwd):/app  -p $PORT:8501 -e API_URL=$API_URL $IMAGE_NAME 
  exit 0
else
    echo "Running container in detached mode..."
    docker run -d --name $CONTAINER_NAME -v $(pwd):/app  -p $PORT:8501 -e API_URL=$API_URL $IMAGE_NAME 
    # open shell in container
    docker exec -it $CONTAINER_NAME /bin/bash
    exit 0
fi