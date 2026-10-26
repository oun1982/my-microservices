# Official sources / resolved versions

Checked 2026-10-26, linux/amd64. Debian package index was consulted BEFORE
selecting installation. APT retains signature verification; no insecure TLS,
trusted=yes, checksum bypass or third-party binary install is used.

- Debian Bookworm index: https://deb.debian.org/debian/dists/bookworm/main/binary-amd64/Packages.xz
- Kamailio upstream module docs pinned to 5.6 branch:
  https://github.com/kamailio/kamailio/tree/5.6/src/modules
  (tm, rr, dispatcher, sanity, permissions, tls, websocket, rtpengine README
  files retrieved from official repository during inspection).
- Debian Docker official image: https://hub.docker.com/_/debian
- RTPengine official mr10.5.3.5 docs and license:
  https://github.com/sipwise/rtpengine/tree/mr10.5.3.5
  README confirms userspace fallback, optional kernel acceleration, and optional
  build-time transcoding. LICENSE is GPLv3; linked components have own terms.
- Docker networking: https://docs.docker.com/engine/network/drivers/
- Docker Compose services: https://docs.docker.com/reference/compose-file/services/
- AWS ENI design reference: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html
- GitHub delivery design: https://docs.github.com/en/actions/publishing-packages/publishing-docker-images

The last four links are design references, not evidence of infrastructure tests.

| Package | Bookworm index version | Decision |
|---|---|---|
| kamailio | 5.6.3-2 | installed, pinned |
| kamailio-tls-modules | 5.6.3-2 | installed, exact Kamailio dependency |
| kamailio-websocket-modules | 5.6.3-2 | installed, exact Kamailio dependency |
| kamailio-postgres-modules | 5.6.3-2 | verified available, not installed |
| rtpengine-daemon | 10.5.3.5-1 | standalone userspace image, pinned |

Base digest resolved from actual Docker pull:
`debian:12-slim@sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8`.
Both Dockerfiles pin this digest. This is the observed registry manifest digest;
other CPU architectures are untested. Exact APT resolutions are recorded in
packages-amd64.lock (Kamailio) and rtpengine-packages-amd64.lock. Transitive APT
packages are recorded but not all pinned: Debian repositories evolve, so this
is not a fully reproducible snapshot build. Use a reviewed Debian snapshot and
verified Release metadata for stricter reproducibility; never freeze security
updates indefinitely without a maintenance policy.

Kamailio main package SHA256 in index:
`1fb43079b3d7e5f575e3ca7b3252239bb4df335a410464fdd39a9d1dfdf28a33`.
TLS module package depends on libssl3/libcurl4; websocket on libssl3/libunistring2.
RTPengine depends on FFmpeg libraries, libbcg729, OpenSSL and others; actual
resolved package list records them. Dependency presence alone does not certify
codec transcoding or interoperability. No assumption all module packages exist:
module-evidence.txt and optional-modules.txt record actual ownership of requested modules and missing
DB drivers. Main-package modules are not separate apt package names.

Bookworm's Kamailio 5.6 is not claimed latest or production-supported upstream.
Before production, review Debian security tracker and upstream support/CVEs,
then test a supported upgrade path rather than automatically changing repos.
