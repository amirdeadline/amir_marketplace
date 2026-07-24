# SECURITY.md — amir_marketplace capability matrix

Credentials are **env-only**, masked to `****last4` in outputs. Default mode is
**read-only**. Mutating / destructive / scan / response actions **confirm first**
and print the exact command or request.

Slash commands are namespaced under **`/amir…`** (plugin names `amir` / `amir-*`).

| Plugin | Can read | Can change | Confirmation required | Credentials |
|--------|----------|------------|----------------------|-------------|
| **amir** | project JSON state / workspace (via tools) | state via tools + skills | skill-level gates for destructive ops | none in plugin |
| **amir-asana** | Asana tasks/projects (MCP) | create/update/complete tasks | confirm before mutate | `ASANA_ACCESS_TOKEN` |
| **amir-prisma** | local PANW markdown corpus + public docs | none (docs only) | n/a | `PRISMA_DOCS_PATH` |
| **amir-litellm** | proxy models/health/spend | chat/completions via MCP | preflight before session | `LiteLLM_*` |
| **amir-paloalto** | PAN-OS op/show, config get | set/edit/delete/commit | mutating API calls | `PANOS_HOST`, `PANOS_API_KEY` |
| **amir-aws** | AWS APIs via MCP / describe-list-get CLI | create/delete/modify | mutating CLI | AWS IAM (`AWS_PROFILE`/`AWS_REGION`) |
| **amir-azure** | Azure via MCP / `az show\|list` | create/update/delete | mutating CLI | `az login` |
| **amir-terraform** | plan/validate/state read | apply/destroy | apply confirm; destroy typed `DESTROY` | local/cloud provider creds |
| **amir-docker** | ps/logs/inspect | up/down/build/push/prune | down/push/prune/volume-rm | local docker |
| **amir-splunk** | search jobs / server info | saved searches, alerts | mutating knowledge objects | `SPLUNK_BASE_URL`, `SPLUNK_TOKEN` |
| **amir-elastic** | `_search`, `_cat`, mappings | index create/delete | delete-index typed confirm | `ELASTIC_BASE_URL`, `ELASTIC_API_KEY` |
| **amir-sentinel** | KQL queries | analytic rules, incidents | rule/incident mutations | `az login` + `SENTINEL_WORKSPACE_ID` |
| **amir-qradar** | AQL / offenses | offense/rules/ref sets | mutating ops | `QRADAR_BASE_URL`, `QRADAR_SEC_TOKEN` |
| **amir-cortex-xdr** | incidents/alerts/endpoints | isolate/unisolate/… | typed `action endpoint_id` | `XDR_FQDN`, `XDR_API_KEY_ID`, `XDR_API_KEY` |
| **amir-ssh** | remote stdout (after confirm) | remote commands user confirms | host+command; destructive typed host | SSH keys/agent |
| **amir-nmap** | scan results / parse files | launches scans | typed `AUTHORIZED <target>` | local `nmap` |
| **amir-wireshark** | pcap analysis | live capture | iface+outfile+limit+confirm | local `tshark` |
