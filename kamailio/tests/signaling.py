"""Real SIP signaling tests; standard library only, no audio claims."""
import base64
import hashlib
import json
import os
import socket
import ssl
import struct
import sys
import uuid

HOST = 'sbc-external'


def message(method='OPTIONS', domain=HOST, hops=10):
    callid = uuid.uuid4().hex
    request = (f'{method} sip:probe@{domain} SIP/2.0\r\n'
               'Via: SIP/2.0/UDP sip-tester:5099;branch=z9hG4bK' + callid + ';rport\r\n'
               f'Max-Forwards: {hops}\r\n'
               'From: <sip:probe@lab.invalid>;tag=test\r\n'
               f'To: <sip:probe@{domain}>\r\n'
               f'Call-ID: {callid}\r\nCSeq: 1 {method}\r\n'
               'Content-Length: 0\r\n\r\n').encode()
    return request, callid


def context():
    ctx = ssl.create_default_context(cafile='/run/lab-tls/ca.crt')
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    return ctx


def receive(sock):
    data = b''
    while b'\r\n\r\n' not in data:
        chunk = sock.recv(65535)
        if not chunk:
            raise RuntimeError('connection closed')
        data += chunk
    return data


def check(transport, method, domain, expected, hops=10):
    request, callid = message(method, domain, hops)
    if transport == 'udp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(4)
        sock.connect((HOST, 5060))
    else:
        port = 5061 if transport == 'tls' else 5060
        sock = socket.create_connection((HOST, port), timeout=4)
        if transport == 'tls':
            sock = context().wrap_socket(sock, server_hostname=HOST)
        # Reliable transports need no UDP Via assumptions.
        request = request.replace(b'SIP/2.0/UDP', b'SIP/2.0/TCP' if transport == 'tcp' else b'SIP/2.0/TLS')
    with sock:
        sock.sendall(request)
        data = sock.recv(65535) if transport == 'udp' else receive(sock)
        # Transactions can send provisional replies before final responses.
        while data.startswith(b'SIP/2.0 100 '):
            if b'SIP/2.0 ' in data[12:]:
                data = data[data.index(b'SIP/2.0 ', 12):]
            else:
                data = sock.recv(65535) if transport == 'udp' else receive(sock)
        assert data.startswith(f'SIP/2.0 {expected} '.encode()), data
        assert callid.encode() in data, data
        if method == 'INVITE' and expected == 486:
            assert b'Record-Route:' in data, data
    print(f'PASS {transport} {method} {domain} hops={hops} -> {expected}', flush=True)


def websocket():
    with context().wrap_socket(socket.create_connection((HOST, 8443), timeout=4), server_hostname=HOST) as sock:
        key = base64.b64encode(os.urandom(16)).decode()
        sock.sendall((f'GET /sip HTTP/1.1\r\nHost: {HOST}:8443\r\n'
                      'Upgrade: websocket\r\nConnection: Upgrade\r\n'
                      f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n'
                      'Sec-WebSocket-Protocol: sip\r\nOrigin: https://lab.invalid\r\n\r\n').encode())
        response = receive(sock)
        assert response.startswith(b'HTTP/1.1 101 '), response
        accept = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
        assert accept in response, response
        data, callid = message()
        data = data.replace(b'SIP/2.0/UDP', b'SIP/2.0/WSS')
        mask = os.urandom(4)
        header = bytes([0x81, 0x80 | 126]) + struct.pack('!H', len(data))
        sock.sendall(header + mask + bytes(v ^ mask[i % 4] for i, v in enumerate(data)))
        def exact(n):
            result = b''
            while len(result) < n:
                part = sock.recv(n - len(result))
                if not part:
                    raise RuntimeError('websocket closed')
                result += part
            return result
        first, second = exact(2)
        assert first & 15 == 1, (first, second)
        length = second & 127
        if length == 126:
            length = struct.unpack('!H', exact(2))[0]
        elif length == 127:
            length = struct.unpack('!Q', exact(8))[0]
        payload = exact(length)
        assert payload.startswith(b'SIP/2.0 200 '), payload
        assert callid.encode() in payload, payload
    print('PASS verified WSS handshake + framed SIP OPTIONS 200', flush=True)


def malformed():
    # Valid SIP framing but missing mandatory To header: sanity must drop it.
    raw, _ = message()
    raw = b'\r\n'.join(line for line in raw.split(b'\r\n') if not line.startswith(b'To:'))
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(1)
        sock.sendto(raw, (HOST, 5060))
        try:
            response = sock.recv(65535)
        except socket.timeout:
            print('PASS malformed SIP missing To silently rejected', flush=True)
        else:
            raise AssertionError(response)


if __name__ == '__main__':
    if '--untrusted' in sys.argv:
        check('udp', 'INVITE', 'lab.invalid', 403)
    else:
        for transport in ('udp', 'tcp'):
            check(transport, 'OPTIONS', HOST, 200)
            check(transport, 'OPTIONS', 'lab.invalid', 200)
            check(transport, 'INVITE', 'lab.invalid', 486)
        check('udp', 'REGISTER', HOST, 403)
        check('udp', 'INVITE', 'outside.invalid', 403)
        check('udp', 'OPTIONS', HOST, 483, hops=0)
        malformed()
        if '--tls' in sys.argv:
            check('tls', 'OPTIONS', HOST, 200)
            websocket()
