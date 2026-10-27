#!/usr/bin/env bash
# fix_route10_persistent.sh — make 10.0.0.0/8 via nic1 survive systemd-networkd restarts.
# Runs ON a GNS3 VM. Default = dry-run (prints the plan). --apply writes the drop-in and adds
# the route now. Does NOT restart systemd-networkd or touch any other interface.
#
# Why: the route was added with `ip route replace` (nic1-route-10.service, startup host_routes).
# networkd treats it as a "foreign" route and deletes it whenever it restarts — e.g. when
# unattended-upgrades upgrades a package at ~06:30 UTC (lab7, 2026-10-27). The dhclient hook
# never fires (Ubuntu 22.04 uses networkd, not dhclient). A [Route] in networkd's own config
# is re-applied on every networkd start/reconfigure.
#
#   ssh root@<nic1> 'bash -s' -- --apply < $LE/scripts/fix_route10_persistent.sh
set -euo pipefail
APPLY=0; [ "${1:-}" = "--apply" ] && APPLY=1
NET=10.0.0.0/8; GW=10.95.98.129; METRIC=100; DROPIN_NAME=60-corp-10-8.conf

# Capture first, then parse: `cmd | awk '{...; exit}'` + pipefail kills the script on SIGPIPE.
ADDRS=$(ip -o -4 addr show)
NIC1_IF=$(awk '$4 ~ /^10\.95\.98\./ {print $2}' <<<"$ADDRS" | head -1)
[ -n "$NIC1_IF" ] || { echo "no interface with a 10.95.98.x address — not a lab VM nic1? abort"; exit 1; }
STATUS=$(networkctl status "$NIC1_IF" 2>/dev/null || true)
NETFILE=$(awk -F': ' '/Network File/ {print $2}' <<<"$STATUS" | head -1)
NETNAME=$(basename "${NETFILE:-/run/systemd/network/10-netplan-$NIC1_IF.network}")
DIR=/etc/systemd/network/$NETNAME.d
CONTENT="# Managed by lab expert agent: corp 10/8 via nic1 (survives networkd restarts)
[Route]
Destination=$NET
Gateway=$GW
GatewayOnLink=yes
Metric=$METRIC"

echo "host=$(hostname) nic1_if=$NIC1_IF network_file=${NETFILE:-?} dropin=$DIR/$DROPIN_NAME"
echo "current: $(ip route show $NET | tr '\n' ';')"
if [ $APPLY -eq 0 ]; then
  echo "DRY-RUN: would write $DIR/$DROPIN_NAME:"; echo "$CONTENT" | sed 's/^/    /'
  echo "DRY-RUN: would run: ip route replace $NET via $GW dev $NIC1_IF metric $METRIC onlink"
  exit 0
fi
mkdir -p "$DIR"
printf '%s\n' "$CONTENT" > "$DIR/$DROPIN_NAME.tmp" && mv "$DIR/$DROPIN_NAME.tmp" "$DIR/$DROPIN_NAME"
ip route replace "$NET" via "$GW" dev "$NIC1_IF" metric "$METRIC" onlink
echo "applied. now: $(ip route show $NET | tr '\n' ';')"
echo "networkd picks the drop-in up on its next start; no restart done here."
