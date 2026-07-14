"""One-shot sync: status report -> Asana tasks (comments, complete, due dates, tags)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from asana_connector.client import AsanaClient, AsanaError

REPORT = "2026-06-04"
PREFIX = f"[Status sync {REPORT}]"

# gid -> (action, comment)  action: "complete" | "open"
UPDATES: list[tuple[str, str, str]] = [
    # §1 Planning
    (
        "1215254574906244",
        "open",
        f"{PREFIX} §1 ~95% complete. Focus shifting to §3. "
        "Aug 2026-08-31 deadline confirmed; E-00–E-03 in scope.",
    ),
    (
        "1215254574906245",
        "open",
        f"{PREFIX} §1.1 Draft HLD — ✅ Agents architecture doc delivered. "
        "Open: PDF diagram export pending.",
    ),
    (
        "1215254574906246",
        "open",
        f"{PREFIX} §1.2 EMEA Automation — 🔄 In progress. "
        "Bootstrap + scripts/gns3/build_lab_full.py delivered to EMEA automation track.",
    ),
    (
        "1215254574906247",
        "complete",
        f"{PREFIX} §1.3 Topology & Day-1 planning — ✅ Complete. "
        "Excel-driven topology; lab1 v1.1 workbook in projects/lab1/v1.1/.",
    ),
    (
        "1215254574906248",
        "complete",
        f"{PREFIX} §1.4 Scope & requirements — ✅ Complete. Documented in project.md.",
    ),
    (
        "1215254574906249",
        "complete",
        f"{PREFIX} §1.5 IP addressing plan — ✅ Complete. Documented in Agents pack.",
    ),
    # §2 Platform
    (
        "1215254574906250",
        "complete",
        f"{PREFIX} §2 Platform & Repository Foundation — ✅ ~95% complete (lab2 cluster). "
        "All §2.1 GCP + §2.2 bootstrap scripts delivered.",
    ),
    (
        "1215254574906251",
        "complete",
        f"{PREFIX} §2.1 GCP lab platform — ✅ Complete on lab2 (10.100.20.4). "
        "3× GNS3 compute + Windows Server VM provisioned.",
    ),
    (
        "1215254574906252",
        "complete",
        f"{PREFIX} §2.1.1 VM sizing & networking — ✅ Complete.",
    ),
    (
        "1215254574906253",
        "complete",
        f"{PREFIX} §2.1.2 Install/prepare VMs — ✅ Complete (3× GNS3 + Win-Server on lab2).",
    ),
    (
        "1215254574906254",
        "complete",
        f"{PREFIX} §2.1.3 GNS3 controller install — ✅ Complete on lab2.",
    ),
    (
        "1215254574906255",
        "complete",
        f"{PREFIX} §2.1.4 Public NAT / firewall rules — ✅ Complete.",
    ),
    (
        "1215254574906256",
        "complete",
        f"{PREFIX} §2.2 Build-new_lab bootstrap — ✅ Complete. "
        "Includes build_lab_full.py orchestrator, gns3_health_check.py, repo layout "
        "(scripts/lib, scripts/topology, projects/lab1/v1.1/).",
    ),
    (
        "1215254574906257",
        "complete",
        f"{PREFIX} §2.2.1 install_gns3.py — ✅ Complete (--check-only / --force).",
    ),
    (
        "1215254574906258",
        "complete",
        f"{PREFIX} §2.2.2 create_templates.py — ✅ Complete (hash-based template sync).",
    ),
    (
        "1215254574906259",
        "complete",
        f"{PREFIX} §2.2.3 create_vxlan.py — ✅ Complete (hub-spoke overlay on lab2).",
    ),
    # §3 Topology
    (
        "1215254574906260",
        "open",
        f"{PREFIX} §3 Topology & Day-1/Day-2 — 🔄 ~55% overall. "
        "dc01 Windows Phase 1 ✅. Critical gap: task 3.4 VyOS Day-1 push. "
        "3.7 Day-2 SD-WAN blocked on SCM credentials (target creds 2026-07-07). "
        "Next milestone M2 Day-1 validated by 2026-06-27.",
    ),
    (
        "1215254574906261",
        "open",
        f"{PREFIX} §3.1 Install GNS3 nodes — 🔄 In progress. "
        "create_topology.py + Excel workbook; project V1.4 deployed on lab2.",
    ),
    (
        "1215254574906262",
        "open",
        f"{PREFIX} §3.2 Images & templates — 🔄 In progress. "
        "create_templates.py delivered; template parity checks ongoing.",
    ),
    (
        "1215254574906263",
        "open",
        f"{PREFIX} §3.3 Test communications & structure — ⏳ Pending. "
        "Blocked until §3.4 Day-1 VyOS configs pushed to live nodes.",
    ),
    (
        "1215254574906264",
        "open",
        f"{PREFIX} §3.4 Deploy Day-1 config — 🔄 TOP PRIORITY. "
        "configs/day1/ ready (14+ VyOS .cfg). Live push TBD via push_day1_configs.py. "
        "Target: 2026-06-13. Blocks 3.3, 3.6, E-02.",
    ),
    (
        "1215254574906265",
        "complete",
        f"{PREFIX} §3.5 Windows Server Day-1 — ✅ COMPLETE. "
        "dc01 @ 10.100.20.5 — domain lab2.prismalab.info, AD/DNS/DHCP/PKI/identity. "
        "phase1-complete.json + validation-latest.json. Doc: 13-win_server.md. "
        "Open sub-item: User-ID Agent Step 8 (MSI manual, svc-panuid ready).",
    ),
    (
        "1215254574906266",
        "open",
        f"{PREFIX} §3.6 Test Day-1 + snapshots — ⏳ Pending after 3.4 validates. "
        "Target gate: M2 by 2026-06-27.",
    ),
    (
        "1215254574906267",
        "open",
        f"{PREFIX} §3.7 Configure Day-2 (SD-WAN) — ⚠️ BLOCKED: SCM credentials not available. "
        "Escalation target: credentials by 2026-07-07. Blocks E-03, E-05, M3.",
    ),
    (
        "1215254574906268",
        "open",
        f"{PREFIX} §3.8 Test Day-2 + snapshots — ⏳ Pending §3.7. Program target 2026-08-31.",
    ),
    (
        "1215254574906269",
        "open",
        f"{PREFIX} §3.9 Troubleshooting scenarios — ⏳ Design captured in exercise index; "
        "execution pending Day-1/Day-2 baseline.",
    ),
    (
        "1215254574906270",
        "open",
        f"{PREFIX} §3.10 User test tools — 🔄 Partial. E-00 ✅; E-01 🔄. "
        "E-02/E-03 blocked on §3.4 and §3.7 respectively.",
    ),
    # §4 Automation
    (
        "1215254574906271",
        "open",
        f"{PREFIX} §4 Automation — 🔄 ~55%. Scripts in repo (build_lab_full, push_day1_configs, "
        "cleanup_gns3_project_docker, topology backup/create). E2E restore + scheduler TBD.",
    ),
    (
        "1215254574906272",
        "open",
        f"{PREFIX} §4.1 Day-1 config restore — ⏳ E2E TBD. push_day1_configs.py available for VyOS.",
    ),
    (
        "1215254574906273",
        "open",
        f"{PREFIX} §4.2 Day-1 snapshot restore — ⏳ Manual GNS3 snapshots; automation pending post-M2.",
    ),
    (
        "1215254979227306",
        "open",
        f"{PREFIX} §4.3 LAB scheduler integration — ⏳ SOP drafted; not wired to portal yet.",
    ),
    # §5 Documentation
    (
        "1215254979227307",
        "open",
        f"{PREFIX} §5 Documentation — 🔄 ~88% updating. Core admin/automation/user guides in progress.",
    ),
    (
        "1215254979227308",
        "open",
        f"{PREFIX} §5.1 LAB Admin Guide — 🔄 Updated 13-win_server.md, 14-win11-instruction.md.",
    ),
    (
        "1215254979227309",
        "open",
        f"{PREFIX} §5.2 LAB Automation Documents — 🔄 lab-config-reference.md, Agents pack, "
        "lab2-session-remaining-tasks.md.",
    ),
    (
        "1215254979227310",
        "open",
        f"{PREFIX} §5.3 LAB User Guide — 🔄 Core guides done; expand with §3.10 enablement modules.",
    ),
]

# Critical path due dates
DUE_DATES: dict[str, str] = {
    "1215254574906264": "2026-06-13",  # 3.4 VyOS push target
    "1215254574906266": "2026-06-27",  # M2 Day-1 gate
    "1215254574906267": "2026-07-07",  # SCM credentials
}

# gid -> tag names to add (created in workspace when missing)
ADD_TAGS: dict[str, list[str]] = {
    "1215254574906264": ["status-sync", "critical-path"],
    "1215254574906267": ["status-sync", "blocked"],
}

# gid -> tag names to remove
REMOVE_TAGS: dict[str, list[str]] = {}


def main() -> int:
    completed = 0
    commented = 0
    tagged = 0
    errors: list[str] = []

    with AsanaClient() as c:
        workspace_gid = c.default_workspace_gid()
        for gid, action, comment in UPDATES:
            try:
                c.post(f"/tasks/{gid}/stories", data={"text": comment})
                commented += 1
                if action == "complete":
                    c.put(f"/tasks/{gid}", data={"completed": True})
                    completed += 1
                if gid in DUE_DATES:
                    c.put(f"/tasks/{gid}", data={"due_on": DUE_DATES[gid]})
                add_names = ADD_TAGS.get(gid)
                remove_names = REMOVE_TAGS.get(gid)
                if add_names or remove_names:
                    c.apply_task_tags(
                        gid,
                        workspace_gid,
                        add_tag_names=add_names,
                        remove_tag_names=remove_names,
                        create_missing=True,
                    )
                    tagged += 1
                time.sleep(0.15)  # gentle rate limit
            except AsanaError as exc:
                errors.append(f"{gid}: {exc.message}")

    print(
        f"commented={commented} completed={completed} tagged={tagged} "
        f"errors={len(errors)}"
    )
    for e in errors:
        print(f"  ERROR: {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
