"""
Automated E2E Test Suite for Header Buttons and Modal Triggers across multiple viewports.
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

BUTTON_MODAL_PAIRS = [
    ('btn-tour', 'modal-tour'),
    ('btn-palette', 'modal-palette'),
    ('btn-open-pivot', 'modal-pivot'),
    ('btn-open-radar', 'modal-radar'),
    ('btn-open-dorks', 'modal-dorks'),
    ('btn-open-geo', 'modal-geo'),
    ('btn-open-social-recon', 'modal-social-recon'),
    ('btn-open-mail-access', 'modal-mail-access'),
    ('btn-open-domain-sniper', 'modal-domain-sniper'),
    ('btn-open-corp', 'modal-corp'),
    ('btn-open-defang', 'modal-defang'),
    ('btn-open-graph', 'modal-graph'),
    ('btn-open-export', 'modal-export'),
    ('btn-custom-bookmark', 'modal-custom-bookmark'),
    ('btn-open-typography', 'modal-typography'),
    ('btn-settings', 'modal-settings')
]

@pytest.mark.parametrize("w,h,vp_name", VIEWPORTS)
def test_header_modal_triggers_across_viewports(live_server, w, h, vp_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': w, 'height': h})
        # Mark tour as seen so it does not auto-popup and interfere during button clicks.
        # This suite exercises the full inline toolset, which is Advanced mode; the
        # Basic-mode path to the same tools is covered in test_ui_modes_e2e.py.
        context.add_init_script(
            "localStorage.setItem('bubbsy_tour_seen', 'true');"
            "localStorage.setItem('bubbsy_ui_mode', 'advanced');"
        )
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        for btn_id, modal_id in BUTTON_MODAL_PAIRS:
            btn = page.locator(f'#{btn_id}')
            assert btn.count() > 0, f"Button #{btn_id} missing from DOM"
            
            btn.click()
            time.sleep(0.15)
            
            is_active = page.evaluate(f'document.getElementById("{modal_id}").classList.contains("active")')
            modal = page.locator(f'#{modal_id}')
            assert is_active is True, f"Button #{btn_id} failed to activate #{modal_id} on {vp_name}"
            assert modal.is_visible() is True, f"Modal #{modal_id} is not visible on {vp_name}"
            
            page.keyboard.press('Escape')
            time.sleep(0.05)

        browser.close()
