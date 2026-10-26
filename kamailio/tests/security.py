"""Negative TLS/Origin checks and explicit TLS version negotiation."""
import socket
import ssl

HOST = 'sbc-external'
CA = '/run/lab-tls/ca.crt'
for version in (ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_3):
    ctx = ssl.create_default_context(cafile=CA)
    ctx.minimum_version = ctx.maximum_version = version
    with ctx.wrap_socket(socket.create_connection((HOST, 5061), timeout=3), server_hostname=HOST) as sock:
        print('PASS negotiated', sock.version(), flush=True)
for label, ctx, hostname in (
    ('wrong hostname', ssl.create_default_context(cafile=CA), 'wrong.invalid'),
    ('untrusted CA', ssl.create_default_context(), HOST),
):
    try:
        with ctx.wrap_socket(socket.create_connection((HOST, 5061), timeout=3), server_hostname=hostname):
            raise AssertionError('unexpected certificate acceptance')
    except ssl.SSLCertVerificationError:
        print('PASS certificate rejection:', label, flush=True)
ctx = ssl.create_default_context(cafile=CA)
with ctx.wrap_socket(socket.create_connection((HOST, 8443), timeout=3), server_hostname=HOST) as sock:
    sock.sendall(b'GET /sip HTTP/1.1\r\nHost: sbc-external\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\nSec-WebSocket-Protocol: sip\r\nOrigin: https://unauthorized.invalid\r\n\r\n')
    data = sock.recv(4096)
    assert data.startswith(b'HTTP/1.1 403 '), data
    print('PASS unauthorized WebSocket Origin rejected', flush=True)
try:
    socket.gethostbyname('mock-freeswitch')
except socket.gaierror:
    print('PASS external-only tester cannot resolve internal backend', flush=True)
else:
    raise AssertionError('backend unexpectedly visible through external network DNS')
