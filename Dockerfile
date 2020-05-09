FROM python:3.6.5
MAINTAINER Dexter Wang

ADD ./ /code
WORKDIR /code
RUN pip install -r requirements.txt
EXPOSE 5003
ENTRYPOINT ["sh", "docker_entrypoint.sh"]
