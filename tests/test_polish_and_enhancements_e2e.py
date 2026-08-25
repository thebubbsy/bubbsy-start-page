"""
Automated E2E Test Suite for Polish Enhancements:
- Floating Bang Autocomplete Dropdown
- Tactical Empty State with Quick Pivot Action Buttons
- Cyber Audio & Soundscape Settings State
- Micro-interactions & Zero-lag keyboard traversal
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

def test_bang_autocomplete_dropdown_and_keyboard_selection(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        search_input = page.locator('#main-search')
        dropdown = page.locator('#bang-autocomplete-dropdown')

        # 1. Type '!' to trigger autocomplete dropdown
        search_input.focus()
        search_input.fill('!')
        time.sleep(0.2)
        assert dropdown.is_visible() is True, "Bang autocomplete dropdown failed to appear on '!'"
        assert dropdown.locator('.bang-autocomplete-item').count() >= 5, "Dropdown should have multiple bang suggestions"

        # 2. Type '!trov' to narrow down to '!trove'
        search_input.fill('!trov')
        time.sleep(0.1)
        items = dropdown.locator('.bang-autocomplete-item')
        assert items.count() >= 1
        first_badge = items.first.locator('.bang-autocomplete-badge').text_content()
        assert first_badge == '!trove', f"Expected '!trove', got {first_badge}"

        # 3. Test keyboard arrow navigation: ArrowDown -> select first item
        search_input.press('ArrowDown')
        time.sleep(0.1)
        assert 'selected' in items.first.get_attribute('class'), "First item should have 'selected' class on ArrowDown"

        # 4. Press Tab to commit autocomplete
        search_input.press('Tab')
        time.sleep(0.2)
        assert dropdown.is_visible() is False, "Dropdown should hide after tab selection"

        # 5. Type '!rad' and click item with mouse
        search_input.fill('!rad')
        time.sleep(0.2)
        assert dropdown.is_visible() is True
        dropdown.locator('.bang-autocomplete-item').first.click()
        time.sleep(0.3)
        assert page.locator('#modal-radar').is_visible() is True, "Selecting !radar should open Threat Radar modal"

        browser.close()

def test_tactical_empty_state_and_clear_action(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        search_input = page.locator('#main-search')

        # 1. Search for a nonexistent query
        search_input.fill('nonexistent_tool_query_xyz999')
        time.sleep(0.3)

        empty_state = page.locator('.tactical-empty-state')
        assert empty_state.is_visible() is True, "Tactical empty state card failed to appear on 0 matches"
        assert "NO LOCAL OSINT INTEL MATCHES" in empty_state.locator('.empty-title').text_content()

        # 2. Check quick action buttons exist
        assert empty_state.locator('#btn-empty-google').is_visible() is True
        assert empty_state.locator('#btn-empty-shodan').is_visible() is True
        assert empty_state.locator('#btn-empty-abn').is_visible() is True
        assert empty_state.locator('#btn-empty-dorks').is_visible() is True
        assert empty_state.locator('#btn-empty-clear').is_visible() is True

        # 3. Click Clear Filter button
        empty_state.locator('#btn-empty-clear').click()
        time.sleep(0.2)
        assert search_input.input_value() == "", "Search input should be cleared"
        assert empty_state.count() == 0, "Empty state should be removed once filter is cleared"
        assert page.locator('.widget-card').count() >= 10, "Widget cards should be visible again"

        browser.close()

def test_sound_effects_settings_configuration(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        # 1. Open Settings modal
        page.locator('#btn-settings').click()
        time.sleep(0.3)

        settings_modal = page.locator('#modal-settings')
        assert settings_modal.is_visible() is True

        sound_cb = page.locator('#cfg-sound-effects')
        assert sound_cb.is_visible() is True
        assert sound_cb.is_checked() is True, "Sound effects should default to checked"

        # 2. Uncheck and save
        sound_cb.uncheck()
        page.locator('#btn-save-settings').click()
        time.sleep(0.3)

        # 3. Verify in localStorage
        sound_setting = page.evaluate("() => JSON.parse(localStorage.getItem('bubbsy_settings')).soundEffects")
        assert sound_setting is False, f"soundEffects in localStorage should be false, got {sound_setting}"

        browser.close()

@pytest.mark.parametrize("w,h,vp_name", VIEWPORTS)
def test_polish_elements_responsive(live_server, w, h, vp_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': w, 'height': h})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        search_input = page.locator('#main-search')
        search_input.fill('!')
        time.sleep(0.2)
        dropdown = page.locator('#bang-autocomplete-dropdown')
        assert dropdown.is_visible() is True, f"Bang dropdown not visible on {vp_name}"

        browser.close()
