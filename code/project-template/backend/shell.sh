CONTAINER_NAME="model-garden-api"

if docker inspect -f '{{.Config.Image}}' $CONTAINER_NAME >/dev/null 2>&1; then
    docker exec -it $CONTAINER_NAME /bin/bash
fi