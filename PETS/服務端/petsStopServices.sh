!#!/bin/bash

docker stack rm PETSHadoop
docker stack rm PETSWebservice
docker stack rm PET_join_Hadoop

docker stack rm pets_dp
docker stack rm pets_service
docker stack rm pets_web
docker stack rm pets_syn

echo "finished, rm service PETSHadoop, PETSWebservice, PET_join_Hadoop, pets_service, pets_syn, pets_web and pets_dp "