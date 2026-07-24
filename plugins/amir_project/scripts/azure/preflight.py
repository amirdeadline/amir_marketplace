#!/usr/bin/env python3
import json, shutil, subprocess, sys
if not shutil.which("az"):
    print("PARTIALLY DOABLE — az not on PATH. https://learn.microsoft.com/cli/azure/install-azure-cli")
    sys.exit(2)
r = subprocess.run(["az", "account", "show", "-o", "json"], capture_output=True, text=True)
if r.returncode != 0:
    print("REFUSING — unauthenticated. Run: az login"); print(r.stderr[:500]); sys.exit(2)
print(r.stdout)
