# Changed files

Initial implementation inventory: 35 new files under kamailio/.
This list records the scope before source-control preservation; the preservation
commit stages these files on feature/kamailio-sbc-lab, without changing main.
No push, PR creation, image publication or deployment is part of that commit. Ignored .runtime/ holds disposable lab
TLS keys and package inspection artifacts, and must not be committed.

```text
kamailio/.dockerignore
kamailio/.env.example
kamailio/.gitignore
kamailio/Dockerfile
kamailio/README.md
kamailio/compose.prod.yaml
kamailio/compose.tls.yaml
kamailio/compose.yaml
kamailio/config/kamailio.cfg
kamailio/config/tls.cfg
kamailio/database/README.md
kamailio/docs/architecture.md
kamailio/docs/ci-plan.md
kamailio/docs/file-manifest.md
kamailio/docs/module-evidence.txt
kamailio/docs/operations.md
kamailio/docs/optional-modules.txt
kamailio/docs/packages-amd64.lock
kamailio/docs/rtpengine-packages-amd64.lock
kamailio/docs/sources.md
kamailio/docs/test-report.md
kamailio/docs/test-results.json
kamailio/rtpengine/Dockerfile
kamailio/rtpengine/README.md
kamailio/rtpengine/compose.yaml
kamailio/scripts/record.py
kamailio/scripts/start.py
kamailio/scripts/test-cert.sh
kamailio/tests/exposure.py
kamailio/tests/health.py
kamailio/tests/mock_backend.py
kamailio/tests/modules.py
kamailio/tests/security.py
kamailio/tests/signaling.py
kamailio/tls/README.md
```
