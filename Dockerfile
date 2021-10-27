FROM ubuntu:20.04
ENV UNSUPPORTED=y
RUN apt-get update && apt-get install -y wget gnupg2 make
RUN wget https://repository.rudder.io/tools/rudder-setup && sh ./rudder-setup setup-agent latest || true
