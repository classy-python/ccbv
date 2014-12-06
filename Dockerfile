FROM python:2-wheezy
MAINTAINER Felipe Arruda Pontes <contato@arruda.blog.br>

# install project deps
RUN apt-get update
RUN apt-get -y -q install libmemcached-dev

ADD . /data
# install requirements
RUN pip install -r /data/requirements.txt

ADD docker_scripts /scripts
RUN chmod +x /scripts/start.sh

EXPOSE 8000
# using steps vol, to save/check if the container
# is running for the first time or not.
# using the /data volume would polute the project files
VOLUME ["/data", "/steps"]

# Set the default command to run when starting the container
CMD ["/scripts/start.sh"]