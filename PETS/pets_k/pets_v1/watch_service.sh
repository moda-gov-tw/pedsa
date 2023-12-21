docker_id="$(docker ps | grep 'celery-redis_citc:06.2_ch_term' | awk '{print $1}')"
echo "HELLO DOCKER $docker_id"
docker exec -i "$docker_id" bash -c "python app/devp/watchFolder.py"
