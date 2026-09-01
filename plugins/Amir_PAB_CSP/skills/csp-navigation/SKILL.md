---
name: csp-navigation
description: Navigation of the Palo Alto Networks Customer Support Portal (CSP) web UI when it runs inside the Prisma Access Browser (PAB). Use this skill WHENEVER a task touches the support portal, support cases / TAC cases, device assets and serial numbers, licenses, or user/account administration on support.paloaltonetworks.com — even if the user just says "check the case", "look at our assets", or "open the support portal".
---

# Navigating the Customer Support Portal (CSP) inside PAB

The CSP (Customer Support Portal, support.paloaltonetworks.com) is where Palo Alto
Networks customers manage support cases (TAC cases), registered device assets,
licenses, and account users.

**Prerequisite:** load and follow `Amir_PAB:pab-driver` first — the cua-driver access
pattern and the READ-ONLY SECURITY GATE apply to every action here. In the CSP,
viewing cases, assets, licenses, and account members is allowed; creating or updating
cases, registering/transferring assets, activating licenses, or changing account
membership needs the owner's approval BEFORE clicking. Case data can contain customer
information — keep it out of notes and outputs beyond what the task strictly needs.

## Current knowledge state

This skill is a scaffold: no live CSP-in-PAB session has been exercised yet, so no
navigation paths are recorded as verified. Do not invent menu paths. On the first
session, discover the UI from the screen (per the pab-driver method: screenshot →
read → act → verify) and record what is actually seen.

Things to establish and log in the first sessions:
- How the CSP is reached from inside PAB and which account context loads
- Top-level menu structure and exact labels
- Where support cases are listed/filtered and what a case view shows
- Where device assets, serials, and licenses are listed
- Which screens are view-only vs state-changing (case creation, asset actions)

## Learning protocol

After every CSP session, append newly verified facts to
[references/learned.md](references/learned.md) with date + verification method.
Promote repeatedly-confirmed paths into this SKILL.md. Never record credentials
or customer data.
