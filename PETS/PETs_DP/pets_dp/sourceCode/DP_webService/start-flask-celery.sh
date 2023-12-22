#!/bin/bash
echo "rm containers redis..."
docker rm -f redis flask celery deidweb

#
echo "start redis..."
docker run -d -ti --name redis -v redis-data:/data -v /etc/localtime:/etc/localtime:ro -p 6380:6379 -p 3220:22 --network hadoopnet --ip 172.26.1.2 redis:4.0.1-alpine02 redis-server --requirepass 'citcw200'
#docker exec -it redis /bin/ash -c "/usr/sbin/sshd -D &"
docker exec  redis /usr/sbin/sshd -D &
#/usr/sbin/sshd","-D

#2. 啟動flask
echo "start flask..."
docker run -d -ti --name flask -e REDIS_HOST=redis -e REDIS_PORT=6379 -e REDIS_PWD=citcw200 \
       -v $(pwd)/APP__:/app/app/devp \
       -v /etc/localtime:/etc/localtime:ro  \
       --network hadoopnet -p 5088:5088 -p 3221:22 --ip 172.26.1.3 --hostname flask.bdp.com flask-redis_citc:04 \
       /bin/bash -c "python app.py /app/sqljdbc4-2.0.jar > /app/app/devp/log/flask_log.txt"
sleep 5

echo "start flask sshd..."
docker exec -it flask /bin/bash -c "service ssh stop" 
docker exec -it flask /bin/bash -c "service ssh start" 
#sleep 5       

#3. 啟動celery
#echo "start celery..."
#docker run -d -ti --name celery -v $(pwd)/APP__:/app/app/devp  \
#      -e REDIS_HOST=redis -e REDIS_PORT=6379 -e REDIS_PWD=citcw200 --network hadoopnet \
#      --ip 172.28.1.4 -p 3322:22 --hostname celery.bdp.com celery-redis_citc:05.1 \
#      /bin/bash -c "celery -A app.celery worker --loglevel=info -f /app/app/devp/log/celery_log.txt"

#sleep 5
#echo "start celery sshd..."
#docker exec -it celery /bin/bash -c "service ssh stop" 
#docker exec -it celery /bin/bash -c "service ssh start" 
#sleep 5    

 #.啟動deID WEB  
#echo "start deidweb ..."   
#docker run --name deidweb --network hadoopnet --ip 172.28.1.10 --link mysql --link flask -p 11000:11000 -p 9922:22 -d deidwebssd:1.9
#docker run -d -ti --name deidweb --network hadoopnet --ip 172.28.1.10 -p 11000:11000 deidwebssd:1.2.5
#sleep 5
#docker exec deidweb /bin/bash -c "sed -ri ‘s/172.18.0/172.28.1/g’ /app/appsettings.json"
#sleep 5
#docker exec deidweb sed -ri 's/172.18.0/172.28.1/g' /app/appsettings.json
#docker exec  deidweb /usr/sbin/sshd -D &
