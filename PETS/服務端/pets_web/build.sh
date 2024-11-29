#!/bin/bash

# Export the env args in .env file.
[ ! -f .env ] || export $(grep -v '^#' .env | xargs)

# Create variable image:tag from .env file
DOCKER_IMAGE_WILL_BUILD="$DOCKER_BUILD_IMAGE_NAME:$DOCKER_BUILD_IMAGE_TAG"

# Check the docker compose command version
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &>"/dev/null"; then
  # Use old version commands
  DOCKER_COMPOSE_CMD="docker-compose"
else
  # Use new version commands
  DOCKER_COMPOSE_CMD="docker compose"
fi

OLD_IMAGE_ID=""
if [ -n "$(docker images -q $DOCKER_IMAGE_WILL_BUILD)" ]; then
  # If the image:tag exists, save the image ID
  OLD_IMAGE_ID=$(docker images -q $DOCKER_IMAGE_WILL_BUILD)
  echo "Old docker image id: $OLD_IMAGE_ID"
fi

# Build image
$DOCKER_COMPOSE_CMD build

# Delete the old image
if [ -z "$OLD_IMAGE_ID" ]; then
  docker rmi $OLD_IMAGE_ID && echo "Old docker image $OLD_IMAGE_ID deleted"
fi
