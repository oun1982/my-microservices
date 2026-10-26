#!/usr/bin/env python3
"""Record a real command's exit code/output without hiding failure."""
import datetime
import json
import subprocess
import sys
from pathlib import Path
name, expected, *command = sys.argv[1:]
result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
path = Path(__file__).resolve().parents[1] / 'docs' / 'test-results.json'
records = json.loads(path.read_text()) if path.exists() else []
records.append(dict(name=name, command=command, expected=expected,
                    actual=result.stdout, exit_code=result.returncode,
                    status='PASS' if result.returncode == 0 else 'FAIL',
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()))
path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
print(result.stdout, end='')
sys.exit(result.returncode)
