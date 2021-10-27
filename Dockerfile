FROM ubuntu:20.04

RUN wget https://repository.rudder.io/tools/rudder-setup
RUN sh ./rudder-setup install-agent
