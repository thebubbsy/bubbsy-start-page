"""
E2E coverage for the catalogue order modes.

Three orders share one control in the category ribbon:

  AU First  - the shipped Australian-first order. [AUS] modules sit high in each column and
              `au` links sit at the top of each module. This is the default and the only mode
              that reflects data/osint_data.json verbatim.
  A-Z       - straight alphabetical, Australian priority off.
  My Picks  - pinned tools first, alphabetical underneath.

The sort happens at render time on a copy, so switching back to AU First must restore the
shipped order exactly - that is the property most of these tests are really protecting.
"""

import pytest
from playwright.sync_api import sync_playwright

SORT_KEY = 'bubbsy_sort_mode'


def _page(p, w=1366, h=768, mode=None, sort=None, favorites=None):
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': w, 'height': h})
    script = "localStorage.setItem('bubbsy_tour_seen', 'true');"
    if mode:
        script += f"localStorage.setItem('bubbsy_ui_mode', '{mode}');"
    if sort:
        script += f"localStorage.setItem('{SORT_KEY}', '{sort}');"
    if favorites:
        script += f"localStorage.setItem('bubbsy_favorites', '{favorites}');"
    context.add_init_script(script)
    page = context.new_page()
    return browser, page


def _module_titles(page):
    return page.eval_on_selector_all(
        '.widget-card .widget-title', 'els => els.map(e => e.textContent.trim())'
    )


def _sortable(title):
    """Mirror of sortableTitle() in app.js - strip the [AUS] prefix before comparing."""
    t = title.strip()
    if t.upper().startswith('[AUS]'):
        t = t[5:].strip()
    return t.lower()


def test_au_first_is_the_default(live_server):
    """No stored preference means the shipped Australian-first order, untouched."""
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        active = page.locator('.sort-mode-btn.active')
        assert active.count() == 1
        assert active.get_attribute('data-sort-mode') == 'au'

        browser.close()


def test_control_is_visible_in_both_interface_modes(live_server):
    """Reading order matters in Basic too, so the control is not data-adv."""
    for ui_mode in ('basic', 'advanced'):
        with sync_playwright() as p:
            browser, page = _page(p, mode=ui_mode)
            page.goto(live_server)
            page.wait_for_load_state('networkidle')

            assert page.locator('#sort-mode-group').is_visible() is True, \
                f"order control should be visible in {ui_mode} mode"
            assert page.locator('.sort-mode-btn').count() == 3

            browser.close()


def test_az_sorts_modules_alphabetically_within_each_column(live_server):
    """A-Z must sort on the real subject, not on the '[' of the [AUS] prefix."""
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        page.click('.sort-mode-btn[data-sort-mode="az"]')
        page.wait_for_timeout(300)

        columns = page.eval_on_selector_all(
            '.column-stack',
            'cols => cols.map(c => Array.from(c.querySelectorAll(".widget-title"))'
            '.map(t => t.textContent.trim()))'
        )
        assert any(len(c) > 1 for c in columns), "expected populated columns"

        for idx, titles in enumerate(columns):
            keys = [_sortable(t) for t in titles]
            assert keys == sorted(keys), f"column {idx} is not alphabetical: {titles[:5]}"

        browser.close()


def test_az_does_not_leave_aus_modules_bunched_at_the_top(live_server):
    """Regression guard: an ASCII sort would put every [AUS] module first and look like AU mode."""
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        page.click('.sort-mode-btn[data-sort-mode="az"]')
        page.wait_for_timeout(300)

        flags = page.eval_on_selector_all(
            '.column-stack',
            'cols => cols.map(c => Array.from(c.querySelectorAll(".widget-card"))'
            '.map(w => w.getAttribute("data-au-module") === "1"))'
        )
        bunched = 0
        for col in flags:
            if len(col) > 3 and col[0] and all(col[:min(3, len(col))]):
                bunched += 1
        assert bunched < len([c for c in flags if len(c) > 3]), \
            "every column still leads with [AUS] modules - the prefix is not being stripped"

        browser.close()


def test_my_picks_floats_pinned_links_to_the_top_of_their_module(live_server):
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        # Pin a link that is not already first in its module.
        target = page.evaluate("""() => {
            const cards = document.querySelectorAll('.widget-card');
            for (const c of cards) {
                const items = c.querySelectorAll('.link-item');
                if (items.length > 3) {
                    const li = items[items.length - 1];
                    return {
                        widget: c.getAttribute('data-widget-id'),
                        title: li.querySelector('.link-title').textContent.trim(),
                        url: li.getAttribute('data-link-url')
                    };
                }
            }
            return null;
        }""")
        assert target, "needed a module with more than three links"

        page.evaluate(
            """(t) => localStorage.setItem('bubbsy_favorites',
                   JSON.stringify([{ id: 1, title: t.title, url: t.url, description: '' }]))""",
            target,
        )
        page.reload()
        page.wait_for_load_state('networkidle')
        page.click('.sort-mode-btn[data-sort-mode="picks"]')
        page.wait_for_timeout(300)

        first = page.evaluate(
            """(w) => {
                const c = document.querySelector(`.widget-card[data-widget-id="${w}"]`);
                if (!c) return null;
                const li = c.querySelector('.link-item .link-title');
                return li ? li.textContent.trim() : null;
            }""",
            target['widget'],
        )
        assert first == target['title'], \
            f"pinned link should lead its module, got {first!r} not {target['title']!r}"

        browser.close()


def test_switching_back_to_au_restores_the_shipped_order(live_server):
    """The whole design rests on the shipped data never being mutated in place."""
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        original = _module_titles(page)

        page.click('.sort-mode-btn[data-sort-mode="az"]')
        page.wait_for_timeout(300)
        assert _module_titles(page) != original, "A-Z should have changed the order"

        page.click('.sort-mode-btn[data-sort-mode="picks"]')
        page.wait_for_timeout(300)

        page.click('.sort-mode-btn[data-sort-mode="au"]')
        page.wait_for_timeout(300)
        assert _module_titles(page) == original, \
            "AU First must restore the shipped order exactly after round-tripping"

        browser.close()


def test_choice_persists_across_reload(live_server):
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        page.click('.sort-mode-btn[data-sort-mode="az"]')
        page.wait_for_timeout(300)

        page.reload()
        page.wait_for_load_state('networkidle')

        stored = page.evaluate(f"localStorage.getItem('{SORT_KEY}')")
        assert stored == 'az'
        assert page.locator('.sort-mode-btn.active').get_attribute('data-sort-mode') == 'az'

        browser.close()


def test_unknown_stored_mode_falls_back_to_au(live_server):
    """A hand-edited or stale localStorage value must not blank the dashboard."""
    with sync_playwright() as p:
        browser, page = _page(p, sort='not-a-real-mode')
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        assert page.locator('.sort-mode-btn.active').get_attribute('data-sort-mode') == 'au'
        assert page.locator('.widget-card').count() > 0, "dashboard should still render"

        browser.close()


def test_no_links_or_modules_are_lost_when_reordering(live_server):
    """Re-ordering must be a permutation - never a filter."""
    with sync_playwright() as p:
        browser, page = _page(p)
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        def counts():
            return page.evaluate(
                "() => [document.querySelectorAll('.widget-card').length,"
                " document.querySelectorAll('.link-item').length]"
            )

        baseline = counts()
        assert baseline[0] > 0 and baseline[1] > 0

        for mode in ('az', 'picks', 'au'):
            page.click(f'.sort-mode-btn[data-sort-mode="{mode}"]')
            page.wait_for_timeout(300)
            assert counts() == baseline, f"{mode} changed the number of modules/links"

        browser.close()
