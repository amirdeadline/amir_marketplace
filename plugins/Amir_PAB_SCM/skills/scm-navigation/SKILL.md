---
name: scm-navigation
description: Expert navigation of Strata Cloud Manager (SCM), Palo Alto Networks' web management console, when it runs inside the Prisma Access Browser (PAB). Use this skill WHENEVER a task touches SCM, Strata Cloud Manager, Prisma SD-WAN or Prisma Access monitoring/administration, tenants/TSGs, dashboards, incidents and alerts, ION devices, branch sites, or validating documentation against the SCM UI — even if the user just says "check the portal", "look at the tenant", or "verify this screen".
---

# Navigating Strata Cloud Manager (SCM) inside PAB

SCM (Strata Cloud Manager) is Palo Alto Networks' cloud web console for managing
Prisma SD-WAN, Prisma Access, and NGFWs. In this workflow it runs inside the
Prisma Access Browser (PAB) desktop app.

**Prerequisite:** load and follow `Amir_PAB:pab-driver` first — it holds the cua-driver
access pattern and the READ-ONLY SECURITY GATE. The gate applies to every click in SCM:
navigation and viewing are free; anything that saves, commits, pushes, creates, deletes,
modifies, enables/disables, or switches tenant needs the owner's approval first.
Never push config to test something.

## Before doing anything in SCM

1. Confirm which tenant the open session is on. Tenants are identified by a name and a
   TSG ID (Tenant Service Group — the number identifying the tenant). Verify against
   what the owner specified before reading or reporting anything; never switch tenants
   on your own.
2. Remember SCM's menus move between releases (for example, entry points have
   historically shifted between "Workflows" and "Manage", and "Monitoring" vs
   "Monitor"). Treat any remembered path as a hypothesis — confirm on screen, and if
   the live UI differs from this skill, trust the screen and log the difference
   (see Learning protocol).

## SCM areas relevant to Prisma SD-WAN operations

These areas are documented in validated Palo Alto material; exact labels must still be
confirmed against the live release on every visit:

- **Dashboards** — widget-based views incl. Prisma SD-WAN dashboards: Device to
  Controller Connectivity, Applications, Incidents by Sites, Link Quality, Bandwidth
  Utilization, Transaction Stats, Predictive Analytics.
- **Monitor** — Branch Sites (Map / List / Activity / Flow views), Data Centers,
  ION Devices (Device List / Activity). Selecting a site commonly deep-links into
  Incidents and Alerts filtered for that site.
- **Incidents and Alerts** — four tabs: Overview, Incidents, Alerts, Settings
  (incident policy rules live under Settings).
- **Reports** — WAN Clarity reports (branch / data center / aggregate bandwidth).
- **Workflows** — e.g. Prisma SD-WAN Setup (branch/DC/ION onboarding). Setup screens
  are configuration surfaces: view only.
- **Manage** — policy and configuration objects. Everything here is config: view only.

## Working style for documentation validation

When validating docs against SCM: follow the documented path literally, screenshot each
step, and record per item whether it is correct / outdated / mismatched (label, layout,
navigation) / missing / not-verifiable. Stop at the first state-changing step and report
instead of clicking it.

## Learning protocol

After every SCM session, append newly verified navigation facts (exact menu labels,
paths, view names, deep-link behaviors, load times, quirks) to
[references/learned.md](references/learned.md) with date + verification method. Promote
repeatedly-confirmed paths into this SKILL.md. Never record credentials, TSG secrets,
or customer data.
