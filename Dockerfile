FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && \
    apt-get install -y python3.8 && \
    ln -s /usr/bin/python3.8 /usr/bin/python3 && \
    apt install -y python3-pip 

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY . /app
WORKDIR /app

RUN rasa train nlu

RUN python3 script.py

RUN apt-get update


RUN apt install -y maven

RUN mvn dependency:copy-dependencies -DoutputDirectory=./jars -f $(python3 -c 'import importlib.util; import pathlib; print(pathlib.Path(importlib.util.find_spec("sutime").origin).parent / "pom.xml")')



EXPOSE 5000
CMD python3 app.py
