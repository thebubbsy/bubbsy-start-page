# Bubbsy Start Page (Local OSINT Hub & Voidtools Everything)

**Bubbsy Start Page** is a locally-hosted, high-performance tactical start page and intelligence command center. It replicates and expands upon the **OSINT4ALL** dashboard with **1,904+ curated OSINT links across 101 modules** — including 12 dedicated **[AUS] Australian** modules, an **Interactive Visual Toolkit**, and 5 **Hacker Search Engine** modules curated from `edoardottt/awesome-hacker-search-engines` — paired with integrated local disk indexing powered by **Voidtools Everything (ES)**.

---

## ⚡ Key Features

1. **100% Self-Hosted & Local**:
   - Zero dependence on start.me or third-party cloud hosting.
   - Operates fully offline with zero external server requirements.
2. **Voidtools Everything (ES) Integration with HTTP Basic Auth**:
   - **Unified Omnisearch**: Instant local disk search right alongside web & OSINT engines.
   - **HTTP Server + Basic Auth Support**: Full support for authenticated Everything servers with Username & Password configuration in Settings.
   - **Interactive Connection Test**: Live "Test Everything Connection" button inside Settings to verify credentials.
   - **Dual-Mode Backend**: Communicates via Everything's built-in HTTP server plugin (`http://127.0.0.1:8080`) and auto-bridges to `es.exe` CLI.
   - **File Triage Actions**: 1-click **Open File**, **Reveal in Windows Explorer**, and **Copy Path**.
   - **Preset File Filters**: Quick filter by Documents (`.pdf`, `.docx`), Data (`.json`, `.py`, `.sql`), Archives (`.zip`, `.7z`), or Media.
3. **1,904+ Curated OSINT Tools**:
   - 101 structured modules across 4 balanced columns (Threat Intel, Geolocation, People & Email, Social Networks, Dorking, DNS/IP, Darknet, Public Records, Gov & Police, etc.).
   - 12 dedicated **[AUS]** modules: Government & Data, Public Records, Police & Courts, Corporations/ABN/ASIC, Real Estate & Cadastre, Transport & Rego, News & Media, Gov Services & myGov, Telco/Postal/Address, Emergency & Weather, Defence & Security, Sport/Arts/Culture.
   - **5 Hacker Search Engine modules** (from `edoardottt/awesome-hacker-search-engines`): Servers & Attack Surface (Quake, ODIN, BinaryEdge, BGPview, Cloudflare Radar…), Vulnerabilities & Exploits (NVD, Vulners, VulDB, Exploit-DB, GTFOBins, RevShells…), Leaks/Credentials/Hashes (Dehashed, LeakCheck, CrackStation, ntlm.pw…), DNS/Certs/Infra (RapidDNS, DNSViz, Validin, CertSpotter…), Threat Intel & Malware (abuse.ch family, AnyRun, Hybrid Analysis, PhishTank, AbuseIPDB…).
   - **Interactive Visual Toolkit** module: Google Earth Timelapse, Windy, Ventusky, Radio Garden, SunCalc, Shadowmap, Stellarium, NASA Worldview and more interactive visual tools.
   - Instant client-side fuzzy search with highlighted matches (`/` or `Ctrl+K`).
4. **Tactical OSINT HUD UI ("Pro Vibes")**:
   - Sleek dark glassmorphism styling with glowing status badges.
   - Live World Clock bar tracking 11 global timezones (LA, Houston, NY, London, Berlin, Cairo, Tehran, Delhi, HK, Tokyo, Sydney).
   - Category jump ribbon for instant section navigation.
   - 4 Cyberpunk themes: Tactical Obsidian (Default), Cyber Amber, Matrix Emerald, Dracula Midnight.
5. **Bang Shortcuts Support**:
   - `!es <query>`: Instantly query Voidtools Everything local disk.
   - `!shodan <ip>`: Search Shodan intelligence.
   - `!vt <hash>`: Query VirusTotal.
   - `!dork <query>`: Google Dorking search.
   - `!whois <domain>`: Domain whois lookup.
   - `!gh <term>`: GitHub code search.
   - `!archive <url>`: Wayback Machine archive.

---

## 🚀 How to Run

### Method 1: One-Click Launcher (Recommended)
Double-click [`start_bubbsy.bat`](file:///c:/Users/Tony/Documents/antigravity/peaceful-euclid/start_bubbsy.bat).
This starts the local Python backend on `http://localhost:7777` and automatically opens your default browser.

### Method 2: Manual Command Line
```powershell
python server.py
```
Then navigate to `http://localhost:7777` in your browser.

### Method 3: Standalone Browser Mode (Zero Server)
Simply double-click [`index.html`](file:///c:/Users/Tony/Documents/antigravity/peaceful-euclid/index.html). The bundled dataset `data/osint_data.js` loads immediately in any browser with full client-side filtering.

---

## 🔐 Configuring Voidtools Everything HTTP Server & Authentication

If your Voidtools Everything HTTP Server requires a Username and Password:
1. Open **Bubbsy Start Page** in your browser (`http://localhost:7777`).
2. Click the **Settings** button (gear icon in the top right) or click the **EVERYTHING (ES)** status chip in the top nav.
3. Enter your **HTTP Username** and **HTTP Password** (you can click the 👁️ icon to reveal/mask the password).
4. Click **⚡ Test Everything Connection** to immediately verify your credentials (it will display a green confirmation indicator).
5. Click **Save & Apply**.

### How to Enable HTTP Server in Voidtools Everything:
1. Open **Everything**.
2. Go to **Tools** &rarr; **Options** (or press `Ctrl+P`).
3. Select **HTTP Server** in the left menu.
4. Check **Enable HTTP server**.
5. Set your preferred Port (default `8080`) and optional Username / Password.
6. Click **Apply** & **OK**.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `/` or `Ctrl + K` | Focus & select Omnisearch bar |
| `Esc` | Clear search / close results dock |
| `Enter` | Execute active search query |
