#!/bin/bash

# Export the env args in .env file.
[ ! -f .env ] || export $(grep -v '^#' .env | xargs)

# Check the docker compose command version
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &>"/dev/null"; then
  # Use old version commands
  DOCKER_COMPOSE_CMD="docker-compose"
else
  # Use new version commands
  DOCKER_COMPOSE_CMD="docker compose"
fi

# Remove old images
docker rmi petsservice/fastapi:$IMAGE_TAG
docker rmi petsservice/redis:$IMAGE_TAG
docker rmi petsservice/celery:$IMAGE_TAG
docker rmi petsservice/flower:$IMAGE_TAG

# Build image
$DOCKER_COMPOSE_CMD build
