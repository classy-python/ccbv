FROM ubuntu:14.04
MAINTAINER Felipe Arruda Pontes <contato@arruda.blog.br>

# Ensure we create the cluster with UTF-8 locale
RUN locale-gen en_US.UTF-8 && \
    echo 'LANG="en_US.UTF-8"' > /etc/default/locale

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y -q install python-software-properties software-properties-common

RUN apt-get update
RUN apt-get -y -q install python-pip

# install project deps
RUN apt-get -y -q install python-dev libmemcached-dev zlib1g-dev libpq-dev

ADD docker_scripts /scripts
RUN chmod +x /scripts/start.sh

EXPOSE 8000
# using steps vol, to save check if the container
# is running for the first time or not.
# using the /data volume would polute the project files
VOLUME ["/data", "/steps"]

# Set the default command to run when starting the container
CMD ["/scripts/start.sh"]