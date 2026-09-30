# Bubbsy Start Page & Tactical OSINT Command Hub

**Bubbsy Start Page** is a premier public web application and tactical cyber intelligence command center. It features **2,061+ curated OSINT links across 113 structured modules** — including 20 dedicated **[AUS] Australian** modules, an **Interactive Visual Toolkit**, and 5 **Hacker Search Engine** modules curated from `edoardottt/awesome-hacker-search-engines` — paired with multi-platform Visual Identity Disambiguation, Social Recon, and a Live CVE Threat Radar.

---

## ⚡ Key Features

1. **Live Cloud Edge & Continuous Threat Intelligence**:
   - Deployed on Cloudflare Pages with Edge Workers and Cloudflare D1 analytics.
   - Live Threat Intel & CVE Radar dynamically pulling real-time vulnerabilities from CISA KEV (1,730+ CVEs), ASD / ACSC, and Essential Eight benchmarks.
   - Automated GitHub Actions data pipeline continuously synchronizes and validates the CVE catalog.

2. **2,061+ Curated OSINT Tools Across 113 Modules**:
   - 113 structured modules across 4 balanced columns (Threat Intel, Geolocation, People & Email, Social Networks, Dorking, DNS/IP, Darknet, Public Records, Gov & Police, etc.).
   - 20 dedicated **[AUS]** modules: Government & Data, Public Records, Police & Courts, Corporations/ABN/ASIC, Real Estate & Cadastre, Transport & Rego, News & Media, Gov Services & myGov, Telco/Postal/Address, Emergency & Weather, Defence & Security, Sport/Arts/Culture, Cyber Security & Scams, Professional/Health & Licence Registers, Maps/Geospatial & Environment, Banking/Tax & Consumer, Jobs/Education & Skills, Aviation/Rail & Vessel Tracking, Marketplaces & Forums, Energy/Utilities & Infrastructure.
   - **4 global depth modules**: Corporate Registries & Ownership (OpenCorporates, Aleph, ICIJ, OpenSanctions), Archives & Fact-Check, Satellite & Earth Observation, OPSEC & Secure Comms.
   - **5 Hacker Search Engine modules** (from `edoardottt/awesome-hacker-search-engines`): Servers & Attack Surface (Quake, ODIN, BinaryEdge, BGPview, Cloudflare Radar…), Vulnerabilities & Exploits (NVD, Vulners, VulDB, Exploit-DB, GTFOBins, LOLBAS…), Leaks/Credentials/Hashes (Dehashed, LeakCheck, CrackStation, ntlm.pw…), DNS/Certs/Infra (RapidDNS, DNSViz, Validin, CertSpotter…), Threat Intel & Malware (abuse.ch family, AnyRun, Hybrid Analysis, PhishTank, AbuseIPDB…).
   - **Interactive Visual Toolkit** module: Google Earth Timelapse, Windy, Ventusky, Radio Garden, SunCalc, Shadowmap, Stellarium, NASA Worldview, and more interactive visual tools.
   - Instant client-side fuzzy search with highlighted matches (`/` or `Ctrl+K`).

3. **Multi-Platform Visual Identity Disambiguation & Social Recon**:
   - Interactive Guided Triage & Disambiguation across 35 platforms (GitHub, Reddit, Keybase, Bluesky, Dev.to, OCAU, Whirlpool, etc.).
   - 3-Way interactive decision gates (`YES` / `UNSURE` / `NO`) with automated cross-platform metadata forwarding.
   - High-resolution avatar harvesting with side-by-side comparison lightbox and 1-click reverse image search pivots (Google Lens, Yandex, TinEye, PimEyes, Bing).
   - Cryptographic proof verification (PGP fingerprints & Keybase proof chains).
   - Timezone/activity chronolocation and corporate email permutations.
   - 1-click persona synthesis into the Visual Investigation Link Graph.

4. **Basic & Advanced Interface Modes**:
   - **Basic** (default on first visit): brand bar, search, and category ribbon only — three rows before your links, not seven. Five everyday search engines (Filter, Google, ChatGPT, Trove, ABN) and five inline tools (Tour, Palette, Radar, Add, Settings).
   - **More Tools** menu keeps the other 12 tools (Pivot, Dorks, Geo, Recon, Mail, Drops, Corp, Defang, Graph, Export, Theme, Typography) one click away — nothing is removed, just tucked away.
   - **Advanced**: restores the full tactical HUD — world clock ticker, hotkey bar, bang ribbon, all 16 search engines, and every tool inline.
   - Toggle lives in the header; your choice persists across sessions and is applied before first paint, so the dense HUD never flashes.

5. **Tactical OSINT HUD UI ("Pro Vibes")**:
   - Sleek dark glassmorphism styling with glowing status badges.
   - Live World Clock bar tracking 11 global timezones (LA, Houston, NY, London, Berlin, Cairo, Tehran, Delhi, HK, Tokyo, Sydney).
   - Category jump ribbon for instant section navigation.
   - 4 Cyberpunk themes: Tactical Obsidian (Default), Cyber Amber, Matrix Emerald, Dracula Midnight.

6. **Bang Shortcuts Support**:
   - `!shodan <ip>`: Search Shodan intelligence.
   - `!vt <hash>`: Query VirusTotal.
   - `!dork <query>`: Google Dorking search.
   - `!whois <domain>`: Domain whois lookup.
   - `!gh <term>`: GitHub code search.
   - `!archive <url>`: Wayback Machine archive.
   - `!radar`: Jump straight to Threat Intel & CVE Live Radar.

---

## 🌐 Public Deployment & Architecture

Bubbsy Start Page is built for the global web and deployed on **Cloudflare Pages**:
- **Hosting & CDN**: Cloudflare Pages edge network (`pages_build_output_dir = "."`).
- **Edge Functions**: Cloudflare Pages serverless functions (`functions/api/`):
  - `/api/radar/feed`: Real-time CISA KEV CVE stream with edge caching.
  - `/api/acsc/feed`: Australian Signals Directorate / ACSC cyber advisory stream.
  - `/api/gods-eye/feed`: Server-side proxy for Australian government open-data feeds.
  - `/api/track` & `/api/admin/*`: High-speed telemetry logging backed by Cloudflare D1.

---

## 💻 Developer & Contribution Guide

For contributors developing locally:

```bash
# Ingest and synchronize the latest live CVEs from CISA KEV
python update_cves.py

# Run local development preview server
python server.py
# Or preview with Cloudflare Wrangler
npx wrangler pages dev .
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `/` or `Ctrl + K` | Focus & select Omnisearch bar |
| `Esc` | Clear search / close results dock |
| `Enter` | Execute active search query |

---

## 🇦🇺 Author & Ecosystem

Developed by **Matthew Bubb (OnYaChamp)** ([@thebubbsy](https://github.com/thebubbsy)).
- Central Hub & Engineering Portfolio: [OnYaChamp.com](https://onyachamp.com)
- OpenXML Flagship: [MarkSmith Compiler](https://onyachamp.com/marksmith.html)
- Sovereign MDM: [LocalPilot Fleet](https://github.com/thebubbsy/LocalPilotFleet)
