"""
E2E coverage for the live search match count being announced to assistive
technology (WCAG 4.1.3 Status Messages).

The "N MATCHES" badge next to the search box updates on every keystroke, but
was a plain <span> with no live-region semantics - a screen reader user got
no feedback that filtering had happened or how many results remained. This
verifies the badge is exposed as a polite live region and that its announced
text actually tracks the match count, plus that the search input itself has
an accessible name (it previously relied on placeholder text alone).
"""

import time

from playwright.sync_api import sync_playwright


def _goto_and_wait_for_dashboard(page, live_server):
    page.goto(live_server)
    page.wait_for_selector('.link-anchor', timeout=15000)


def test_search_input_has_accessible_name(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
        page = context.new_page()
        try:
            _goto_and_wait_for_dashboard(page, live_server)
            search_input = page.locator('#main-search')
            aria_label = search_input.get_attribute('aria-label')
            assert aria_label and aria_label.strip(), \
                "#main-search must expose an accessible name (aria-label), not just a placeholder"
        finally:
            browser.close()


def test_match_count_badge_is_a_polite_live_region(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
        page = context.new_page()
        try:
            _goto_and_wait_for_dashboard(page, live_server)
            badge = page.locator('#search-live-matches')
            assert badge.get_attribute('aria-live') == 'polite'
            assert badge.get_attribute('role') == 'status'
            assert badge.get_attribute('aria-atomic') == 'true'
        finally:
            browser.close()


def test_match_count_text_updates_as_the_user_types(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
        page = context.new_page()
        try:
            _goto_and_wait_for_dashboard(page, live_server)
            search_input = page.locator('#main-search')
            badge = page.locator('#search-live-matches')

            # Before typing, the badge is hidden and carries no stale count.
            assert badge.is_visible() is False

            search_input.fill('shodan')
            time.sleep(0.2)
            assert badge.is_visible() is True
            first_text = badge.text_content()
            assert 'MATCH' in first_text

            # A query with zero results is still announced (0 MATCHES), not
            # silently swapped for the visual-only empty state.
            search_input.fill('nonexistent_tool_query_xyz999')
            time.sleep(0.2)
            assert badge.text_content() == '0 MATCHES'

            # Clearing the query hides the live region again.
            search_input.fill('')
            time.sleep(0.2)
            assert badge.is_visible() is False
        finally:
            browser.close()
