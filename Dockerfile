FROM ubuntu:20.04
COPY . /app
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && \
    apt-get install -y python3.8 && \
    ln -s /usr/bin/python3.8 /usr/bin/python3 && \
    apt install -y python3-pip  && \
    pip3 install -r requirements.txt && \
    pip3 install sutime

RUN apt install -y maven

RUN mvn dependency:copy-dependencies -DoutputDirectory=./jars -f $(python3 -c 'import importlib.util; import pathlib; print(pathlib.Path(importlib.util.find_spec("sutime").origin).parent / "pom.xml")')

WORKDIR /app/data
CMD rasa train nlu 

WORKDIR /app
CMD python3 script.py

EXPOSE 5000
CMD python3 app.py
