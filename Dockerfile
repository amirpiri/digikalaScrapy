FROM ubuntu:latest
MAINTAINER Amir H Piri "ahpiri@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential python3-pip vim screen
ADD . /flask-app
WORKDIR /flask-app
RUN python3 -m pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["flask-docker.py"]
