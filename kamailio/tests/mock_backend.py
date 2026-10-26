"""UDP signaling stub, NOT FreeSWITCH. Never simulates media acceptance."""
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 5080))
print('mock backend ready udp/5080', flush=True)
while True:
    raw, peer = sock.recvfrom(65535)
    lines = raw.decode('utf-8', errors='replace').split('\r\n')
    method = lines[0].split(' ')[0]
    if method == 'ACK':
        continue
    code = '200 OK' if method == 'OPTIONS' else '486 Busy Here'
    headers = [line for line in lines[1:] if line.lower().startswith(
        ('via:', 'from:', 'to:', 'call-id:', 'cseq:', 'record-route:'))]
    headers = [line + ';tag=mock' if line.lower().startswith('to:') and ';tag=' not in line else line for line in headers]
    response = '\r\n'.join(['SIP/2.0 ' + code, *headers, 'Content-Length: 0', '', ''])
    sock.sendto(response.encode(), peer)
    print(f'mock method={method} status={code}', flush=True)
