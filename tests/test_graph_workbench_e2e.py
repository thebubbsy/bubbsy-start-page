"""
E2E coverage for the investigation graph: typed shapes and legend, hover details, right-click
menu, the details panel, pinning, and named cases saved in the browser.
"""
import json

from playwright.sync_api import sync_playwright


def _open_graph(p, live_server):
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 900})
    context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true');")
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('dialog', lambda d: d.accept())
    page.goto(live_server)
    page.wait_for_selector('.widget-card')
    page.evaluate('openInvestigationGraph()')
    page.wait_for_selector('#modal-graph.active')
    page.click('#btn-graph-template')
    page.wait_for_timeout(1200)
    page.click('#btn-graph-fit')
    page.wait_for_timeout(200)
    return browser, page, errors


def _graph(page):
    return page.evaluate("JSON.parse(localStorage.getItem('bubbsy_investigation_graph'))")


def _pos(page, node_id):
    return page.evaluate(f"BubbsyGraph.screenPos('{node_id}')")


def test_legend_lists_each_type_with_its_own_shape(live_server):
    with sync_playwright() as p:
        browser, page, errors = _open_graph(p, live_server)
        types = page.eval_on_selector_all('.graph-legend-row', 'rows => rows.map(r => r.dataset.type)')
        assert set(types) == {'org', 'aus', 'domain', 'ip', 'cve'}
        # Clicking a legend row hides that type; clicking again shows it.
        page.click('.graph-legend-row[data-type="ip"]')
        page.wait_for_timeout(400)  # saves are debounced
        assert 'ip' in _graph(page)['hiddenTypes']
        page.click('.graph-legend-row[data-type="ip"]')
        page.wait_for_timeout(400)
        assert 'ip' not in _graph(page)['hiddenTypes']
        assert errors == []
        browser.close()


def test_hover_shows_entity_details_and_connections(live_server):
    with sync_playwright() as p:
        browser, page, errors = _open_graph(p, live_server)
        pos = _pos(page, 'n_dom')
        page.mouse.move(pos['x'], pos['y'])
        tooltip = page.locator('#graph-tooltip')
        tooltip.wait_for(state='visible')
        text = tooltip.inner_text()
        assert 'atlassian.com' in text
        assert '3 connections' in text
        assert 'resolves to' in text
        browser.close()


def test_right_click_menu_restyles_and_pins(live_server):
    with sync_playwright() as p:
        browser, page, errors = _open_graph(p, live_server)
        pos = _pos(page, 'n_ip')
        page.mouse.click(pos['x'], pos['y'], button='right')
        menu = page.locator('#graph-context-menu')
        menu.wait_for(state='visible')
        page.click('#graph-context-menu .gm-shape[data-value="star"]')
        page.wait_for_timeout(400)  # saves are debounced
        node = next(n for n in _graph(page)['nodes'] if n['id'] == 'n_ip')
        assert node['customShape'] == 'star'

        pos = _pos(page, 'n_ip')
        page.mouse.click(pos['x'], pos['y'], button='right')
        page.click('#graph-context-menu .gm-swatch[data-value="#facc15"]')
        page.keyboard.press('Escape')
        page.mouse.click(pos['x'], pos['y'], button='right')
        page.click('#graph-context-menu .gm-item[data-action="pin"]')
        page.wait_for_timeout(400)
        node = next(n for n in _graph(page)['nodes'] if n['id'] == 'n_ip')
        assert node['customColor'] == '#facc15'
        assert node['pinned'] is True
        assert errors == []
        browser.close()


def test_details_panel_edits_and_adds_linked_entity(live_server):
    with sync_playwright() as p:
        browser, page, errors = _open_graph(p, live_server)
        pos = _pos(page, 'n_org')
        page.mouse.click(pos['x'], pos['y'])
        panel = page.locator('#graph-detail-panel')
        panel.wait_for(state='visible')
        page.fill('#gd-notes', 'Parent company. Confirmed via ASIC.')
        page.fill('#gd-tags', 'confirmed, AU')
        page.fill('#gd-link-label', 'Jane Citizen')
        page.select_option('#gd-link-type', 'person')
        page.select_option('#gd-link-rel', 'employs')
        page.click('[data-gd="add-link"]')
        page.wait_for_timeout(600)
        g = _graph(page)
        org = next(n for n in g['nodes'] if n['id'] == 'n_org')
        jane = next(n for n in g['nodes'] if n['label'] == 'Jane Citizen')
        assert org['notes'] == 'Parent company. Confirmed via ASIC.'
        assert org['tags'] == ['confirmed', 'AU']
        assert jane['type'] == 'person'
        assert {'source': 'n_org', 'target': jane['id'], 'label': 'employs'} in [
            {k: e[k] for k in ('source', 'target', 'label')} for e in g['edges']]
        assert 'employs' in panel.inner_text()
        browser.close()


def test_dragging_a_node_pins_it_where_dropped(live_server):
    with sync_playwright() as p:
        browser, page, errors = _open_graph(p, live_server)
        pos = _pos(page, 'n_cve')
        page.mouse.move(pos['x'], pos['y'])
        page.mouse.down()
        page.mouse.move(pos['x'] + 120, pos['y'] - 60, steps=8)
        page.mouse.up()
        page.wait_for_timeout(1500)  # physics would pull an unpinned node back
        after = _pos(page, 'n_cve')
        assert abs(after['x'] - (pos['x'] + 120)) < 4 and abs(after['y'] - (pos['y'] - 60)) < 4
        assert next(n for n in _graph(page)['nodes'] if n['id'] == 'n_cve')['pinned'] is True
        browser.close()


def test_cases_are_kept_separately_and_survive_reload(live_server):
    with sync_playwright() as p:
        browser, page, errors = _open_graph(p, live_server)
        # The example opened as its own case; the original case is still there and untouched.
        cases = page.evaluate("JSON.parse(localStorage.getItem('bubbsy_graph_cases'))")
        assert len(cases['cases']) == 2
        assert cases['cases'][cases['activeId']]['name'] == 'AU template'

        page.reload()
        page.wait_for_selector('.widget-card')
        page.evaluate('openInvestigationGraph()')
        page.wait_for_selector('#modal-graph.active')
        names = page.eval_on_selector_all('#graph-case-select option', 'os => os.map(o => o.textContent)')
        assert 'AU template' in names
        assert len(_graph(page)['nodes']) == 5

        other = [cid for cid in cases['cases'] if cid != cases['activeId']][0]
        page.select_option('#graph-case-select', other)
        page.wait_for_timeout(300)
        assert len(_graph(page)['nodes']) != 5 or _graph(page)['nodes'][0]['id'] != 'n_org'
        browser.close()


def test_sign_in_button_explains_when_no_account_server(live_server):
    """Opened straight from disk there is no server: the button still shows and says why."""
    import os
    index = 'file://' + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(index)
        page.wait_for_selector('.widget-card')
        page.locator('#btn-account').wait_for(state='visible')
        page.click('#btn-account')
        assert page.locator('#account-unavailable').is_visible()
        assert page.locator('#account-signed-out').is_hidden()
        browser.close()
