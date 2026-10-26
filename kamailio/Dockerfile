FROM debian:12-slim@sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8
ARG KAMAILIO_VERSION=5.6.3-2
RUN apt-get update && apt-get install -y --no-install-recommends \
    kamailio=${KAMAILIO_VERSION} kamailio-tls-modules=${KAMAILIO_VERSION} \
    kamailio-websocket-modules=${KAMAILIO_VERSION} ca-certificates openssl netbase \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/lab
COPY config/ /opt/lab/config/
COPY scripts/ /opt/lab/scripts/
COPY tests/ /opt/lab/tests/
RUN chmod -R a+rX /opt/lab && kamailio -V \
    && dpkg-query -W > /opt/lab/packages.lock
USER kamailio
ENTRYPOINT ["python3", "/opt/lab/scripts/start.py"]
