FROM ubuntu:20.04

RUN curl -O rudder-setup https://repository.rudder.io/tools/rudder-setup
RUN sh ./rudder-setup install-agent
