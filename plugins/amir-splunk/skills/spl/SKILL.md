---
name: amir-splunk-spl
description: >-
  SPL authoring: search-time patterns, stats/tstats, data models, performance, detections.
---

# spl

Author SPL for investigations/detections. Prefer `tstats` on accelerated DM when available.
Performance: earliest filters, avoid `*` joins, limit fields.
Deep KQL → sentinel plugin; ES|QL → elastic plugin.
