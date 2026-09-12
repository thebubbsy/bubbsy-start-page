import pytest, urllib.request
from playwright.sync_api import sync_playwright

def test_ge_button_opens_modal(live_server):
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={'width': 1366, 'height': 768})
        ctx.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        pg = ctx.new_page()
        pg.goto(live_server, wait_until='networkidle')
        assert pg.locator('#btn-open-gods-eye').count() == 1
        pg.locator('#btn-open-gods-eye').click()
        pg.wait_for_timeout(500)
        assert pg.locator('#modal-gods-eye').is_visible()
        b.close()

def test_ge_bang_shortcut(live_server):
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={'width': 1366, 'height': 768})
        ctx.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        pg = ctx.new_page()
        pg.goto(live_server, wait_until='networkidle')
        pg.locator('#main-search').click()
        pg.keyboard.type('!eye')
        pg.keyboard.press('Enter')
        pg.wait_for_timeout(600)
        assert pg.locator('#modal-gods-eye').is_visible()
        b.close()

def test_ge_state_tiles(live_server):
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={'width': 1366, 'height': 768})
        ctx.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        pg = ctx.new_page()
        pg.goto(live_server, wait_until='networkidle')
        pg.locator('#btn-open-gods-eye').click()
        pg.wait_for_timeout(600)
        tiles = pg.locator('.ge-state-tile')
        assert tiles.count() == 8
        rendered = [tiles.nth(i).locator('.ge-state-abbr').inner_text().strip() for i in range(8)]
        for s in ['NSW','VIC','QLD','WA','SA','TAS','ACT','NT']: assert s in rendered
        b.close()

def test_ge_hud_chip(live_server):
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={'width': 1366, 'height': 768})
        ctx.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        pg = ctx.new_page()
        pg.goto(live_server, wait_until='networkidle')
        chips = pg.locator('.hud-key')
        texts = [chips.nth(i).inner_text().strip() for i in range(chips.count())]
        assert '!eye' in texts
        b.close()

def test_ge_close_button(live_server):
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={'width': 1366, 'height': 768})
        ctx.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        pg = ctx.new_page()
        pg.goto(live_server, wait_until='networkidle')
        pg.locator('#btn-open-gods-eye').click()
        pg.wait_for_timeout(400)
        pg.locator('#btn-close-gods-eye').click()
        pg.wait_for_timeout(300)
        assert not pg.locator('#modal-gods-eye').is_visible()
        b.close()

def test_ge_stat_ids_in_html(live_server):
    with urllib.request.urlopen(live_server + '/', timeout=5) as r:
        html = r.read().decode()
    for sid in ['ge-stat-abns','ge-stat-acsc','ge-stat-austlii','ge-stat-asic']: assert sid in html
