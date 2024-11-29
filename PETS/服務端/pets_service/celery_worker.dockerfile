FROM python:3.9

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update -y \
&& apt-get -y install sshpass

ENV TZ="Asia/Taipei"
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"
#COPY ["requirements.txt", "/usr/src/app/"]
COPY ./ /usr/src/app
RUN pip install $(cat requirements.txt | grep -E "celery|redis|paramiko|marshmallow")
#COPY ["celery_worker.py", "/usr/src/app/"]
#RUN pip install -r requirements.txt

CMD ["celery", "-A", "celery_worker.celery", "worker", "--loglevel=info"]
