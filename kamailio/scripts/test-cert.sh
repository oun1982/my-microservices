#!/bin/sh
# Disposable LAB CA and server certificate. Never a production identity.
set -eu
cd "$(dirname "$0")/.."
[ ! -e .runtime/tls ] || { echo 'Refusing to overwrite existing TLS files' >&2; exit 1; }
mkdir -p .runtime/tls
chmod 755 .runtime .runtime/tls
openssl req -x509 -newkey rsa:2048 -nodes -days 2 -subj /CN=Disposable-Lab-CA \
  -keyout .runtime/tls/ca.key -out .runtime/tls/ca.crt
openssl req -newkey rsa:2048 -nodes -subj /CN=sbc-external \
  -keyout .runtime/tls/server.key -out .runtime/tls/server.csr
printf 'subjectAltName=DNS:sbc-external\nextendedKeyUsage=serverAuth\n' > .runtime/tls/extensions
openssl x509 -req -in .runtime/tls/server.csr -CA .runtime/tls/ca.crt \
  -CAkey .runtime/tls/ca.key -CAcreateserial -days 2 \
  -extfile .runtime/tls/extensions -out .runtime/tls/server.crt
# Container uid is resolved from the built image, never guessed.
lab_uid=$(docker run --rm --entrypoint id kamailio-sbc-lab:dev -u)
lab_gid=$(docker run --rm --entrypoint id kamailio-sbc-lab:dev -g)
docker run --rm --user 0 --entrypoint sh -v "$PWD/.runtime/tls:/tls" \
  kamailio-sbc-lab:dev -c "chown $lab_uid:$lab_gid /tls/server.key && chmod 640 /tls/server.key"
chmod 600 .runtime/tls/ca.key
chmod 644 .runtime/tls/server.crt .runtime/tls/ca.crt
