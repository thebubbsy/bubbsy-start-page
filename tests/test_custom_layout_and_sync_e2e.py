"""
E2E coverage for the Newest and Custom catalogue orders, arrange mode, and optional account sync.

  Newest  - every module lists its most recently added tools first (dates from data/link_dates.js).
  Custom  - the user drags modules (between columns too) and links into their own order and saves.
  Account - optional; mirrors preferences to the server so a second computer gets the same layout.
"""
import json
import uuid

from playwright.sync_api import sync_playwright

SORT_KEY = 'bubbsy_sort_mode'
LAYOUT_KEY = 'bubbsy_custom_layout'


def _context(browser, sort=None, layout=None):
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    script = "if (!sessionStorage.getItem('seeded')) { sessionStorage.setItem('seeded','1'); localStorage.setItem('bubbsy_tour_seen', 'true');"
    if sort:
        script += f"localStorage.setItem('{SORT_KEY}', '{sort}');"
    if layout:
        script += f"localStorage.setItem('{LAYOUT_KEY}', {json.dumps(json.dumps(layout))});"
    script += "}"
    context.add_init_script(script)
    return context


def _open(context, url):
    page = context.new_page()
    page.goto(url)
    page.wait_for_selector('.widget-card')
    return page


def _column_ids(page):
    return page.eval_on_selector_all(
        '.column-stack',
        'cols => cols.map(c => Array.from(c.querySelectorAll(":scope > .widget-card")).map(w => w.dataset.widgetId))')


def test_newest_orders_links_by_added_date(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = _open(_context(browser, sort='newest'), live_server)
        assert page.locator('.sort-mode-btn.active').get_attribute('data-sort-mode') == 'newest'
        ok = page.evaluate('''() => {
          const dates = window.BUBBSY_LINK_DATES;
          return Array.from(document.querySelectorAll('.widget-card')).every(card => {
            const ts = Array.from(card.querySelectorAll('.link-anchor')).map(a => dates[a.getAttribute('href')] ?? Infinity);
            return ts.every((t, i) => i === 0 || ts[i - 1] >= t);
          });
        }''')
        assert ok, 'every module should list its newest links first'
        browser.close()


def test_custom_first_click_enters_arrange_mode_and_cancel_discards(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = _open(_context(browser), live_server)
        before = _column_ids(page)
        page.click('.sort-mode-btn[data-sort-mode="custom"]')
        assert page.locator('body.layout-editing').count() == 1
        assert page.locator('#layout-edit-bar').is_visible()
        assert page.locator('.module-handle').count() == page.locator('.widget-card').count()

        page.locator('.module-handle').first.focus()
        page.keyboard.press('ArrowDown')
        assert _column_ids(page) != before

        page.click('#btn-layout-cancel')
        assert page.locator('body.layout-editing').count() == 0
        assert page.locator('.drag-handle').count() == 0
        assert _column_ids(page) == before
        assert page.evaluate(f"localStorage.getItem('{LAYOUT_KEY}')") is None
        assert page.locator('.sort-mode-btn.active').get_attribute('data-sort-mode') == 'au'
        browser.close()


def test_keyboard_arrange_between_columns_saves_and_survives_reload(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = _open(_context(browser), live_server)
        page.click('.sort-mode-btn[data-sort-mode="custom"]')
        first_id = _column_ids(page)[0][0]
        page.locator(f'.widget-card[data-widget-id="{first_id}"] .module-handle').focus()
        page.keyboard.press('ArrowRight')  # into column 2
        page.keyboard.press('ArrowDown')
        # Reorder a link inside the module too.
        link_handles = page.locator(f'.widget-card[data-widget-id="{first_id}"] .link-handle')
        first_link = page.locator(f'.widget-card[data-widget-id="{first_id}"] .link-anchor').first.get_attribute('href')
        link_handles.first.focus()
        page.keyboard.press('ArrowDown')
        page.click('#btn-layout-save')

        assert page.locator('.sort-mode-btn.active').get_attribute('data-sort-mode') == 'custom'
        cols = _column_ids(page)
        assert first_id not in cols[0] and cols[1].index(first_id) == 1

        page.reload()
        page.wait_for_selector('.widget-card')
        cols = _column_ids(page)
        assert cols[1].index(first_id) == 1
        hrefs = page.eval_on_selector_all(f'.widget-card[data-widget-id="{first_id}"] .link-anchor', 'as => as.map(a => a.getAttribute("href"))')
        assert hrefs[1] == first_link
        assert page.locator('#btn-arrange-layout').is_visible()
        browser.close()


def test_mouse_drag_moves_a_module(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = _open(_context(browser), live_server)
        page.click('#btn-toggle-all-cards')  # collapsed cards are easier to drag
        page.click('.sort-mode-btn[data-sort-mode="custom"]')
        cols = _column_ids(page)
        moving, target = cols[0][0], cols[2][2]
        h = page.locator(f'.widget-card[data-widget-id="{moving}"] .module-handle').bounding_box()
        t = page.locator(f'.widget-card[data-widget-id="{target}"]').bounding_box()
        page.mouse.move(h['x'] + h['width'] / 2, h['y'] + h['height'] / 2)
        page.mouse.down()
        page.mouse.move(t['x'] + 40, t['y'] + 4, steps=12)
        page.mouse.up()
        page.click('#btn-layout-save')
        cols = _column_ids(page)
        assert moving in cols[2] and moving not in cols[0]
        browser.close()


def test_saved_layout_keeps_modules_it_does_not_know(live_server):
    """A layout saved before new modules shipped must not hide them."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = _open(_context(browser), live_server)
        au_cols = _column_ids(page)
        # Layout that only knows about one module, moved to the last column.
        layout = {'v': 1, 'base': 'au', 'columns': [[], [], [], [au_cols[0][0]]], 'links': {}}
        page.close()
        page = _open(_context(browser, sort='custom', layout=layout), live_server)
        cols = _column_ids(page)
        assert sorted(sum(cols, [])) == sorted(sum(au_cols, []))
        assert cols[3][0] == au_cols[0][0]
        browser.close()


def test_account_signup_syncs_layout_to_a_second_computer(live_server):
    email = f'e2e-{uuid.uuid4().hex[:10]}@example.com'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Computer 1: arrange, save, accept the sync offer, create an account.
        page = _open(_context(browser), live_server)
        assert page.locator('#btn-account').is_visible()
        page.click('.sort-mode-btn[data-sort-mode="custom"]')
        page.locator('.module-handle').first.focus()
        page.keyboard.press('ArrowRight')
        page.click('#btn-layout-save')
        page.click('.sync-offer-yes')
        assert page.locator('#modal-account.active').count() == 1
        assert 'all it does' in page.locator('.account-honest').inner_text()
        page.fill('#account-email', email)
        page.fill('#account-password', 'password123')
        page.click('#account-submit')
        page.wait_for_function("document.getElementById('account-btn-label').textContent === 'Synced'")
        page.wait_for_function("!!localStorage.getItem('bubbsy_prefs_synced_at')")
        layout_1 = _column_ids(page)

        # Computer 2: fresh browser, default order; signing in brings the layout across.
        page2 = _open(_context(browser), live_server)
        assert _column_ids(page2) != layout_1
        page2.click('#btn-account')
        page2.fill('#account-email', email)
        page2.fill('#account-password', 'password123')
        with page2.expect_navigation():
            page2.click('#account-submit')
        page2.wait_for_selector('.widget-card')
        assert page2.locator('.sort-mode-btn.active').get_attribute('data-sort-mode') == 'custom'
        assert _column_ids(page2) == layout_1
        browser.close()
