FROM python:3.9

RUN apt update && apt install -y vim dnsutils curl sshpass iputils-ping mariadb-client
# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ENV TZ="Asia/Taipei"
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"
ENV PORT=8000

RUN pip install --upgrade pip

COPY ./requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

COPY ./ /usr/src/app

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8800", "--proxy-headers", "--forwarded-allow-ips", "*"]
