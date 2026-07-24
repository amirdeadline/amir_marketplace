#!/usr/bin/env python3
import shutil, subprocess, sys
if not shutil.which("az"):
    print("az missing — install Azure CLI"); sys.exit(2)
r=subprocess.run(["az","account","show","-o","json"], capture_output=True, text=True)
if r.returncode!=0:
    print("REFUSING — az login required"); sys.exit(2)
print(r.stdout)
