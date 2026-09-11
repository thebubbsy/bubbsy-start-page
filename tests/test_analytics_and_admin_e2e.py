import pytest
import time
import json
import base64
import urllib.request
import urllib.error
from playwright.sync_api import sync_playwright

def test_api_track_endpoint(live_server):
    track_url = f"{live_server}/api/track"
    payload = {
        "session_id": "test_sess_py_01",
        "element_tag": "BUTTON",
        "element_id": "btn-test-action",
        "element_classes": "btn-icon active",
        "element_text": "CISA KEV Radar Test",
        "target_href": "https://cisa.gov/test",
        "page_path": "/#radar",
        "timestamp": "2026-09-11T05:00:00.000Z"
    }

    req = urllib.request.Request(
        track_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode('utf-8'))
        assert data.get('success') is True

def test_admin_analytics_auth_checks(live_server):
    analytics_url = f"{live_server}/api/admin/analytics"

    # 1. Unauthorized request
    req_no_auth = urllib.request.Request(analytics_url)
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(req_no_auth)
    assert exc_info.value.code == 401

    # 2. Bad credentials
    bad_auth = base64.b64encode(b"wrong:creds").decode('ascii')
    req_bad_auth = urllib.request.Request(analytics_url, headers={'Authorization': f'Basic {bad_auth}'})
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(req_bad_auth)
    assert exc_info.value.code == 401

    # 3. Valid credentials (user:hacker)
    valid_auth = base64.b64encode(b"user:hacker").decode('ascii')
    req_valid = urllib.request.Request(analytics_url, headers={'Authorization': f'Basic {valid_auth}'})
    with urllib.request.urlopen(req_valid) as response:
        assert response.status == 200
        data = json.loads(response.read().decode('utf-8'))
        assert data.get('authorized') is True
        assert 'summary' in data
        assert 'clicks' in data
        assert isinstance(data['clicks'], list)
        assert data['summary']['total_clicks'] >= 1

def test_admin_modal_ui_e2e(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        # 1. Click a few buttons to generate real client-side telemetry
        page.locator('#btn-theme-picker').click()
        time.sleep(0.1)
        page.locator('#btn-open-export').click()
        time.sleep(0.1)
        page.locator('#btn-close-export').click()
        time.sleep(0.2)

        # 2. Open Admin Modal via header button
        btn_admin = page.locator('#btn-open-admin')
        assert btn_admin.is_visible() is True, "btn-open-admin must be visible in header toolbar"
        btn_admin.click()
        time.sleep(0.2)

        modal_admin = page.locator('#modal-admin')
        assert modal_admin.is_visible() is True, "Admin modal should be open"
        assert page.locator('#admin-login-view').is_visible() is True

        # 3. Test invalid login
        page.locator('#admin-username').fill('user')
        page.locator('#admin-password').fill('wrongpassword')
        page.locator('#btn-admin-login-submit').click()
        time.sleep(0.2)
        assert page.locator('#admin-login-error').is_visible() is True

        # 4. Test valid login (user / hacker)
        page.locator('#admin-password').fill('hacker')
        page.locator('#btn-admin-login-submit').click()
        time.sleep(0.3)

        assert page.locator('#admin-dashboard-view').is_visible() is True, "Dashboard view should display after valid login"
        assert page.locator('#admin-login-view').is_visible() is False

        # 5. Verify Metric Cards and Table
        metric_clicks = page.locator('#admin-metric-total-clicks')
        assert metric_clicks.is_visible() is True

        tbody = page.locator('#admin-clicks-tbody')
        assert tbody.is_visible() is True

        rows = page.locator('.telemetry-row')
        assert rows.count() >= 1, "Should have rendered telemetry rows from clicks"

        # 6. Test Filter input
        filter_input = page.locator('#admin-filter-input')
        filter_input.fill('export')
        time.sleep(0.1)

        # 7. Test Logout
        page.locator('#btn-admin-logout').click()
        time.sleep(0.2)
        assert page.locator('#admin-login-view').is_visible() is True

        browser.close()

def test_admin_bang_shortcut(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        # Type '!admin' into main search bar
        search_input = page.locator('#main-search')
        search_input.fill('!admin')
        time.sleep(0.3)

        assert page.locator('#modal-admin').is_visible() is True, "!admin bang should launch admin modal"

        browser.close()
