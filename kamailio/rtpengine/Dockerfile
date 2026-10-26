FROM debian:12-slim@sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8
ARG RTPENGINE_VERSION=10.5.3.5-1
RUN apt-get update && apt-get install -y --no-install-recommends \
    rtpengine-daemon=${RTPENGINE_VERSION} \
    && rm -rf /var/lib/apt/lists/* \
    && dpkg-query -W > /packages.lock
WORKDIR /tmp
USER nobody
# Userspace only: no kernel module, no iptables manipulation, no published ports.
ENTRYPOINT ["rtpengine", "--foreground", "--log-stderr", "--table=-1", "--interface=127.0.0.1", "--listen-ng=127.0.0.1:2223", "--port-min=30000", "--port-max=30020"]
