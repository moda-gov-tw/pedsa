#!/bin/bash

if [ "$1" == "dev" ]; then
    ln -sf dev.dockerfile Dockerfile
    ln -sf dev-docker-compose.yaml docker-compose.yaml
    echo "switch to dev mode"
elif [ "$1" == "dep" ]; then
    ln -sf deploy.dockerfile Dockerfile
    ln -sf deploy-docker-compose.yaml docker-compose.yaml
    echo "switch to deploy mode"
else
    echo "Input error. Please enter dev (Next.js in development mode) or dep (Next.js production deploy mode)."
fi