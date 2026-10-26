"""Read-only Docker metadata assertions on this disposable lab."""
import json
import subprocess

name = 'kamailio-sbc-lab-kamailio-1'
container = json.loads(subprocess.check_output(['docker', 'inspect', name]))[0]
ports = container['NetworkSettings']['Ports']
expected = {'5060/udp', '5060/tcp', '5061/tcp', '8443/tcp'}
assert set(ports) == expected, ports
for bindings in ports.values():
    assert bindings and all(b['HostIp'] == '127.0.0.1' for b in bindings), ports
assert len(container['NetworkSettings']['Networks']) == 2
assert container['Config']['User'] == 'kamailio'
assert container['HostConfig']['Privileged'] is False
assert container['HostConfig']['ReadonlyRootfs'] is True
assert 'ALL' in container['HostConfig']['CapDrop']
network = json.loads(subprocess.check_output(['docker', 'network', 'inspect', 'kamailio-sbc-lab_internal']))[0]
assert network['Internal'] is True
assert set(network['Containers']) == {
    container['Id'],
    json.loads(subprocess.check_output(['docker', 'inspect', 'kamailio-sbc-lab-mock-freeswitch-1']))[0]['Id'],
}
print('PASS loopback-only host ports, no internal 5080 publish, two networks, internal membership, nonroot/capabilities/read-only')
print('process_state=', container['State']['Status'])
print('health=', container['State'].get('Health', {}).get('Status'))
assert container['State']['Running']
assert container['State']['Health']['Status'] == 'healthy'
