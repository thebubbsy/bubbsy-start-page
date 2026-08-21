# E2E Test Infra: Advanced Multi-Platform Visual Identity Disambiguation & Cross-Pivot Corroboration Engine

## Test Philosophy
- Opaque-box, requirement-driven. Derived from `ORIGINAL_REQUEST.md`.
- Methodology: 4-Tier Test Case Design (Feature Coverage + Boundary/Corner Cases + Cross-Feature Interactions + Real-World Application Workloads).

## Feature Inventory & Test Mapping
| # | Feature | Requirement | Tier 1 (Min 5) | Tier 2 (Min 5) | Tier 3 (Pairwise) | Tier 4 (Scenario) |
|---|---------|-------------|:--------------:|:--------------:|:-----------------:|:-----------------:|
| 1 | GitHub Candidate & Avatar Scraping | R1 | 5 | 5 | ✓ | ✓ |
| 2 | Bluesky Actor & Avatar Extraction | R1 | 5 | 5 | ✓ | ✓ |
| 3 | Keybase Proofs & PGP Extraction | R1, R4 | 5 | 5 | ✓ | ✓ |
| 4 | Reddit Web Profile & Karma Scraping | R1 | 5 | 5 | ✓ | ✓ |
| 5 | GitLab, Dev.to & Docker Hub Scraping | R1 | 5 | 5 | ✓ | ✓ |
| 6 | Australian Forums (Whirlpool, OCAU, OzBargain) | R1 | 5 | 5 | ✓ | ✓ |
| 7 | Single-Platform Triage Carousel (Top 5) | R2 | 5 | 5 | ✓ | ✓ |
| 8 | 3-Way Decision Gates (YES, UNSURE, NO) | R2 | 5 | 5 | ✓ | ✓ |
| 9 | Dual View Modes (Guided vs Grid) & Tag Cloud | R2 | 5 | 5 | ✓ | ✓ |
| 10 | Harvested Intelligence Pool HUD & Auto-Chaining | R3 | 5 | 5 | ✓ | ✓ |
| 11 | Avatar Inspection & Reverse Image Pivots | R4 | 5 | 5 | ✓ | ✓ |
| 12 | Corporate Email Permutations & ABN/ASIC Pivots | R4 | 5 | 5 | ✓ | ✓ |
| 13 | Activity Chronolocation Timezone Estimator | R4 | 5 | 5 | ✓ | ✓ |
| 14 | Forensic Markdown Persona Dossier Export | R5 | 5 | 5 | ✓ | ✓ |
| 15 | Visual Investigation Link Graph Synthesis | R5 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- **Automated Test Runner**: `tests/test_social_recon_e2e.py`
- **Invocation**: `python tests/test_social_recon_e2e.py` or `pytest tests/`
- **Output**: Detailed tier-by-tier execution logs, pass/fail assertions, JSON schema validations, and exit code 0 on 100% pass.

## Coverage Thresholds
- **Tier 1 (Feature Coverage)**: ≥75 tests (≥5 per feature)
- **Tier 2 (Boundary & Corner Cases)**: ≥75 tests (empty queries, special characters, rate limits, timeouts, missing fields, unicode)
- **Tier 3 (Cross-Feature Combinations)**: ≥15 pairwise interaction tests (e.g. YES gate -> HUD update -> query parameter propagation -> reverse image URLs)
- **Tier 4 (Real-World Scenarios)**: ≥8 end-to-end full workflow scenarios (e.g., target `torvalds`, target `mitnick`, Australian IT target `whirlpool_user`, multi-platform corporate target)
- **Tier 5 (Adversarial Coverage Hardening)**: White-box challenger test generation and mutation testing.

## Real-World Application Scenarios (Tier 4)
| Scenario ID | Target Persona | Platforms Traversed | Key Corroboration Points | Expected Outcome |
|---|---|---|---|---|
| SC-1 | Linus Torvalds (`torvalds`) | GitHub -> Bluesky -> Keybase -> Reddit | Real name, Portland OR location, Linux Foundation org, PGP key, Reverse image search | Full persona synthesized with 4 confirmed platforms |
| SC-2 | Australian Tech Analyst (`oz_analyst`) | Whirlpool -> OCAU -> OzBargain -> GitHub | Sydney/Melbourne location, AEST UTC+10 timezone, ABN corporate search | Accurate Australian timezone & forum profile matching |
| SC-3 | Decentralized Developer (`crypto_dev`) | Bluesky -> Keybase -> Dev.to -> GitLab | Keybase Twitter/GitHub proofs, PGP fingerprint, email permutations | Verified cryptographic chain & email permutations |
| SC-4 | Rejected & Ambiguous Persona (`ambiguous_user`) | GitHub -> Reddit | Multiple candidate profiles, 1 YES, 1 UNSURE, 3 NO | Correct amber/dimming states, exclusion from final dossier |
| SC-5 | Manual Pivot Injection Persona | Custom Target | User injects `+ Add Pivot` manually in HUD | Newly injected alias propagates to downstream searches |
