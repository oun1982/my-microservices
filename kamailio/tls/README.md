# TLS material

Never commit private keys or production certificates. `scripts/test-cert.sh`
creates a disposable two-day CA and SAN server certificate in ignored
`.runtime/tls/`; never overwrites existing TLS material. Requires host openssl.
Server key is assigned to the built container runtime UID/GID with restricted
permissions. CA key stays host-only 600; container mount is read-only. Test
client mounts only public CA. No production identity or browser login is implied.

Production private keys/full chains must come from external secure storage.
Do not use these lab keys or lab.invalid as production endpoints.
