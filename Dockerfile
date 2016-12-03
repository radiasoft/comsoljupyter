FROM jupyterhub/jupyterhub:latest
MAINTAINER Pepe Barbe <pepe@radiasoft.net>

RUN apt-get update && \
    apt-get install -y build-essential libffi-dev nginx-full libssl-dev 
   
ADD requirements.txt /src/requirements.txt
# One of the dependencies in comsoljupyter requires pyasn1 and pyasn1-modules.
# Using the automatic installation procedure when it tries to install pyasn1
# it requests pyasn1-modules somehow and the installation crashes.
# By installing manually we work around the issue. 
RUN pip install jupyter && \
    pip install pyasn1 && \
    pip install -r /src/requirements.txt
 
ADD . /src/comsoljupyter/
RUN cd /src/comsoljupyter && pip install . && \
    /src/comsoljupyter/integration-test/add_credentials.sh && \
    cp /src/comsoljupyter/integration-test/jupyterhub/jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py 

RUN useradd -m jupyterhub && echo 'jupyterhub:jupyterhub' | chpasswd && \
    echo nameserver 8.8.8.8 > /etc/resolv.conf && \
    rm -rf /var/lib/apt/lists/* && rm -rf /root/.cache && rm -rf /src

CMD echo 'nameserver 8.8.8.8\nnameserver 8.8.4.4' > /etc/resolv.conf && exec jupyterhub
