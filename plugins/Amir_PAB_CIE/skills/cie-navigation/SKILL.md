---
name: cie-navigation
description: Navigation of the Cloud Identity Engine (CIE) web UI, Palo Alto Networks' cloud identity service, when it runs inside the Prisma Access Browser (PAB). Use this skill WHENEVER a task touches CIE, Cloud Identity Engine, directory sync, identity/user-ID data, authentication sources, or group mappings viewed in a Palo Alto cloud portal — even if the user just says "check identities" or "look at the directory sync".
---

# Navigating the Cloud Identity Engine (CIE) inside PAB

CIE (Cloud Identity Engine) is Palo Alto Networks' cloud service for identity:
it collects users and groups from directories (like Active Directory or Azure AD /
Entra ID) and makes them available to Palo Alto products for policy and
authentication.

**Prerequisite:** load and follow `Amir_PAB:pab-driver` first — the cua-driver access
pattern and the READ-ONLY SECURITY GATE apply to every action here. In CIE, viewing
directories, sync status, users, groups, and authentication settings is allowed;
adding/removing directories, changing sync or authentication configuration, or
anything with Save/Commit/Update needs the owner's approval BEFORE clicking.
Identity data is sensitive — never copy user lists or personal data into notes or
outputs beyond what the task strictly needs.

## Current knowledge state

This skill is a scaffold: no live CIE-in-PAB session has been exercised yet, so no
navigation paths are recorded as verified. Do not invent menu paths. On the first
session, discover the UI from the screen (per the pab-driver method: screenshot →
read → act → verify) and record what is actually seen.

Things to establish and log in the first sessions:
- How CIE is reached from inside PAB (direct URL, app switcher, or SCM hub link)
- Top-level menu structure and exact labels
- Where directory sync status and last-sync times are shown
- Where authentication types/sources are listed
- Which screens are view-only vs configuration surfaces

## Learning protocol

After every CIE session, append newly verified facts to
[references/learned.md](references/learned.md) with date + verification method.
Promote repeatedly-confirmed paths into this SKILL.md. Never record credentials,
tokens, or personal identity data.
