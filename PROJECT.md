# Project: Advanced Multi-Platform Visual Identity Disambiguation & Cross-Pivot Corroboration Engine

## Architecture
- **Backend Architecture (`server.py`)**:
  - Python 3.14 standard library asynchronous/multi-threaded HTTP server (`ThreadingHTTPServer`).
  - REST endpoint `GET /api/social/candidates` with query parameters `platform`, `query`, `names`, `locations`, `org`, `limit`.
  - In-memory thread-safe TTL cache (`SOCIAL_CACHE`, 10-minute expiry) to preserve external API rate limits.
  - Comprehensive 35-Platform Scraper & Avatar Resolver Suite across 5 major categories:
    1. **Mainstream Social & Microblogging**: X / Twitter, Instagram, TikTok, Threads, Facebook, Bluesky, Mastodon, Tumblr, Pinterest, Snapchat.
    2. **Messaging & Community**: Telegram, Discord, Reddit, Linktree, VKontakte (VK), WeChat.
    3. **Video, Audio & Creator**: YouTube, Twitch, Kick, Rumble, Spotify, SoundCloud, Substack, Medium.
    4. **Professional & Dev**: LinkedIn, GitHub, GitLab, Dev.to, Keybase, Docker Hub, Stack Overflow.
    5. **Australian Networks**: Whirlpool Forums, OCAU, OzBargain, Gumtree AU.
  - Dynamic cross-pivot alias query expansion for R3.
  - Rich OSINT payload injection for R4: reverse image search deep links (Google Lens, Yandex, TinEye, PimEyes, Bing), PGP fingerprints, Keybase proof chains, candidate corporate email permutations, ABN/ASIC search URLs, and timezone chronolocation inference.
- **Frontend Architecture (`index.html`, `js/app.js`, `css/styles.css`, `data/radar_cache.js`)**:
  - Modular Tactical Cyberpunk Start Page & OSINT Hub supporting 4 color themes.
  - `#modal-social-recon`: Interactive Guided Triage & Disambiguation Workspace.
    - Single-platform Triage Carousel with Top 5 candidate profiles per platform, Rank #1-#5 badges, and 35-platform stepper tab ribbon.
    - 3-Way interactive decision gates: `YES` (emerald halo, auto-harvest, auto-advance), `UNSURE` (amber highlight), `NO` (dimming & exclusion).
    - Dual view modes: Guided Carousel vs Aggregate All Profiles Grid with interactive topic/keyword tag cloud and platform category filters (All, Mainstream, Messaging, Creator, Dev/Pro, Australian).
    - Harvested Intelligence Pool HUD displaying live accumulating badges (`👤 Names`, `📍 Locations`, `🏢 Orgs`, `🔗 Handles`, `🔑 Proofs`, `📧 Emails`), badge dismissal `×`, `+ Add Pivot`, `Copy Intel`, and `Reset Context`.
  - `#modal-avatar-compare`: Avatar Inspection Lightbox with side-by-side comparison across confirmed platforms, high-res zoom, and 1-click deep links to Google Lens, Yandex Visual Search, TinEye, PimEyes, and Bing Visual Search.
  - Cryptographic Proofs & Linked Handles Drawer: Formatted 40-character OpenPGP fingerprints, Keybase verified proof chains (Twitter, GitHub, Reddit, DNS), and profile anchors.
  - Email Permutation Matrix & Corporate Pivots: Combinatorial email candidate generation with 1-click copy and Australian Business Register (ABN Lookup) / ASIC Connect registry links.
  - Activity Chronolocation Timezone Estimator: 24-hour UTC histogram binning, circadian waking/sleep model, and Australian/international timezone mapping.
  - Persona Dossier Exporter: Formatted forensic Markdown report copied to clipboard and downloadable as `.md`.
  - Visual Investigation Link Graph (`#modal-graph`): HTML5 2D Canvas force-directed physics engine with kinetic energy auto-sleep (`totalKineticEnergy < 0.005`), radial constellation layout, and PNG exporter.
  - Offline Threat Radar Cache: 250 authentic CVE threat advisories bundled in `data/radar_cache.js` (`window.BUBBSY_RADAR_DATA`) and `js/app.js` (`BUNDLED_OFFLINE_RADAR_ADVISORIES`).

## Feature Inventory
Every feature from the Survey phase and User Directives is mapped to an assigned milestone.

| # | Feature | Description | Milestone | Source | Status |
|---|---------|-------------|-----------|--------|:------:|
| 1 | Multi-Threaded Server & TTL Cache | Upgrade `server.py` to `ThreadingHTTPServer` with 10-min thread-safe TTL cache | M1 | Survey Backend | DONE |
| 2 | Comprehensive 35-Platform Candidate Scraper | Implement candidate resolvers across all 35 platforms (Mainstream, Messaging, Creator, Dev, Australian) | M1 | User Directive | DONE |
| 3 | High-Resolution Avatar Resolvers | Extract authentic CDN avatar URLs for all 35 platforms with resilient fallbacks | M1 | User Directive | DONE |
| 4 | Backend Cross-Pivot Query Expansion | Dynamic alias & token expansion on `GET /api/social/candidates` with `names`, `locations`, `org` | M1 | Survey Backend | DONE |
| 5 | Backend OSINT Payload Generator | Inject reverse image URLs, PGP, email permutations, ABN/ASIC links, and timezone into candidate JSON | M1 | Survey Backend | DONE |
| 6 | Single-Platform Triage Carousel (35 Platforms) | Carousel UI displaying Top 5 candidates per platform with Rank #1-#5 and 35-platform stepper tabs | M2 | User Directive | DONE |
| 7 | 3-Way Interactive Decision Gates | `YES` (emerald halo, auto-harvest, auto-advance), `UNSURE` (amber), `NO` (dimming/exclusion) | M2 | Survey Frontend | DONE |
| 8 | Dual View Modes & Tag Cloud | Step-by-step Guided Triage vs Aggregate Grid with interactive topic/keyword tag cloud filtering & category pills | M2 | Survey Frontend | DONE |
| 9 | Harvested Intelligence Pool HUD | Real-time accumulating badge HUD (`👤 Names`, `📍 Locations`, `🏢 Orgs`, `🔗 Handles`), badge `×`, `+ Add Pivot`, Reset | M2 | Survey Frontend | DONE |
| 10 | Recursive Cross-Pivot Chaining UI | Auto-chain newly confirmed metadata into subsequent platform search queries with UI status string | M2 | Survey Frontend | DONE |
| 11 | Avatar Inspection & Reverse Search Modal | `#modal-avatar-compare` side-by-side comparison with 1-click Google Lens, Yandex, TinEye, PimEyes, Bing | M3 | Survey OSINT | DONE |
| 12 | Cryptographic Proofs & PGP Drawer | OpenPGP formatted 40-char fingerprint, Keybase proof chains, and verified profile anchors | M3 | Survey OSINT | DONE |
| 13 | Email Permutation & Corporate Pivots | Combinatorial candidate email generator matrix and 1-click ABN Lookup / ASIC Connect links | M3 | Survey OSINT | DONE |
| 14 | Activity Chronolocation Engine | Regex word-boundary timestamp analysis, 24-hr histogram, and Australian/international timezone badges | M3 | Survey OSINT / Challenger 2 | DONE |
| 15 | Forensic Persona Dossier Exporter | 1-click compilation of all confirmed accounts and metadata into formatted Markdown copied to clipboard | M4 | Survey OSINT | DONE |
| 16 | Visual Link Graph Node/Edge Engine Fix | Fix `addNodeToGraph` to return node ID, implement `addEdgeToGraph`, and extend palette (`social`, `geo`, `crypto`, `org`) | M4 | Survey OSINT | DONE |
| 17 | Radial Persona Graph Synthesis | 1-click "Send Persona to Link Graph" with central Person node and radial constellation layout | M4 | Survey OSINT | DONE |
| 18 | Full E2E Test Suite (Tiers 1-4) | Comprehensive opaque-box and backend test suite verifying all features end-to-end (233+ tests) | M5 / Test Track | Original Request | DONE |
| 19 | Adversarial Coverage Hardening (Tier 5) | White-box stress testing, corner cases, error recovery, and forensic integrity audit | M5 | Original Request | DONE |
| 20 | Continuous Refinement & System Polish | Sub-millisecond latency (<1ms), zero DOM thrashing (`BOOKMARK_SEARCH_INDEX`), 250 offline advisories bundle, WCAG AAA contrast, focus trap/restoration across 19 modals, dead code elimination, 239/239 pytest suite | M_REF | User Directive 2026-08-21 | DONE |
| 21 | Australian Modules Expansion & Interactive Visual Toolkit | 6 new `[AUS]` modules (News/Media/Streaming, Gov Services & myGov, Telco/Postal/Address, Emergency/Weather/Public Safety, Defence/Borders/National Security, Sport/Arts/Culture) + Interactive Visual Toolkit module (Earth Timelapse, Windy, Ventusky, Radio Garden, SunCalc, Shadowmap, Stellarium, NASA Worldview, GDELT, Kepler.gl); gap-fill links (Common Crawl, Marginalia, Wiby, Internet Archive full-text, Google Dataset Search, TheyRule, Crunchbase); new `visual_tools` ribbon pill & live-updating hero placeholder; onboarding tour extended with category-ribbon slide & dynamic tool/module totals; data pipeline rebuilt to id-based widget filtering | M_AUS | User Directive 2026-08-21 | DONE |
| 22 | Hacker Search Engines Expansion (awesome-hacker-search-engines) | 5 new `HACKER SEARCH` modules under `cyber_intel` (Servers & Attack Surface, Vulnerabilities & Exploits, Leaks/Credentials/Hashes, DNS/Certs/Infra, Threat Intel & Malware) curating 100+ tools from `edoardottt/awesome-hacker-search-engines` (Quake, ODIN, BinaryEdge, BGPview, NVD, Vulners, VulDB, Exploit-DB, GTFOBins, LOLBAS, Dehashed, LeakCheck, CrackStation, RapidDNS, DNSViz, abuse.ch family, AnyRun, Hybrid Analysis, PhishTank, AbuseIPDB…); +28 gap-fill links (Yep, Stract, SearXNG, Sourcegraph-adjacent code search, Hunter.io, RocketReach, Pipl, NumLookup, ChainAbuse, EpicVin…); dataset grown to 101 widgets / 1,904 links, version 2.5.0 | M_AUS | User Directive 2026-08-21 | DONE |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|:------:|
| M1 | Deep Multi-Platform Avatar & Profile Scraping Backend | `server.py` threading upgrade, in-memory TTL cache, `/api/social/candidates` route, full 35-platform scrapers (Mainstream, Messaging, Creator, Dev/Pro, Australian), high-res avatar extraction, cross-pivot expansion, chronolocation regex boundaries, and OSINT payload generation | none | DONE |
| M2 | Interactive Guided Triage & Disambiguation Workspace UI/UX | `index.html`, `css/styles.css`, `js/app.js`: Triage carousel with 35 platforms, Top 5 cards, 3-way gates (emerald/amber/dim), Dual views, Tag cloud, Category filter pills, Harvested Intelligence HUD, auto-advance & cross-pivot chaining | M1 | DONE |
| M3 | Rich Visual OSINT & Chrono-Correlation Tooling | `index.html`, `css/styles.css`, `js/app.js`: Avatar comparison lightbox & reverse image search links (Google Lens, Yandex, TinEye, PimEyes, Bing), Cryptographic proofs drawer, Email permutations, ABN/ASIC links, Chronolocation timezone engine | M2 | DONE |
| M4 | Persona Dossier & Visual Link Graph Synthesis | `js/app.js`, `index.html`, `css/styles.css`: Forensic Markdown dossier exporter, Graph engine bug fixes (`addNodeToGraph`, `addEdgeToGraph`), node type palette extension, 1-click radial persona graph synthesis into `#modal-graph` | M3 | DONE |
| M5 | Final E2E Test Pass & Adversarial Coverage Hardening | Pass 100% of E2E Test Suite (Tiers 1-4, 233+ tests), Tier 5 adversarial hardening, and final Forensic Integrity Audit | M1, M2, M3, M4, Test Track | DONE |
| Test Track | E2E Testing Suite (Tiers 1-4) | `tests/test_social_recon_e2e.py` & automated runner: Tier 1 (Feature Coverage), Tier 2 (Boundary & Corner), Tier 3 (Cross-Feature Combinations), Tier 4 (Real-World Application Scenarios), publishes `TEST_READY.md` | none | DONE |
| M_REF | Autonomous Continuous Refinement & System Polish | Performance & latency (<1ms, `BOOKMARK_SEARCH_INDEX`, event delegation, memoization), 100% zero-latency offline fidelity across 6 core utilities + 250 bundled CVE advisories, WCAG AAA contrast (72/72 combinations), modal focus trapping across 19 modals, dead code elimination, 239/239 pytest suite | M5 | DONE |
| M_AUS | Australian Modules Expansion & Interactive Visual Toolkit | 6 new `[AUS]` modules + Interactive Visual Toolkit (group `visual_tools`, new ribbon pill) + 5 Hacker Search Engine modules (group `cyber_intel`, curated from `awesome-hacker-search-engines`), gap-fill links across Search/Code/Email/People/Phone/Crypto/Vehicle/Geo, live-updating hero placeholder & stats, extended onboarding tour with dynamic totals, id-based widget filtering in `build_data.py` (101 widgets / 1,904 links) | M_REF | DONE |
