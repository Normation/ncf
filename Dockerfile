FROM ubuntu:20.04

RUN apt-get update && apt-get install -y wget
RUN wget https://repository.rudder.io/tools/rudder-setup && sh ./rudder-setup install-agent
