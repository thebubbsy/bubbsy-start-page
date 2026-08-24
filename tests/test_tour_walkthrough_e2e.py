"""
Automated E2E Test Suite for the Comprehensive 12-Stage Interactive Tactical Tour Walkthrough.
"""

import pytest
import time
from playwright.sync_api import sync_playwright

VIEWPORTS = [
    (1920, 1080, '1080p'),
    (1366, 768, 'Laptop'),
    (1024, 768, 'Tablet'),
    (390, 844, 'Mobile')
]

EXPECTED_STAGES = [
    ("STAGE 01 / 12", "TACTICAL OSINT COMMAND HUB", "Mission Briefing: Bubbsy Command Architecture"),
    ("STAGE 02 / 12", "OMNI-SEARCH & BANG OPERATOR MATRIX", "Omnisearch, 35+ Bangs & Instant Routing"),
    ("STAGE 03 / 12", "LIVE THREAT INTEL & CVE RADAR", "Threat Intel CVE Live Radar & ACSC Feed"),
    ("STAGE 04 / 12", "KEYLESS EMAIL OSINT & RECON", "MailAccess: Email Intelligence & Consensus"),
    ("STAGE 05 / 12", "DOMAIN DROP SNIPER & EXPIRY RADAR", "Domain Drop Sniper & Backorder Launchpad"),
    ("STAGE 06 / 12", "IDENTITY DISAMBIGUATION & SOCIAL RECON", "Visual Identity Disambiguation & Avatar Scraper"),
    ("STAGE 07 / 12", "AUSTRALIAN CADASTRE & GEO RECON", "Australian Cadastre & Coordinate Recon"),
    ("STAGE 08 / 12", "CORPORATE OSINT & ABR / ASIC NETWORK", "Australian Corporate & ASIC / ABR Network"),
    ("STAGE 09 / 12", "ATTACK SURFACE & THREAT DORK ENGINE", "Threat Dork & Attack Surface Generator"),
    ("STAGE 10 / 12", "IOC NORMALIZER & SEARCH BUILDER", "Cyber Defang / Refang & IOC Normalizer"),
    ("STAGE 11 / 12", "INVESTIGATION LINK GRAPH CANVAS", "Visual Investigation Link Graph Canvas"),
    ("STAGE 12 / 12", "EXPORT, COMMAND PALETTE & ACCESSIBILITY", "Command Palette, Customizer & Forensic Export")
]

def test_tour_all_12_stages_walkthrough_and_navigation(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        # 1. Open the Tour via the top button
        page.locator('#btn-tour').click()
        time.sleep(0.3)

        modal_tour = page.locator('#modal-tour')
        assert modal_tour.is_visible() is True, "Tour modal failed to open"

        # 2. Step through each of the 12 stages
        for idx, (expected_badge, expected_cat, expected_title) in enumerate(EXPECTED_STAGES):
            badge = page.locator('#tour-step-badge').text_content()
            assert badge == expected_badge, f"Stage {idx+1} badge mismatch: got {badge}, expected {expected_badge}"

            cat_el = page.locator('.tour-slide-category').text_content()
            assert expected_cat in cat_el, f"Stage {idx+1} category mismatch: got {cat_el}, expected {expected_cat}"

            title_el = page.locator('.tour-slide-title').text_content()
            assert expected_title in title_el, f"Stage {idx+1} title mismatch: got {title_el}, expected {expected_title}"

            # Verify capability cards and try-live card exist
            assert page.locator('.tour-capability-card').count() >= 2, f"Stage {idx+1} missing capability cards"
            assert page.locator('.tour-live-try-card').count() == 1, f"Stage {idx+1} missing try-live card"

            # Advance to next stage if not on the last stage
            if idx < len(EXPECTED_STAGES) - 1:
                page.locator('#btn-tour-next').click()
                time.sleep(0.1)

        # 3. On final stage, click Finish button
        page.locator('#btn-tour-next').click()
        time.sleep(0.3)
        assert modal_tour.is_visible() is False, "Tour failed to close after final stage"

        # 4. Reopen and test stage navigator pills (jump to Stage 5 Domain Drops)
        page.locator('#btn-tour').click()
        time.sleep(0.2)
        pills = page.locator('.tour-nav-pill')
        assert pills.count() == 12, "Should have 12 stage navigation pills"

        # Click pill 5 (Domain Drops)
        pills.nth(4).click()
        time.sleep(0.1)
        assert page.locator('#tour-step-badge').text_content() == "STAGE 05 / 12"
        assert "Domain Drop Sniper" in page.locator('.tour-slide-title').text_content()

        # 5. Test keyboard navigation: press ArrowLeft -> Stage 4
        page.keyboard.press('ArrowLeft')
        time.sleep(0.1)
        assert page.locator('#tour-step-badge').text_content() == "STAGE 04 / 12"

        # Press '3' key -> Jump to Stage 3 Threat Radar
        page.keyboard.press('3')
        time.sleep(0.1)
        assert page.locator('#tour-step-badge').text_content() == "STAGE 03 / 12"

        # 6. Test 'Try Live' action from Threat Radar slide (press 'T')
        page.keyboard.press('t')
        time.sleep(0.4)
        assert page.locator('#modal-radar').is_visible() is True, "Try live action failed to open Threat Radar modal"

        browser.close()

@pytest.mark.parametrize("w,h,vp_name", VIEWPORTS)
def test_tour_responsive_rendering(live_server, w, h, vp_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': w, 'height': h})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        page.locator('#btn-tour').click()
        time.sleep(0.3)

        modal_tour = page.locator('#modal-tour')
        assert modal_tour.is_visible() is True, f"Tour modal not visible on {vp_name}"

        # Verify buttons & content fit
        assert page.locator('#btn-tour-next').is_visible() is True, f"Next button not visible on {vp_name}"
        assert page.locator('#tour-step-badge').is_visible() is True, f"Step badge not visible on {vp_name}"

        browser.close()
