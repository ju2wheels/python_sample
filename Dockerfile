FROM       centos:centos7
MAINTAINER Julio Lajara <julio.lajara@alum.rpi.edu>

VOLUME ["/data"]

EXPOSE 443
EXPOSE 8080

COPY ./docker/overlay/etc           /etc
COPY ./docker/overlay/usr/bin/start /usr/bin/start
COPY ./ /usr/src/sha_api

# Dont trust user umask
RUN chmod 644 /etc/nginx/server.crt   \
              /etc/nginx/server.key   \
              /etc/nginx/nginx.conf   \
              /etc/supervisord.d/*    \
              /etc/yum.repos.d/*   && \
    chmod 755 /etc                    \
              /etc/nginx              \
              /etc/supervisord.d      \
              /etc/yum.repos.d        \
              /usr/bin/start
RUN yum install --enablerepo=epel-bootstrap,ius-bootstrap -q -y epel-release ius-release
RUN yum install -y nginx             \
                   python-nose       \
                   python-pip        \
                   python-setuptools \
                   supervisor
RUN cd /usr/src/sha_api     && \
    python setup.py install

ENTRYPOINT ["/usr/bin/start"]
CMD        []
