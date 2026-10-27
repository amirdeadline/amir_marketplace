#!/usr/bin/env bash
# collect_vm_evidence.sh — READ-ONLY snapshot of one GNS3 VM for troubleshooting / deep review.
# Runs ON the VM. Changes nothing. Prints secret NAMES (SET/UNSET) only, never values.
#
# From the workstation (Git Bash), one VM:
#   ssh -i ~/.ssh/sdwan -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
#       root@<nic1> 'bash -s' -- <lab_key> <lab_id> <tsg_id> "<foreign tsgs space separated>" \
#       < $LE/scripts/collect_vm_evidence.sh > evidence-<vm>.txt
# Get the arguments from: python $LE/scripts/lab_facts.py <lab> --json
set -u
LAB_KEY="${1:-?}"; LAB_ID="${2:-?}"; TSG="${3:-?}"; FOREIGN="${4:-}"
SHARED=/opt/gns3/shared/lab
NON_SECRET_KEYS='LAB_ID|LAB_KEY|SCENARIO_ID|TSG_ID|SCM_TSG_ID|TSG_NAME|RESERVATION_USER|RESERVATION_ID|START_TIME|END_TIME|LABAPP_BUILD_MODE|LABAPP_AUTO_DAY0|LABAPP_AUTO_DAY1|LABAPP_RELEASE|LABAPP_REBUILD_IMAGE|LABAPP_APPLY_ID|LAB_ADDRESS|RELEASE_PROFILE|LABAPP_REFRESH_FROM_NFS'
SECRET_NAMES='ADMIN_PASS SCM_CLIENT_ID SCM_CLIENT_SECRET CLOUDGENIX_AUTH_TOKEN CSP_API_KEY USER_PASSWORD'

h() { printf '\n===== %s =====\n' "$*"; }
run() { "$@" 2>&1 || true; }

h "identity  (expected lab=$LAB_KEY id=$LAB_ID tsg=$TSG)"
hostname; uptime; date -u
ip -br addr | grep -vE '^(lo|docker|veth|tap|gns3tap|virbr|br-[0-9a-f]{12})' || true
last -x 2>/dev/null | grep -E 'reboot|shutdown' | head -3

h "routes / policy routing"
echo "10/8 route: $(ip route show 10.0.0.0/8 || true)"; [ -z "$(ip route show 10.0.0.0/8)" ] && echo "!! MISSING 10.0.0.0/8"
ip route show default; ip rule show | head -20
ls /etc/systemd/network/*.d/ 2>/dev/null; grep -rl '10.0.0.0/8' /etc/systemd/network /etc/netplan 2>/dev/null || echo "10/8 not persisted in networkd/netplan (route is lost on any networkd restart)"

h "networkd restarts + unattended upgrades (last 3 days)"
journalctl --no-pager --since '-3d' -u systemd-networkd 2>/dev/null | grep -E 'Started Network|Stopped Network|Starting Network' | tail -8
grep -h -A2 'Start-Date' /var/log/apt/history.log 2>/dev/null | grep -E 'Start-Date|Upgrade' | tail -8 | cut -c1-220
echo "unattended-upgrades: $(systemctl is-enabled unattended-upgrades 2>&1) / apt-daily-upgrade.timer: $(systemctl is-enabled apt-daily-upgrade.timer 2>&1)"

h "shared mount"
findmnt /opt/gns3/shared 2>&1 | tail -1 || echo "!! /opt/gns3/shared NOT mounted"
cat "$SHARED/RELEASE.json" 2>/dev/null | grep -E '"git_short"|"subject"|"published_at"|"repo"'
echo "startup VERSION on bucket: $(cat $SHARED/labs/scripts/startup/VERSION 2>/dev/null)"

h "units"
for u in nic1-route-10 nic1-policy-routing sase-startup sase-labapp sase-pod-bootstrap gns3server gns3-tls-materialize lab-tls-ensure lab-gns3-computes-nic1 gns3-edge-authz oauth2-proxy lab11-oob-policy google-startup-scripts docker; do
  printf '%-26s enabled=%-10s active=%s\n' "$u" "$(systemctl is-enabled $u 2>/dev/null)" "$(systemctl is-active $u 2>/dev/null)"
done
echo "launcher: $(ls -la /usr/local/sbin/sase-startup-launch.sh 2>&1)"
systemctl cat sase-startup 2>/dev/null | grep -E '^ExecStart' || true
systemctl --failed --no-pager --no-legend 2>/dev/null | head -10

h "boot orchestrator (sase-startup)"
cat /var/lib/sase-startup/last_run.json 2>/dev/null | head -40
cat /var/lib/sase-startup/last_applied.json 2>/dev/null | head -20
tail -25 /var/log/sase-startup/startup.log 2>/dev/null
journalctl -b --no-pager -u sase-startup 2>/dev/null | grep -E 'ERROR|WARN|rc=|DONE|exit' | tail -10

h "GCE metadata startup-script (CRLF breaks it)"
S=$(curl -s -m 5 -H 'Metadata-Flavor: Google' http://169.254.169.254/computeMetadata/v1/instance/attributes/startup-script)
echo "bytes=${#S} CR-lines=$(printf '%s' "$S" | grep -c $'\r')"
journalctl -b --no-pager -u google-startup-scripts 2>/dev/null | grep 'startup-script' | grep -v 'GCSFuse Config' \
  | grep -iE 'exit status|error|command not found|\\r' | tail -6
for f in $SHARED/labs/scripts/startup/*.sh $SHARED/labs/lab_automation/terraform/gcp-eve-ng-test-instance-feature-gns3-greenfield-merge/scripts/*.sh; do
  [ -f "$f" ] && grep -q $'\r' "$f" && echo "!! CRLF in $f"
done

h "booking env (non-secret keys) + secret names"
for f in /etc/labapp/labapp.env /run/labapp/labapp.env; do
  [ -f "$f" ] || { echo "$f: absent"; continue; }
  echo "--- $f"; grep -E "^($NON_SECRET_KEYS)=" "$f"
  for k in $SECRET_NAMES; do v=$(grep -E "^$k=" "$f" | head -1 | cut -d= -f2-); [ -n "$v" ] && echo "$k=SET" || echo "$k=UNSET"; done
done
for f in "$SHARED"/docker/labapp/lab-"$LAB_ID"/.env "$SHARED"/docker/labapp/dev/.env; do
  [ -f "$f" ] && { echo "--- $f"; grep -E "^($NON_SECRET_KEYS)=" "$f"; }
done

h "lab_status.json (identity + lifecycle fields)"
for f in /etc/labapp/lab_status.json "$SHARED/labs/logs/labs/$LAB_ID/gns3/lab_status.json"; do
  [ -f "$f" ] || { echo "$f: absent"; continue; }
  echo "--- $f  sha256=$(sha256sum "$f" | cut -c1-16)"
  python3 - "$f" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
c = d.get("checks", {}) if isinstance(d.get("checks"), dict) else {}
keys = ["labKey", "labId", "STATUS", "READY", "HEALTHY", "DELETED", "vff_lab_tsg_id",
        "day0_config_status", "day1_config_status", "first_time_boot", "scenario", "stage"]
print({k: d.get(k) for k in keys if k in d})
print("checks:", {k: c.get(k) for k in ("labKey", "labId") if k in c})
print("last* keys:", sorted(k for k in d if k.startswith("last")))
print("vff_keys empty:", d.get("vff_keys") in ({}, None), " ions:", len(d.get("ions") or []), " panos:", len(d.get("panos") or []))
PY
done
ls /etc/labapp/ 2>/dev/null | grep -E 'bak|old' | head
echo "ion_keys.env: $(ls /var/lib/sase-labapp/lifecycle/ion_keys.env 2>&1)"

h "foreign TSG / lab identity leak scan (/etc/labapp, /etc/gns3)"
if [ -n "$FOREIGN" ]; then
  for t in $FOREIGN; do grep -rl --exclude='*.bak*' "$t" /etc/labapp /etc/gns3 2>/dev/null | sed "s|^|!! foreign TSG $t in |"; done
  echo "(scan done)"
else echo "no foreign list passed"; fi
grep -nE 'lab[0-9]+' /etc/hosts | grep -v "$LAB_KEY" | head -5
nft list tables 2>/dev/null | tr '\n' ' '; echo

h "docker / labapp"
docker ps -a --format '{{.Names}}\t{{.Image}}\t{{.Status}}' 2>/dev/null
curl -ks -m 5 -o /dev/null -w 'labapp health/live: %{http_code}\n' https://127.0.0.1/health/live 2>/dev/null || true
curl -s -m 5 -o /dev/null -w 'uvicorn 8082 health/live: %{http_code}\n' http://127.0.0.1:8082/health/live 2>/dev/null || true

h "GNS3 + TLS"
echo "gns3server: $(systemctl is-active gns3server)  version: $(ls -d /opt/gns3/venv-gns3-* 2>/dev/null | tr '\n' ' ')"
openssl x509 -in /etc/gns3/certs/web/server.crt -noout -subject -enddate -fingerprint -sha256 2>/dev/null
openssl x509 -in /etc/gns3/certs/web/server.crt -noout -ext subjectAltName 2>/dev/null | tail -1

h "disk / load"
df -h / /opt 2>/dev/null | tail -2; free -g | head -2

h "lab logs on shared tree (newest)"
ls -lt "$SHARED/labs/logs/labs/$LAB_ID/" "$SHARED/labs/logs/labs/$LAB_ID/gns3/" 2>/dev/null | head -25
for f in $(ls -t "$SHARED/labs/logs/labs/$LAB_ID/gns3/"*.log 2>/dev/null | head -4); do
  echo "--- errors in $f"; grep -E ' ERROR |Traceback' "$f" | tail -3
done
echo; echo "END $(hostname) $(date -u +%FT%TZ)"
