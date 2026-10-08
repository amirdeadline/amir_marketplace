# Cellular interfaces (4G LTE / 5G)

Domain: 2 | Applies to: ION 1200 / 1200-S / 3200H cellular variants; Admin Guide May 2025; network selection from 6.5.1 | Status: DOCUMENTED | Last updated: 2026-10-08

## Explanation (plain words)

Cellular ION models carry a built-in modem with two SIM slots. The cellular link can be a backup, an active link next to wired links, or the only link. The device recognizes major carriers' SIMs and loads the right modem firmware automatically; for other carriers you give it an APN. Because cellular data usually costs money, the product has switches to keep control traffic and probes off the cellular link unless nothing else works.

## Documented behavior

- Modem falls back to 3G when 4G/5G is absent. Dual SIMs give carrier backup; auto-detection of AT&T, T-Mobile, Verizon SIMs with automatic profile and firmware.
- Configuration (`Workflows > Devices > Claimed Devices > Configure > Interfaces > Cellular Interfaces`): name, admin up, SIM status; use for Internet or Private WAN; circuit label (see "Minimize Metered LTE Usage", admin guide p. 456); APN: Auto (default; dynamic-IP SIMs from AT&T, T-Mobile, Verizon), APN profile (`Manage > Resources > Configuration Profiles > APN`; PAP/CHAP/PAP-CHAP, username/password), or manual; IP type IPv4 or IPv4v6; IPFIX collector/filter; NAT zone = internet; External NAT address and port; **IP MTU IPv4 552–1428, IPv6 1280–1428**; **Network Selection** (Auto default; manual selection does not fall back automatically; available from **6.5.1**).
- Auto APN supports all major carriers in: USA, Canada, Japan, Australia, Taiwan, Philippines, Thailand, Cambodia, Vietnam, Hong Kong, Korea, Qatar.
- **SIM switchover**: automatic when the active SIM cannot establish a data session for more than **five minutes**; limited to two switchovers (SIM1→SIM2→SIM1); different-carrier secondary SIM causes a modem reset and firmware load; same carrier does not.
- SIM PIN: configure then enable; three attempts; after the third failure the SIM is blocked, alarm `Device_Cellular_SIM_PUK_Needed`, PUK needed to unblock; blocked active SIM triggers switchover; PIN saved on the device for verification after resets; superuser can set APN, SIM security and firmware through CLI toolkit commands before claim.
- Firmware: AT&T, T-Mobile, Verizon and Generic (PTCRB/GCF) images pre-loaded; up to two firmware files on the modem, inactive ones stored on the ION; schedule download/update now or later; max download/upgrade time 5–59 minutes. New 5G modem firmware for 1200-C5G-WW / 1200-S-C5G-WW is compatible with ION 5.6.1+ but **6.1.6 or above is recommended before applying it** (modems on 3.14.x must first go to 6.1.6+).
- Monitoring (`Monitor > Activity > Cellular`): filters by site, device, module, carrier, APN, circuit; charts: signal strength quality (Excellent/Good/Fair/Poor/Dead Zone), signal stats (SNR dB, RSSI dBm, RSRP dBm, RSRQ dB, RSCP dBm for 3G), traffic volume (exported every minute), technologies (3G/LTE/5G), bandwidth usage (Kbps, per minute), packet drops/errors/overflows, GPS locations, cellular tower switches; time ranges 1H–3M; refresh every 5 minutes.
- Related CLI names: `config cellular modem`, `debug cellular stats`, `dump cellular config`, `dump cellular status`, `dump cellular stats`.
- Hardware: see note 01-fundamentals/05 (bands, carrier certifications). Deck: two nano-SIM (4FF) slots, micro-USB modem debug port needs special BIOS; IMEI printed on the back panel; 1200-C-NA/ROW have 3 antennas, C5G-WW has 4.

## Internal best practice (WS-001)

Upgrade modem firmware to the recommended version shown on the Firmware page for your carrier; use "Minimize Cellular Usage" for metered links (raises cost, stops controller statistics/connections on that circuit); adjust keep-alives on LTE to reduce control traffic at the cost of slower failure detection; cellular default MTU 1428.

## Claims register

| Claim | Label | Evidence | Source pointer |
|---|---|---|---|
| Modes (backup, active/active, only link); dual SIM; carrier auto-detect | VERIFIED | DOC | SRC-000029 p.188 |
| APN options and auto-APN country list | VERIFIED | DOC | SRC-000029 pp.189–192 |
| MTU ranges; network selection from 6.5.1 | VERIFIED | DOC | SRC-000029 p.190 |
| SIM switchover rules (5 minutes, two switchovers, modem reset on carrier change) | VERIFIED | DOC | SRC-000029 p.192 |
| SIM PIN behavior and PUK alarm | VERIFIED | DOC | SRC-000029 pp.193–197 |
| Firmware management and 6.1.6 recommendation | VERIFIED | DOC | SRC-000029 pp.197–199 |
| Cellular monitoring charts and metrics | VERIFIED | DOC | SRC-000029 pp.199–207 |
| Cellular software bypass pair for HA | VERIFIED | DOC | SRC-000029 pp.236–238 |
| Antenna counts, SIM form factor, debug port | UNVERIFIED (deck) | DOC | WS-033 slides 55–64 |

## Open questions

- KG-075: "Minimize Metered LTE Usage" exact behavior (admin guide p.456) to be read in B9 (path policy).
