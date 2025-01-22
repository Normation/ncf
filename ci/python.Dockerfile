FROM debian:11
LABEL ci=ncf/ci/python.Dockerfile

RUN apt-get update && apt-get install -y git wget gnupg2 make python3-pip ;\
    pip3 install avocado-framework pylint Jinja2

# Accept all OSes
ENV UNSUPPORTED=y
RUN wget https://repository.rudder.io/tools/rudder-setup && sed -i "s/set -e/set -xe/" rudder-setup && sed -i "s/rudder agent inventory//" rudder-setup && sed -i "s/rudder agent health/rudder agent health || true/" rudder-setup && sh ./rudder-setup setup-agent latest
