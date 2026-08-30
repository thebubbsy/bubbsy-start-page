# Bubbsy Start Page & Tactical OSINT Command Hub

**Bubbsy Start Page** is a high-performance tactical start page and intelligence command center. It features **2,061+ curated OSINT links across 113 structured modules** — including 20 dedicated **[AUS] Australian** modules, an **Interactive Visual Toolkit**, and 5 **Hacker Search Engine** modules curated from `edoardottt/awesome-hacker-search-engines` — paired with multi-platform Visual Identity Disambiguation, Social Recon, and a Live CVE Threat Radar.

---

## ⚡ Key Features

1. **100% Self-Hosted & Offline Resilient**:
   - Zero dependence on start.me or third-party cloud hosting.
   - Operates fully offline with zero external server requirements.
   - 250 bundled CVE & threat advisories cached locally.

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

4. **Tactical OSINT HUD UI ("Pro Vibes")**:
   - Sleek dark glassmorphism styling with glowing status badges.
   - Live World Clock bar tracking 11 global timezones (LA, Houston, NY, London, Berlin, Cairo, Tehran, Delhi, HK, Tokyo, Sydney).
   - Category jump ribbon for instant section navigation.
   - 4 Cyberpunk themes: Tactical Obsidian (Default), Cyber Amber, Matrix Emerald, Dracula Midnight.

5. **Bang Shortcuts Support**:
   - `!shodan <ip>`: Search Shodan intelligence.
   - `!vt <hash>`: Query VirusTotal.
   - `!dork <query>`: Google Dorking search.
   - `!whois <domain>`: Domain whois lookup.
   - `!gh <term>`: GitHub code search.
   - `!archive <url>`: Wayback Machine archive.
   - `!radar`: Jump straight to Threat Intel & CVE Live Radar.

---

## 🚀 How to Run

### Method 1: One-Click Launcher (Recommended)
Double-click `start_bubbsy.bat`.
This starts the local Python backend on `http://localhost:7777` and automatically opens your default browser.

### Method 2: Manual Command Line
```powershell
python server.py
```
Then navigate to `http://localhost:7777` in your browser.

### Method 3: Standalone Browser Mode (Zero Server)
Simply double-click `index.html`. The bundled dataset `data/osint_data.js` loads immediately in any browser with full client-side filtering.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `/` or `Ctrl + K` | Focus & select Omnisearch bar |
| `Esc` | Clear search / close results dock |
| `Enter` | Execute active search query |
