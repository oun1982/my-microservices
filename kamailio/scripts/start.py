"""Render non-secret runtime values without modifying mounted configuration."""
import ipaddress
import os
import socket
from pathlib import Path


def resolve(name):
    return str(ipaddress.IPv4Address(socket.gethostbyname(name)))


values = {
    "EXTERNAL_IP": resolve("sbc-external"),
    "INTERNAL_IP": resolve("sbc-internal"),
    "CLIENT_IP": resolve(os.getenv("TRUSTED_CLIENT_HOST", "sip-tester")),
    "BACKEND_IP": resolve(os.getenv("BACKEND_HOST", "mock-freeswitch")),
}
text = Path('/opt/lab/config/kamailio.cfg').read_text()
for name, value in values.items():
    text = text.replace('@' + name + '@', value)
if os.getenv('TLS_ENABLED', '0') == '1':
    text = '#!define WITH_TLS\n' + text
Path('/tmp/kamailio.cfg').write_text(text)
Path('/tmp/dispatcher.list').write_text(f"1 sip:{values['BACKEND_IP']}:5080 0 0\n")
os.execvp('kamailio', ['kamailio', '-DD', '-E', '-f', '/tmp/kamailio.cfg'])
