import glob
import subprocess

required = 'sl tm rr maxfwd sanity pv textops siputils xlog tls xhttp websocket nathelper path dispatcher permissions pike htable dialog acc rtpengine'.split()
for name in required:
    paths = glob.glob('/usr/lib/*/kamailio/modules/' + name + '.so')
    assert len(paths) == 1, name
    result = subprocess.run(['ldd', paths[0]], capture_output=True, text=True, check=True)
    assert 'not found' not in result.stdout, (name, result.stdout)
    print('PASS shared libraries:', name)
for name in ('outbound', 'db_postgres', 'db_mysql'):
    paths = glob.glob('/usr/lib/*/kamailio/modules/' + name + '.so')
    assert not paths, ('optional module unexpectedly installed', name)
    print('EXPECTED NOT INSTALLED:', name)
