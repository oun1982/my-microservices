# Test report — 2026-10-26, linux/amd64

Exact commands, expected/actual output, exit codes, and timestamps are in
[test-results.json](test-results.json). Each recorded command preserves its
underlying exit code; PASS means assertions in that specific command passed.
Do not infer production acceptance from syntax checks or an open port.

| # | Acceptance check | Status / scope |
|---|---|---|
| 1 | Debian 12 base | PASS: os-release in built container |
| 2 | Kamailio version | PASS: 5.6.3 upstream, Debian 5.6.3-2 |
| 3 | Modules + shared libs | PASS: actual .so ownership inventory and ldd checks |
| 4 | Docker build | PASS: legacy builder; base digest, pinned primary packages |
| 5 | Kamailio config | PASS: rendered cfg syntax under non-root user |
| 6 | Compose syntax | PASS: development + TLS override; RTPengine compose |
| 7 | Start Kamailio | PASS: container starts, health tested |
| 8 | Process/listeners | PASS: running state, /proc listeners and active transports |
| 9 | SIP UDP OPTIONS | PASS: local 200, relayed mock 200 |
| 10 | SIP TCP OPTIONS | PASS: local 200, relayed mock 200 |
| 11 | SIP TLS | PASS: verified CA/SAN OPTIONS; TLS1.2 and TLS1.3 negotiated; negative CA/name tests |
| 12 | WSS | PASS: verified TLS + HTTP101 + masked SIP OPTIONS -> 200; bad Origin 403 |
| 13 | Malformed/unauthorized | PASS: missing To dropped, untrusted source 403, disallowed domain 403, REGISTER 403, hops 0 -> 483 |
| 14 | Mock backend routing | PASS: UDP/TCP ingress -> UDP mock; INVITE 486 and Record-Route; NOT real FreeSWITCH |
| 15 | Logs/exit codes | PASS: captured logs, runtime states and command exits; no production behavior claim |
| 16 | Config persistence | PASS: mounted config SHA256 unchanged and signaling passed after owned container recreation |
| 17 | Database connectivity | NOT TESTED: database not enabled because baseline does not require persistence |
| 18 | RTPengine integration | NOT TESTED: separate image/control NG ping PASS, Kamailio SDP/media integration absent |
| 19 | Network isolation | PASS: loopback-only ports, private backend network, tester cannot resolve backend; not hostile-host isolation |
| 20 | Production scenarios | NOT TESTED: gaps in architecture/operations documents |

TLS/WSS tests use a generated two-day test CA, not production certificates.
Mock final INVITE rejection deliberately prevents any claim of a successful call.
No real media packets, audio, ICE, NAT traversal, DTLS-SRTP, actual SIP trunk,
real FreeSWITCH, DB, multi-node failover or EC2 deployment were tested.

## Failures investigated and fixed before final validation

- Debian slim TCP protocol lookup failed: verified missing netbase, installed
  netbase through signed APT, rebuilt and TCP tests passed.
- TM binding order warning: moved tm before sl; rebuilt and startup rechecked.
- First routed response timed out: made internal sending socket explicit and
  force_rport explicit, then verified mock receipt and returned transaction.
  Both changes remain in the controlled two-leg lab config; do not assume a
  general NAT fix for production.
- Mock failed to echo Record-Route: fixed only the mock to reflect route headers
  and add To tag; INVITE test now verifies response Record-Route explicitly.
- One restart was attempted while Compose recreation was still active; Docker
  rejected restart of a container marked for removal. Let recreation finish,
  then started stack sequentially. No cleanup/prune/reset was used.

No unresolved failure is intentionally hidden. Earlier exploratory failures are
summarized above; machine-readable evidence records the final validation runs.

- Broad module assertion incorrectly included optional outbound as installed;
  actual inventory showed it absent. Verified the separate official
  kamailio-outbound-modules package and its checksum/file list, kept it deferred,
  corrected required-vs-optional checks and reran successfully. The original
  failed command remains in JSON evidence rather than being erased.

## Deferred prerequisites

BLOCKED for production acceptance: actual FQDN/certificates, provider ACL/auth
ownership, EC2 network/ENI information, real FreeSWITCH/WebRTC endpoints, and
reviewed SIP/SDP/ICE/media routing. No credentials are requested in chat and no
infrastructure changes or publishing are authorized by successful local tests.
