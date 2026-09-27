"""
Guards for the public, hosted site:
  - no endpoints that only make sense on the owner's own PC (opening files, local file search,
    a shared bookmarks file any visitor could overwrite);
  - no invented claims or hand-typed counts in the page;
  - the Settings status box reports real state;
  - bookmarks added with "Add" survive a reload.
"""
import os
import re
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _status(url, data=None):
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def test_local_pc_only_endpoints_are_gone(live_server):
    for path in ('/api/es/status', '/api/es/search?q=x&http_url=http://169.254.169.254', '/api/bookmarks', '/api/manifest'):
        assert _status(live_server + path) == 404 or _status(live_server + path) >= 400, path
    assert _status(live_server + '/api/es/open', b'{"path": "/etc/passwd"}') == 404
    assert _status(live_server + '/api/bookmarks', b'{"custom_bookmarks": []}') == 404


def test_page_has_no_invented_claims_or_hand_typed_counts():
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    js = open(os.path.join(ROOT, 'js', 'app.js'), encoding='utf-8').read()
    for text in (html, js):
        assert 'Port 7777' not in text
        assert not re.search(r'Gemini 3\.8', text, re.I)
        assert 'Essential 8 Verified' not in text and 'ML3 privacy' not in text
        assert 'ACTIVE 2026' not in text
    assert '2,061' not in html


def test_settings_status_reports_real_state(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
        page.goto(live_server)
        page.wait_for_selector('.widget-card')
        page.wait_for_function("document.getElementById('account-btn-label') && !document.getElementById('btn-account').hidden")
        page.evaluate('openSettingsModal()')
        box = page.inner_text('#settings-diagnostics-box')
        assert 'Connected' in box
        tools = page.evaluate("BUBBSY_DATA.columns.reduce((s,c)=>s+c.widgets.reduce((a,w)=>a+w.links.length,0),0)")
        assert f'{tools:,} tools' in box
        assert page.inner_text('#stats-total-tools') == f'{tools:,}'

        # Opened from a file there is no server, and the box says so.
        page.goto('file://' + os.path.join(ROOT, 'index.html'))
        page.wait_for_selector('.widget-card')
        page.evaluate('openSettingsModal()')
        assert 'Not running' in page.inner_text('#settings-diagnostics-box')
        browser.close()


def test_added_bookmark_survives_reload(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
        page.goto(live_server)
        page.wait_for_selector('.widget-card')
        page.evaluate("document.getElementById('btn-custom-bookmark').click()")
        page.fill('#bm-title', 'My Custom Tool')
        page.fill('#bm-url', 'https://my-custom-tool.example/')
        page.evaluate("document.getElementById('form-custom-bookmark').requestSubmit()")
        page.wait_for_selector('.link-anchor[href="https://my-custom-tool.example/"]')
        page.reload()
        page.wait_for_selector('.widget-card')
        assert page.locator('.link-anchor[href="https://my-custom-tool.example/"]').count() == 1
        browser.close()


def test_no_modal_is_nested_inside_another():
    """A merge once dropped a popup's closing tags, trapping the Sign in window inside a hidden one."""
    from html.parser import HTMLParser
    void = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}

    class Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.stack, self.nested = [], []

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            is_modal = 'modal-overlay' in (a.get('class') or '').split()
            if is_modal and any(m for _, m in self.stack):
                self.nested.append((a.get('id'), [m for _, m in self.stack if m][-1]))
            if tag not in void:
                self.stack.append((tag, a.get('id') if is_modal else None))

        def handle_endtag(self, tag):
            if tag in void:
                return
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break

    p = Parser()
    p.feed(open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read())
    assert p.nested == []
