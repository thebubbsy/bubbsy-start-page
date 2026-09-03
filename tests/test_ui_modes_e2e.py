"""
E2E coverage for the Basic / Advanced interface modes.

Basic is the default for first-time visitors: brand, search and categories only.
Advanced restores the full tactical HUD. Nothing is removed from the DOM in
either mode, so every tool stays reachable.
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

# Chrome that Basic mode hides to cut the header down from seven rows to three.
ADVANCED_ONLY_BARS = ['.world-clock-bar', '.shortcuts-hud-bar', '.bang-bar']

# Tools that move behind the "More Tools" menu in Basic mode.
OVERFLOW_TOOLS = [
    ('btn-open-pivot', 'modal-pivot'),
    ('btn-open-dorks', 'modal-dorks'),
    ('btn-open-geo', 'modal-geo'),
    ('btn-open-social-recon', 'modal-social-recon'),
    ('btn-open-mail-access', 'modal-mail-access'),
    ('btn-open-domain-sniper', 'modal-domain-sniper'),
    ('btn-open-corp', 'modal-corp'),
    ('btn-open-defang', 'modal-defang'),
    ('btn-open-graph', 'modal-graph'),
    ('btn-open-export', 'modal-export'),
    ('btn-open-typography', 'modal-typography'),
]

# Tools that stay inline in Basic mode.
CORE_TOOLS = ['btn-tour', 'btn-palette', 'btn-open-radar', 'btn-custom-bookmark', 'btn-settings']


def _page(p, w=1366, h=768, mode=None):
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': w, 'height': h})
    script = "localStorage.setItem('bubbsy_tour_seen', 'true');"
    if mode:
        script += f"localStorage.setItem('bubbsy_ui_mode', '{mode}');"
    context.add_init_script(script)
    page = context.new_page()
    return browser, page


def test_basic_is_the_default_and_hides_the_dense_chrome(live_server):
    """A first-time visitor lands in Basic mode with the ticker bars hidden."""
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        mode = page.evaluate("document.documentElement.getAttribute('data-ui-mode')")
        assert mode == 'basic', f"First visit should default to Basic mode, got {mode}"

        for sel in ADVANCED_ONLY_BARS:
            assert page.locator(sel).count() > 0, f"{sel} should remain in the DOM"
            assert page.locator(sel).is_visible() is False, f"{sel} should be hidden in Basic mode"

        # The essentials stay.
        assert page.locator('#main-search').is_visible() is True
        assert page.locator('#category-ribbon').is_visible() is True
        assert page.locator('#dashboard-grid').is_visible() is True

        browser.close()


def test_basic_mode_trims_search_engine_tabs(live_server):
    """Basic keeps five everyday engines; the long tail is Advanced-only."""
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        shown = page.eval_on_selector_all(
            '#search-mode-tabs .search-tab',
            "els => els.filter(e => e.offsetParent !== null).map(e => e.dataset.mode)"
        )
        assert set(shown) == {'filter', 'google', 'chatgpt', 'trove', 'abn'}, shown

        # Every tab is still in the DOM, just hidden.
        assert page.locator('#search-mode-tabs .search-tab').count() == 16

        browser.close()


def test_core_tools_stay_inline_in_basic_mode(live_server):
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        for btn_id in CORE_TOOLS:
            assert page.locator(f'#{btn_id}').is_visible() is True, \
                f"#{btn_id} should stay inline in Basic mode"

        assert page.locator('#btn-nav-more').is_visible() is True

        browser.close()


def test_overflow_menu_reaches_every_advanced_tool_in_basic_mode(live_server):
    """Nothing is lost in Basic mode: each advanced tool still opens its modal."""
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        panel = page.locator('#nav-overflow-panel')
        assert panel.is_visible() is False, "Overflow panel should start closed"

        for btn_id, modal_id in OVERFLOW_TOOLS:
            page.locator('#btn-nav-more').click()
            time.sleep(0.15)
            assert panel.is_visible() is True, "More Tools menu failed to open"

            page.locator(f'#{btn_id}').click()
            time.sleep(0.2)

            is_active = page.evaluate(
                f'document.getElementById("{modal_id}").classList.contains("active")'
            )
            assert is_active is True, f"#{btn_id} failed to open #{modal_id} from the overflow menu"

            # Using a tool closes the menu behind it.
            assert panel.is_visible() is False, f"Menu should close after clicking #{btn_id}"

            page.keyboard.press('Escape')
            time.sleep(0.1)

        browser.close()


def test_switching_to_advanced_restores_the_full_hud(live_server):
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        page.locator('#btn-mode-advanced').click()
        time.sleep(0.3)

        assert page.evaluate("document.documentElement.getAttribute('data-ui-mode')") == 'advanced'

        for sel in ADVANCED_ONLY_BARS:
            assert page.locator(sel).is_visible() is True, f"{sel} should return in Advanced mode"

        # Every tool is back inline and the overflow button steps aside.
        assert page.locator('#btn-nav-more').is_visible() is False
        for btn_id, _ in OVERFLOW_TOOLS:
            assert page.locator(f'#{btn_id}').is_visible() is True, \
                f"#{btn_id} should be inline in Advanced mode"

        shown_tabs = page.eval_on_selector_all(
            '#search-mode-tabs .search-tab',
            "els => els.filter(e => e.offsetParent !== null).length"
        )
        assert shown_tabs == 16, f"Advanced mode should show all 16 engine tabs, got {shown_tabs}"

        browser.close()


def test_mode_choice_persists_across_reload(live_server):
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        page.locator('#btn-mode-advanced').click()
        time.sleep(0.25)

        page.reload()
        page.wait_for_load_state('networkidle')
        assert page.evaluate("document.documentElement.getAttribute('data-ui-mode')") == 'advanced', \
            "Advanced mode should survive a reload"

        page.locator('#btn-mode-basic').click()
        time.sleep(0.25)

        page.reload()
        page.wait_for_load_state('networkidle')
        assert page.evaluate("document.documentElement.getAttribute('data-ui-mode')") == 'basic', \
            "Basic mode should survive a reload"

        browser.close()


def test_hidden_engine_tab_cannot_stay_selected_when_leaving_advanced(live_server):
    """Switching to Basic while an Advanced-only engine is active must not leave
    the search bar silently routing through an engine the user cannot see."""
    with sync_playwright() as p:
        browser, page = _page(p, mode='advanced')
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        page.locator('#search-mode-tabs .search-tab[data-mode="shodan"]').click()
        time.sleep(0.2)
        assert 'active' in page.locator(
            '#search-mode-tabs .search-tab[data-mode="shodan"]').get_attribute('class')

        page.locator('#btn-mode-basic').click()
        time.sleep(0.3)

        active_mode = page.eval_on_selector(
            '#search-mode-tabs .search-tab.active', "el => el.dataset.mode"
        )
        assert active_mode == 'filter', \
            f"Basic mode should fall back to the Filter engine, got {active_mode}"
        assert page.locator('#search-mode-tabs .search-tab.active').is_visible() is True

        browser.close()


@pytest.mark.parametrize("w,h,vp_name", VIEWPORTS)
def test_ui_modes_responsive(live_server, w, h, vp_name):
    with sync_playwright() as p:
        browser, page = _page(p, w=w, h=h)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        assert page.locator('#main-search').is_visible() is True, f"Search missing on {vp_name}"
        assert page.locator('#btn-nav-more').is_visible() is True, f"More Tools missing on {vp_name}"

        page.locator('#btn-nav-more').click()
        time.sleep(0.2)
        panel = page.locator('#nav-overflow-panel')
        assert panel.is_visible() is True, f"Overflow panel failed to open on {vp_name}"

        box = panel.bounding_box()
        assert box is not None, f"Overflow panel has no box on {vp_name}"
        assert box['x'] >= -1, f"Overflow panel overflows the left edge on {vp_name}: {box}"
        assert box['x'] + box['width'] <= w + 1, \
            f"Overflow panel overflows the right edge on {vp_name}: {box} (viewport {w})"

        browser.close()
