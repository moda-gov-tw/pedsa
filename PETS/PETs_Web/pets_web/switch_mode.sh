#!/bin/bash

thisDirPath=$(realpath "$0")
baseDir=$(dirname "$thisDirPath")

ip=$2

if [ "$1" == "dev" ]; then
    NEXTAUTH_PORT=8081
    export NEXTAUTH_PORT
    sed -i "s/NEXTAUTH_URL=.*/NEXTAUTH_URL=\'http:\/\/localhost:$NEXTAUTH_PORT\/\'/g" $baseDir/.env
    DOCKER_BUILD_IMAGE_TAG='1.0-dev'
    export DOCKER_BUILD_IMAGE_TAG
    sed -i "s/DOCKER_BUILD_IMAGE_TAG=.*/DOCKER_BUILD_IMAGE_TAG=\'$DOCKER_BUILD_IMAGE_TAG\'/g" $baseDir/.env
    ln -sf dev.dockerfile Dockerfile
    ln -sf dev-docker-compose.yaml docker-compose.yaml
    echo "switch to dev mode"
elif [ "$1" == "dep" ]; then
    NEXTAUTH_PORT=3000
    export NEXTAUTH_PORT
    sed -i "s/NEXTAUTH_URL=.*/NEXTAUTH_URL=\'http:\/\/localhost:$NEXTAUTH_PORT\/\'/g" $baseDir/.env
    ln -sf deploy.dockerfile Dockerfile
    ln -sf deploy-docker-compose.yaml docker-compose.yaml
    echo "switch to deploy mode"
else
    echo "Input error. Please enter dev (Next.js in development mode) or dep (Next.js production deploy mode)."
fi

### Change IP/Port ###
sed -i "s/PERMISSION_SERVICE=.*/PERMISSION_SERVICE=\'http:\/\/$ip\'/g" $baseDir/.env
## sed -i "s/PERMISSION_SERVICE_PORT=.*/PERMISSION_SERVICE_PORT=\'$PERMISSION_SERVICE_PORT\'/g" $baseDir/.env

sed -i "s/SUBSERVICE_K_HOST=.*/SUBSERVICE_K_HOST=\'https:\/\/$ip\'/g" $baseDir/.env
## sed -i "s/SUBSERVICE_K_PORT=.*/SUBSERVICE_K_PORT=\'$SUBSERVICE_K_PORT\'/g" $baseDir/.env

sed -i "s/SUBSERVICE_SYN_HOST=.*/SUBSERVICE_SYN_HOST=\'http:\/\/$ip\'/g" $baseDir/.env
## sed -i "s/SUBSERVICE_SYN_PORT=.*/SUBSERVICE_SYN_PORT=\'$SUBSERVICE_SYN_PORT\'/g" $baseDir/.env

sed -i "s/SUBSERVICE_DP_HOST=.*/SUBSERVICE_DP_HOST=\'http:\/\/$ip\'/g" $baseDir/.env
## sed -i "s/SUBSERVICE_DP_PORT=.*/SUBSERVICE_DP_PORT=\'$SUBSERVICE_DP_PORT\'/g" $baseDir/.env