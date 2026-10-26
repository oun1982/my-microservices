# CI/publishing proposal only

No .github files changed. Docker is available here, so fallback workflow creation
is unnecessary and would exceed kamailio/ scope. Future reviewed CI should run:

1. checkout immutable revision; build Debian digest + pinned Kamailio packages;
2. generate disposable test CA, never upload its keys;
3. validate compose and config, inventory shared libraries;
4. run UDP/TCP/TLS/WSS, ACL/malformed, mock routing and recreation tests;
5. archive sanitized test results and exact packages/image digest, teardown
   owned disposable containers without pruning volumes/images;
6. separate approval-gated registry publication job using scoped GitHub token;
7. do not add AWS secrets/deploy jobs until infrastructure review.

A successful signaling test is not a WebRTC audio acceptance test. Media CI needs
real SDP negotiation, both-side RTP packet capture and decoded audio validation.
