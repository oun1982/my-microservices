# RTPengine standalone userspace control lab

Independent Debian 12 image with pinned rtpengine-daemon=10.5.3.5-1. No kernel
module installed, --table=-1, unprivileged nobody, cap_drop ALL, no host network
modifications. Compose uses network_mode none. Loopback 127.0.0.1 is intentional
for isolated control testing only, NOT a public media advertisement address.

From this directory:

```sh
DOCKER_BUILDKIT=0 docker build -t rtpengine-sbc-lab:dev .
docker compose config --quiet
docker compose up -d --no-build
docker compose logs
docker compose down
```

Actual NG ping test joins only this disposable container's network namespace
using a separate Python client image. See docs/test-results.json for exact
command and pong evidence. This does not test SIP module integration or RTP.

Next implementation gate: supply actual external/internal media IP mappings,
put NG on a private network reachable only by Kamailio, load verified Kamailio
rtpengine module, implement offer/answer/delete with direction-specific flags,
then test SDP rewrite, both media legs, ICE candidates, DTLS fingerprint/profile,
SRTP decryption/packet flow and audio with real WebRTC + FreeSWITCH endpoints.
Use disposable synthetic media, protect packet captures, record codecs and
actual build features before claiming transcoding. No host kernel changes needed
for the initial userspace path. Production capacity/performance still untested.
