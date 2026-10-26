# Operations, storage, security, and deployment plan

## Persistent paths (proposed, not created on host)

| Host path | Contents | Container access |
|---|---|---|
| /opt/voip-stack/kamailio/config | reviewed config and routing lists | read-only |
| /opt/voip-stack/kamailio/tls | chain and restricted private key | read-only |
| /opt/voip-stack/kamailio/data | only if a feature requires it | not currently mounted |
| /opt/voip-stack/kamailio/logs | optional exported logs | stdout preferred; not mounted |
| /opt/voip-stack/rtpengine/config | reviewed interface/media settings | read-only, future |
| /opt/voip-stack/rtpengine/logs | optional exported logs | stdout preferred |
| /opt/voip-stack/database/data | database only if enabled | dedicated volume, future |

Actual lab mounts only config and optional test TLS. Runtime rendered cfg and
dispatcher list are in container /tmp tmpfs, recreated on startup. Package locks
are image files. Resolve runtime id using `docker run --rm --entrypoint id
kamailio-sbc-lab:dev`; do not guess UID/GID across images. Config requires read
and directory traversal; private keys require restricted runtime ownership.
No arbitrary host directories or Docker socket are mounted into services.

Backup config/version manifests and encrypted TLS keys separately before
replacement. Store backups outside the same disk and rehearse recovery. Restore
into a new directory, verify checksums/config syntax/key permissions; start a
separate isolated disposable stack, smoke-test, then approve traffic switch.
Do not replace a running directory or delete old images/volumes as rollback.

Rollback: retain previous immutable image digest plus its matching configuration
and schema compatibility record. Stop new traffic, account for active dialogs,
switch to prior reviewed version and retest. DB downgrade is not automatically
safe: use tested forward-fix or restore into NEW volume after approval.

## Logs and monitoring

stdout/stderr primary; Compose json-file log rotation bounds size. `log_prefix`
plus event=relay provides textual structured fields (not JSON). Config debug=2
is editable in mounted configuration; raise temporarily, review privacy, restart
and restore normal level. Do not enable raw SIP tracing on production by default;
SIP headers/SDP may carry personal data/credentials. Never log Authorization,
passwords, keys, tokens or full message bodies. WSS/TLS failures are in core/module
logs; future auth, dispatcher probing, DB and media events need dedicated tests.

Healthcheck is TCP liveness only, NOT full routing readiness. Run signaling.py
for readiness. Future Prometheus/Grafana: expose via protected management
network; count SIP errors/latency, dialogs, dispatcher state, NG/DB failures,
resources and container restarts. HEP/Homer needs access control, redaction and
retention review. No monitoring stack installed.

## Troubleshooting

1. Capture `docker compose ps -a`, service logs and exit status, without env dumps.
2. Check resolved listen IPs, Docker network membership and bind-mount permissions.
3. Run Kamailio syntax check, module/ldd inventory and package lock comparison.
4. Isolate transport vs routing vs backend vs media. Keep verified facts separate
   from hypotheses. Change the smallest relevant setting and rerun affected test.
5. Permission-denied config: chmod config files 644 and directory 755 (public
   non-secret config only). Private keys: exact runtime UID, mode 640/600.
6. Missing TCP protocol number on slim Debian: install netbase; do not ignore it.
7. TM bind warning: load tm before dependent sl/dispatcher modules.
8. TLS startup/handshake: check certificate dates, SAN, CA chain and runtime read
   permissions. Never disable certificate verification to make tests pass.
9. DNS/IP changed after recreate: restart SBC to rerender ACL/backend addresses.
10. Never prune Docker, reset DB, upgrade packages wholesale or modify host routes
    as an unexplained fix.

## EC2 and delivery plan — no deployment performed

Source-control preservation uses local branch `feature/kamailio-sbc-lab`.
The initial implementation ran on `work`; main is not modified or merged.
A local source-only commit is authorized; push and Draft PR creation await
confirmation. No PR publication or deployment has been performed.
Draft PR should contain architecture, evidence, limitations and this file list.
CI plan in docs/ci-plan.md; no workflow or registry publishing enabled.

After approval: commit to development branch, CI builds/tests, reviewer approves
image, publish uniquely tagged image and record immutable digest, back up EC2
config/state, pull reviewed Git revision + digest, validate compose/config,
maintenance-window traffic switch, acceptance tests, rollback on failures.
Never use mutable latest alone. No AWS keys required for lab. EC2 prerequisites:
confirmed IP/FQDN, certs, ENI/routes, provider allowlists, SG/firewall limited to
required protocols/media ranges, private FreeSWITCH reachability, host Docker
security and storage permissions. No public admin ports. Production compose is
only a guarded standalone design scaffold, NOT a validated deploy override.

## Production security/readiness checklist

- Real bidirectional dialogs/ACK/BYE/CANCEL, timeout and failover tests missing.
- Registration/auth ownership, browser identity/flow binding, anti-fraud dialplan.
- Pike/htable/rate controls, concurrent call quotas and provider ACL/mTLS policy.
- Public/private SIP advertisement and real EC2 symmetric routing/capture tests.
- Real cert renewal and negative validation/cipher policy tests.
- WebRTC SDP, ICE, DTLS-SRTP, RTP packet/audio evidence and codecs.
- Actual FreeSWITCH integration and controlled load/resource tests.
- Reviewed image CVEs/support lifecycle; Bookworm Kamailio is not latest upstream.
- Tested durable DB schemas/backups only when needed; no fake HA claims.
- Protected metrics, log redaction and incident response.
