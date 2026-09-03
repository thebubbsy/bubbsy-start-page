import pytest
import time
import json
from playwright.sync_api import sync_playwright

VIEWPORTS = [
    (1920, 1080, '1080p'),
    (1366, 768, 'Laptop'),
    (1024, 768, 'Tablet'),
    (390, 844, 'Mobile')
]

def test_ai_copilot_modal_and_prompt_synthesis(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        # 1. Open AI Copilot via Header button
        btn_copilot = page.locator('#btn-open-ai-copilot')
        assert btn_copilot.is_visible() is True, "btn-open-ai-copilot must be visible"
        btn_copilot.click()
        time.sleep(0.3)

        modal = page.locator('#modal-ai-copilot')
        assert modal.is_visible() is True, "AI Copilot modal should be open"

        # 2. Fill target and context
        target_input = page.locator('#ai-copilot-target')
        target_input.fill('CVE-2026-45659 SharePoint Deserialization')
        
        ctx_input = page.locator('#ai-copilot-context')
        ctx_input.fill('Observed IP 104.192.141.1 and target domain atlassian.com.au')

        # 3. Switch Recipe to 'person' and verify prompt preview updates
        page.locator('.ai-recipe-pill[data-recipe="person"]').click()
        time.sleep(0.1)
        preview = page.locator('#ai-copilot-prompt-preview')
        val = preview.input_value()
        assert 'Multi-Platform Digital Footprint & Persona Dossier' in val, f"Prompt should contain person recipe text, got: {val[:100]}"
        assert 'CVE-2026-45659' in val

        # 4. Switch Format to 'mitre'
        page.locator('.ai-format-pill[data-format="mitre"]').click()
        time.sleep(0.1)
        val_mitre = preview.input_value()
        assert 'MITRE ATT&CK Matrix Table' in val_mitre

        # 5. Test Send to Link Graph
        page.locator('#btn-ai-send-to-graph').click()
        time.sleep(0.3)
        assert page.locator('#modal-graph').is_visible() is True, "Should transition to Link Graph modal"

        browser.close()

def test_ai_copilot_bang_shortcut_trigger(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        # Type '!ai test_target' into main search
        search_input = page.locator('#main-search')
        search_input.fill('!ai test_target')
        time.sleep(0.3)

        modal = page.locator('#modal-ai-copilot')
        assert modal.is_visible() is True, "Typing !ai should automatically launch AI Copilot modal"
        assert page.locator('#ai-copilot-target').input_value() == 'test_target'

        browser.close()

def test_link_graph_38_layouts_and_minimap(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        page.locator('#btn-open-graph').click()
        time.sleep(0.3)
        modal_graph = page.locator('#modal-graph')
        assert modal_graph.is_visible() is True

        # Check mini-map canvas is rendered
        minimap = page.locator('#graph-minimap-canvas')
        assert minimap.is_visible() is True, "Mini-map canvas must be visible"

        # Load AU Template
        page.locator('#btn-graph-template').click()
        time.sleep(0.3)

        # Test Layout Switcher
        layout_select = page.locator('#graph-layout-mode')
        assert layout_select.is_visible() is True

        for mode in ['radial', 'tree', 'grid', 'force']:
            layout_select.select_option(mode)
            time.sleep(0.1)

        # Test Relationship selector
        rel_select = page.locator('#graph-edge-rel-type')
        assert rel_select.is_visible() is True
        rel_select.select_option('controls')

        # Test Export JSON button
        export_btn = page.locator('#btn-graph-export-json')
        assert export_btn.is_visible() is True

        browser.close()

def test_threat_radar_ai_brief_and_graph_dispatch(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        # Open Threat Radar
        page.locator('#btn-open-radar').click()
        time.sleep(0.3)
        assert page.locator('#modal-radar').is_visible() is True

        # Test AI Threat Brief Button -> Opens AI Copilot with context
        btn_brief = page.locator('#btn-radar-ai-brief')
        assert btn_brief.is_visible() is True, "btn-radar-ai-brief must be present"
        btn_brief.click()
        time.sleep(0.3)

        modal_copilot = page.locator('#modal-ai-copilot')
        assert modal_copilot.is_visible() is True, "AI Threat Brief should transition to AI Copilot"
        ctx = page.locator('#ai-copilot-context').input_value()
        assert 'ACTIVE RADAR ADVISORIES' in ctx

        # Close Copilot and reopen radar to test To Graph
        page.locator('#btn-close-ai-copilot').click()
        time.sleep(0.2)
        page.locator('#btn-open-radar').click()
        time.sleep(0.2)

        page.locator('#btn-radar-send-to-graph').click()
        time.sleep(0.3)
        assert page.locator('#modal-graph').is_visible() is True, "Radar send to graph should open Link Graph"

        browser.close()

@pytest.mark.parametrize("w,h,vp_name", VIEWPORTS)
def test_gemini_38_responsive(live_server, w, h, vp_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': w, 'height': h})
        context.add_init_script("localStorage.setItem('bubbsy_tour_seen', 'true'); localStorage.setItem('bubbsy_ui_mode', 'advanced');")
        page = context.new_page()
        page.goto(live_server)
        page.wait_for_load_state('networkidle')

        # Verify AI Copilot renders without layout errors
        page.evaluate("openAiCopilotModal('Test Subject', 'ttp');")
        time.sleep(0.2)
        copilot_modal = page.locator('#modal-ai-copilot')
        assert copilot_modal.is_visible() is True, f"AI Copilot failed to render in {vp_name}"
        page.locator('#btn-close-ai-copilot').click()
        time.sleep(0.1)

        # Verify Link Graph renders without layout errors
        page.evaluate("openInvestigationGraph();")
        time.sleep(0.2)
        graph_modal = page.locator('#modal-graph')
        assert graph_modal.is_visible() is True, f"Link Graph failed to render in {vp_name}"

        browser.close()
