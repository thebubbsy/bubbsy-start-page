"""
E2E coverage for the `prefers-reduced-motion` accessibility support (WCAG 2.3.3).

Anyone with the OS-level "reduce motion" preference set should get an
effectively-instant page: no smooth scrolling, no lingering CSS transitions
or animations, and JS-driven scrollIntoView/scrollTo calls that request
'smooth' explicitly should fall back to 'auto' too.
"""

import pytest
from playwright.sync_api import sync_playwright


def _context(p, reduced_motion):
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(reduced_motion=reduced_motion)
    context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
    page = context.new_page()
    return browser, page


def test_reduced_motion_collapses_css_transitions_and_scroll_behavior(live_server):
    """With the OS preference set, transitions/animations shrink to ~instant."""
    with sync_playwright() as p:
        browser, page = _context(p, 'reduce')
        try:
            page.goto(live_server)
            page.wait_for_load_state('networkidle')

            html_scroll_behavior = page.evaluate(
                "getComputedStyle(document.documentElement).scrollBehavior"
            )
            assert html_scroll_behavior == 'auto'

            anchor = page.query_selector('.link-anchor')
            assert anchor is not None, "expected at least one rendered .link-anchor"
            transition_duration = page.evaluate(
                "getComputedStyle(document.querySelector('.link-anchor')).transitionDuration"
            )
            # Every comma-separated duration in the shorthand must be collapsed.
            for part in transition_duration.split(','):
                part = part.strip()
                assert part.endswith('ms') or part.endswith('s')
                value = float(part[:-2]) if part.endswith('ms') else float(part[:-1]) * 1000
                assert value <= 1.0, f"expected a near-zero transition duration, got {part}"
        finally:
            browser.close()


def test_no_motion_preference_keeps_original_transitions(live_server):
    """Without the reduced-motion preference, the normal (non-zero) durations apply."""
    with sync_playwright() as p:
        browser, page = _context(p, 'no-preference')
        try:
            page.goto(live_server)
            page.wait_for_load_state('networkidle')

            html_scroll_behavior = page.evaluate(
                "getComputedStyle(document.documentElement).scrollBehavior"
            )
            assert html_scroll_behavior == 'smooth'

            transition_duration = page.evaluate(
                "getComputedStyle(document.querySelector('.link-anchor')).transitionDuration"
            )
            durations_ms = []
            for part in transition_duration.split(','):
                part = part.strip()
                durations_ms.append(float(part[:-2]) if part.endswith('ms') else float(part[:-1]) * 1000)
            assert max(durations_ms) > 1.0, "expected the un-reduced transition duration to survive"
        finally:
            browser.close()


def test_motion_safe_behavior_helper_respects_the_media_query(live_server):
    """window.motionSafeBehavior() is the one place JS decides 'smooth' vs 'auto'."""
    with sync_playwright() as p:
        browser, page = _context(p, 'reduce')
        try:
            page.goto(live_server)
            page.wait_for_load_state('networkidle')
            assert page.evaluate("window.motionSafeBehavior('smooth')") == 'auto'
        finally:
            browser.close()

        browser2, page2 = _context(p, 'no-preference')
        try:
            page2.goto(live_server)
            page2.wait_for_load_state('networkidle')
            assert page2.evaluate("window.motionSafeBehavior('smooth')") == 'smooth'
        finally:
            browser2.close()
