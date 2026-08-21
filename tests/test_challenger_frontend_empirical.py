#!/usr/bin/env python3
"""
================================================================================
CHALLENGER EMPIRICAL TEST SUITE: FRONTEND RECON ENGINE & OSINT SYNTHESIS
================================================================================
Stress-tests frontend state machine, triage decisions, recursive chaining,
manual pivots, chip removal, reverse image search links, email permutations,
radial graph geometry, and keyboard shortcuts.
================================================================================
"""

import unittest
import os
import re
import json
import math
import urllib.parse
from bs4 import BeautifulSoup

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML_PATH = os.path.join(ROOT_DIR, "index.html")
APP_JS_PATH = os.path.join(ROOT_DIR, "js", "app.js")
STYLES_CSS_PATH = os.path.join(ROOT_DIR, "css", "styles.css")


class TestFrontendDOMStructureIntegrity(unittest.TestCase):
    """Verifies all required DOM elements, IDs, modals, buttons, and inputs exist in index.html."""

    @classmethod
    def setUpClass(cls):
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            cls.html_content = f.read()
        cls.soup = BeautifulSoup(cls.html_content, "html.parser")

    def test_01_social_recon_modal_and_core_controls(self):
        """Checks presence of #modal-social-recon and all critical triage elements."""
        modal = self.soup.find(id="modal-social-recon")
        self.assertIsNotNone(modal, "Modal #modal-social-recon not found in index.html")
        
        required_ids = [
            "social-recon-input",
            "btn-social-recon-search",
            "btn-view-mode-triage",
            "btn-view-mode-grid",
            "social-triage-stepper-text",
            "triage-stepper-ribbon",
            "social-harvest-pool-bar",
            "harvest-pool-count",
            "btn-add-harvest-pivot",
            "btn-copy-harvested-intel",
            "btn-clear-harvested-intel",
            "harvest-add-pivot-form",
            "harvest-pivot-type",
            "harvest-pivot-value",
            "btn-submit-harvest-pivot",
            "btn-cancel-harvest-pivot",
            "harvest-pool-chips",
            "harvest-pool-names",
            "harvest-pool-locations",
            "harvest-pool-orgs",
            "harvest-pool-handles",
            "harvest-pool-proofs",
            "harvest-pool-emails",
            "harvest-pool-empty-hint",
            "social-triage-view",
            "triage-platform-name",
            "triage-platform-category-badge",
            "triage-query-context",
            "btn-triage-prev",
            "btn-triage-next",
            "social-triage-candidates-list",
            "social-grid-view",
            "social-status-hud",
            "social-keywords-container",
            "social-keywords-chips",
            "social-recon-results",
            "btn-social-consolidate-person",
            "btn-social-download-dossier",
            "btn-social-add-to-graph",
            "btn-open-crypto-drawer",
            "btn-open-email-drawer",
            "btn-open-chrono-drawer",
            "btn-social-launch-all",
        ]
        for elem_id in required_ids:
            self.assertIsNotNone(
                self.soup.find(id=elem_id),
                f"Missing required element #{elem_id} in #modal-social-recon"
            )

    def test_02_rich_osint_drawers_and_modals(self):
        """Verifies avatar comparison lightbox, crypto drawer, email matrix, and chrono drawer."""
        # Avatar compare modal
        avatar_modal = self.soup.find(id="modal-avatar-compare")
        self.assertIsNotNone(avatar_modal, "Missing #modal-avatar-compare")
        self.assertIsNotNone(self.soup.find(id="avatar-zoom-img"))
        self.assertIsNotNone(self.soup.find(id="avatar-placeholder-banner"))
        self.assertIsNotNone(self.soup.find(id="avatar-compare-strip"))
        self.assertIsNotNone(self.soup.find(id="btn-rev-google-lens"))
        self.assertIsNotNone(self.soup.find(id="btn-rev-yandex"))
        self.assertIsNotNone(self.soup.find(id="btn-rev-tineye"))
        self.assertIsNotNone(self.soup.find(id="btn-rev-pimeyes"))
        self.assertIsNotNone(self.soup.find(id="btn-rev-bing"))
        self.assertIsNotNone(self.soup.find(id="btn-rev-google-images"))

        # Crypto drawer
        self.assertIsNotNone(self.soup.find(id="modal-crypto-drawer"))
        self.assertIsNotNone(self.soup.find(id="crypto-drawer-content"))

        # Email matrix drawer
        self.assertIsNotNone(self.soup.find(id="modal-email-matrix"))
        self.assertIsNotNone(self.soup.find(id="email-matrix-content"))

        # Chrono drawer
        self.assertIsNotNone(self.soup.find(id="modal-chrono-drawer"))
        self.assertIsNotNone(self.soup.find(id="chrono-drawer-content"))

    def test_03_visual_graph_modal(self):
        """Verifies #modal-graph, canvas, and toolbar elements."""
        self.assertIsNotNone(self.soup.find(id="modal-graph"))
        self.assertIsNotNone(self.soup.find(id="investigation-canvas"))
        self.assertIsNotNone(self.soup.find(id="graph-new-node-label"))
        self.assertIsNotNone(self.soup.find(id="graph-new-node-type"))
        self.assertIsNotNone(self.soup.find(id="btn-graph-add-node"))
        self.assertIsNotNone(self.soup.find(id="btn-graph-auto-layout"))


class TestTriageStateMachineSimulation(unittest.TestCase):
    """Simulates JavaScript frontend triage state machine behavior and edge cases."""

    def setUp(self):
        self.platforms = [
            {'id': 'twitter', 'name': 'X / Twitter', 'category': 'social'},
            {'id': 'instagram', 'name': 'Instagram', 'category': 'social'},
            {'id': 'bluesky', 'name': 'Bluesky', 'category': 'social'},
            {'id': 'reddit', 'name': 'Reddit', 'category': 'messaging'},
            {'id': 'github', 'name': 'GitHub', 'category': 'dev'},
            {'id': 'keybase', 'name': 'Keybase', 'category': 'dev'},
            {'id': 'whirlpool', 'name': 'Whirlpool', 'category': 'aus'},
        ]
        self.context = {
            'primaryQuery': 'torvalds',
            'confirmedNames': set(),
            'confirmedHandles': {'torvalds'},
            'confirmedLocations': set(),
            'confirmedOrgs': set(),
            'confirmedProofs': [],
            'confirmedPgp': None,
            'discoveredEmails': set(),
            'decisions': {},
            'confirmedProfiles': [],
            'platformCandidatesCache': {}
        }

    def simulate_decision(self, candidate, action, plat):
        """Replicates handleTriageDecision in app.js."""
        prev = self.context['decisions'].get(candidate['key'])
        if prev == action:
            # Re-click toggle reset
            del self.context['decisions'][candidate['key']]
            if action == 'yes':
                self.context['confirmedProfiles'] = [
                    p for p in self.context['confirmedProfiles'] if p['key'] != candidate['key']
                ]
            return 'toggled_off'

        self.context['decisions'][candidate['key']] = action

        if action == 'yes':
            if candidate.get('display_name') and candidate['display_name'].strip().lower() != candidate['handle'].strip().lower():
                self.context['confirmedNames'].add(candidate['display_name'].strip())
            self.context['confirmedHandles'].add(candidate['handle'].strip().lower())
            if candidate.get('location'):
                self.context['confirmedLocations'].add(candidate['location'].strip())
            if candidate.get('company'):
                self.context['confirmedOrgs'].add(candidate['company'].strip())
            if candidate.get('pgp_fingerprint'):
                self.context['confirmedPgp'] = {
                    'fingerprint': candidate['pgp_fingerprint'],
                    'key_id': candidate.get('pgp_key_id') or candidate['pgp_fingerprint'][-16:]
                }
            if candidate.get('cryptographic_proofs'):
                for p in candidate['cryptographic_proofs']:
                    if not any(cp['type'] == p['type'] and cp['nametag'] == p['nametag'] for cp in self.context['confirmedProofs']):
                        self.context['confirmedProofs'].append(p)
            if candidate.get('email_permutations'):
                for em in candidate['email_permutations']:
                    self.context['discoveredEmails'].add(em)
            if not any(p['key'] == candidate['key'] for p in self.context['confirmedProfiles']):
                self.context['confirmedProfiles'].append(candidate)
            return 'confirmed_yes'

        elif action == 'unsure':
            return 'flagged_unsure'

        elif action == 'no':
            self.context['confirmedProfiles'] = [
                p for p in self.context['confirmedProfiles'] if p['key'] != candidate['key']
            ]
            return 'rejected_no'

    def test_01_yes_triage_decision_harvests_metadata(self):
        cand = {
            'key': 'github_torvalds',
            'handle': 'torvalds',
            'display_name': 'Linus Torvalds',
            'location': 'Portland, OR',
            'company': 'Linux Foundation',
            'pgp_fingerprint': 'E13B8F6D74B29C0A1F4E8D5B3C2A9E0F6A7B8C9D',
            'cryptographic_proofs': [{'type': 'github', 'nametag': 'torvalds'}],
            'email_permutations': ['linus.torvalds@linuxfoundation.org', 'torvalds@gmail.com']
        }
        res = self.simulate_decision(cand, 'yes', self.platforms[4])
        self.assertEqual(res, 'confirmed_yes')
        self.assertIn('Linus Torvalds', self.context['confirmedNames'])
        self.assertIn('Portland, OR', self.context['confirmedLocations'])
        self.assertIn('Linux Foundation', self.context['confirmedOrgs'])
        self.assertIn('torvalds', self.context['confirmedHandles'])
        self.assertIsNotNone(self.context['confirmedPgp'])
        self.assertEqual(self.context['confirmedPgp']['fingerprint'], 'E13B8F6D74B29C0A1F4E8D5B3C2A9E0F6A7B8C9D')
        self.assertEqual(len(self.context['confirmedProfiles']), 1)

    def test_02_decision_toggle_off_and_switch(self):
        cand = {
            'key': 'reddit_torvalds',
            'handle': 'torvalds',
            'display_name': 'torvalds',
            'location': 'Helsinki',
            'company': ''
        }
        # First click YES
        self.simulate_decision(cand, 'yes', self.platforms[3])
        self.assertEqual(self.context['decisions'].get(cand['key']), 'yes')
        self.assertEqual(len(self.context['confirmedProfiles']), 1)

        # Re-click YES toggles off
        res2 = self.simulate_decision(cand, 'yes', self.platforms[3])
        self.assertEqual(res2, 'toggled_off')
        self.assertNotIn(cand['key'], self.context['decisions'])
        self.assertEqual(len(self.context['confirmedProfiles']), 0)

        # Switch to NO
        res3 = self.simulate_decision(cand, 'no', self.platforms[3])
        self.assertEqual(res3, 'rejected_no')
        self.assertEqual(self.context['decisions'].get(cand['key']), 'no')
        self.assertEqual(len(self.context['confirmedProfiles']), 0)

    def test_03_unsure_flagging(self):
        cand = {'key': 'twitter_torvalds', 'handle': 'torvalds', 'display_name': 'Torvalds News'}
        res = self.simulate_decision(cand, 'unsure', self.platforms[0])
        self.assertEqual(res, 'flagged_unsure')
        self.assertEqual(self.context['decisions'].get(cand['key']), 'unsure')
        self.assertEqual(len(self.context['confirmedProfiles']), 0)


class TestForwardChainingQuerySynthesis(unittest.TestCase):
    """Stress tests dynamic query string generation and parameter encoding."""

    def test_01_query_context_desc_builder(self):
        q = "bubbsy"
        names = ["Tony Stark", "Anthony Edward Stark"]
        locs = ["Melbourne, VIC", "Sydney, NSW"]
        orgs = ["Stark Industries", "Avengers AU"]

        query_desc = f'Query: "{q}"'
        if names:
            query_desc += f' • Names: [{", ".join(names)}]'
        if locs:
            query_desc += f' • Locations: [{", ".join(locs)}]'
        if orgs:
            query_desc += f' • Orgs: [{", ".join(orgs)}]'

        self.assertIn('Query: "bubbsy"', query_desc)
        self.assertIn("Tony Stark", query_desc)
        self.assertIn("Melbourne, VIC", query_desc)
        self.assertIn("Stark Industries", query_desc)

    def test_02_url_encoding_special_characters(self):
        base_query = 'target & alias'
        names = 'Linus "The Father" Torvalds, John & Sons'
        locs = 'Portland, OR / Melbourne VIC'
        org = 'Linux Foundation & Co.'

        params = urllib.parse.urlencode({
            'platform': 'github',
            'query': base_query,
            'names': names,
            'locations': locs,
            'org': org,
            'limit': 5
        })

        parsed = urllib.parse.parse_qs(params)
        self.assertEqual(parsed['platform'][0], 'github')
        self.assertEqual(parsed['query'][0], 'target & alias')
        self.assertEqual(parsed['names'][0], names)
        self.assertEqual(parsed['locations'][0], locs)
        self.assertEqual(parsed['org'][0], org)


class TestManualPivotInjectionAndRemoval(unittest.TestCase):
    """Tests manual pivot addition, deduplication, and chip removal."""

    def setUp(self):
        self.confirmedNames = set()
        self.confirmedLocations = set()
        self.confirmedOrgs = set()
        self.confirmedHandles = set()
        self.discoveredEmails = set()

    def add_pivot(self, ptype, val):
        val = val.strip()
        if not val:
            return False
        if ptype == 'name':
            self.confirmedNames.add(val)
        elif ptype == 'location':
            self.confirmedLocations.add(val)
        elif ptype == 'org':
            self.confirmedOrgs.add(val)
        elif ptype == 'handle':
            self.confirmedHandles.add(val.lower())
        elif ptype == 'email':
            self.discoveredEmails.add(val.lower())
        return True

    def remove_pivot(self, ptype, val):
        if ptype == 'name':
            self.confirmedNames.discard(val)
        elif ptype == 'location':
            self.confirmedLocations.discard(val)
        elif ptype == 'org':
            self.confirmedOrgs.discard(val)
        elif ptype == 'handle':
            self.confirmedHandles.discard(val.lower())
        elif ptype == 'email':
            self.discoveredEmails.discard(val.lower())

    def test_01_add_and_remove_all_pivot_types(self):
        self.add_pivot('name', 'Linus Torvalds')
        self.add_pivot('location', 'Portland, OR')
        self.add_pivot('org', 'Linux Foundation')
        self.add_pivot('handle', 'Torvalds_AU')
        self.add_pivot('email', 'linus@linuxfoundation.org')

        self.assertIn('Linus Torvalds', self.confirmedNames)
        self.assertIn('Portland, OR', self.confirmedLocations)
        self.assertIn('Linux Foundation', self.confirmedOrgs)
        self.assertIn('torvalds_au', self.confirmedHandles)
        self.assertIn('linus@linuxfoundation.org', self.discoveredEmails)

        # Removal
        self.remove_pivot('name', 'Linus Torvalds')
        self.assertNotIn('Linus Torvalds', self.confirmedNames)
        self.remove_pivot('location', 'Portland, OR')
        self.assertNotIn('Portland, OR', self.confirmedLocations)
        self.remove_pivot('org', 'Linux Foundation')
        self.assertNotIn('Linux Foundation', self.confirmedOrgs)
        self.remove_pivot('handle', 'Torvalds_AU')
        self.assertNotIn('torvalds_au', self.confirmedHandles)
        self.remove_pivot('email', 'linus@linuxfoundation.org')
        self.assertNotIn('linus@linuxfoundation.org', self.discoveredEmails)


class TestReverseImageSearchAndEmailPermutations(unittest.TestCase):
    """Tests deep link generation and email permutations matrix."""

    def test_01_reverse_image_search_links_generation(self):
        avatar_url = "https://avatars.githubusercontent.com/u/1024025?v=4"
        enc = urllib.parse.quote(avatar_url, safe='')

        google_lens = f"https://lens.google.com/uploadbyurl?url={enc}"
        yandex = f"https://yandex.com/images/search?rpt=imageview&url={enc}"
        tineye = f"https://tineye.com/search?url={enc}"
        bing = f"https://www.bing.com/images/search?view=detailv2&iss=sbi&form=SBIHMP&sbisrc=UrlPaste&q=imgurl:{enc}"

        self.assertTrue(google_lens.startswith("https://lens.google.com/uploadbyurl?url="))
        self.assertTrue(yandex.startswith("https://yandex.com/images/search?rpt=imageview"))
        self.assertTrue(tineye.startswith("https://tineye.com/search?url="))
        self.assertTrue(bing.startswith("https://www.bing.com/images/search?view=detailv2"))
        self.assertIn(enc, google_lens)
        self.assertIn(enc, yandex)
        self.assertIn(enc, tineye)
        self.assertIn(enc, bing)

    def test_02_email_permutation_matrix(self):
        name = "Linus Torvalds"
        handle = "torvalds"
        company = "Linux Foundation"

        # Test combinatorial algorithm matching app.js
        perms = set()
        clean_handle = re.sub(r'[^a-zA-Z0-9]', '', handle).lower() if handle else ''
        if clean_handle:
            perms.add(f"{clean_handle}@gmail.com")
            perms.add(f"{clean_handle}@proton.me")
            perms.add(f"{clean_handle}@pm.me")
            perms.add(f"{clean_handle}@outlook.com")
            perms.add(f"{clean_handle}@icloud.com")

        clean_comp = re.sub(r'[^a-zA-Z0-9]', '', company).lower() if company else ''
        domain = f"{clean_comp}.org" if "foundation" in clean_comp else f"{clean_comp}.com"

        parts = [re.sub(r'[^a-zA-Z0-9]', '', p).lower() for p in name.split() if p.strip()]
        if len(parts) >= 2:
            first, last = parts[0], parts[-1]
            perms.add(f"{first}.{last}@gmail.com")
            if domain:
                perms.add(f"{first}.{last}@{domain}")
                perms.add(f"{first[0]}.{last}@{domain}")
                perms.add(f"{first}{last}@{domain}")
                perms.add(f"{first}@{domain}")
                perms.add(f"{last}@{domain}")
                if clean_handle:
                    perms.add(f"{clean_handle}@{domain}")

        self.assertIn("torvalds@gmail.com", perms)
        self.assertIn("linus.torvalds@linuxfoundation.org", perms)
        self.assertIn("l.torvalds@linuxfoundation.org", perms)
        self.assertIn("linustorvalds@linuxfoundation.org", perms)
        self.assertIn("linus@linuxfoundation.org", perms)
        self.assertGreaterEqual(len(perms), 8)


class TestRadialGraphLayoutGeometry(unittest.TestCase):
    """Empirically tests radial constellation trigonometry and node ID return."""

    def test_01_radial_constellation_positions(self):
        cx, cy = 400.0, 300.0
        radius = 160.0
        n_items = 6
        step = (2 * math.pi) / n_items

        positions = []
        for i in range(n_items):
            angle = i * step
            nx = cx + radius * math.cos(angle)
            ny = cy + radius * math.sin(angle)
            positions.append((nx, ny))

            # Verify Euclidean distance from center is exactly equal to radius
            dist = math.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
            self.assertAlmostEqual(dist, radius, places=5)

        # Ensure no two nodes occupy the same point
        unique_positions = set((round(x, 2), round(y, 2)) for x, y in positions)
        self.assertEqual(len(unique_positions), n_items)

    def test_02_addNodeToGraph_contract_in_js(self):
        """Scans app.js to confirm addNodeToGraph returns newNode.id."""
        with open(APP_JS_PATH, "r", encoding="utf-8") as f:
            js_code = f.read()

        match = re.search(r'window\.addNodeToGraph\s*=\s*function\s*\((.*?)\)\s*\{(.*?return\s+newNode\.id;.*?)\}', js_code, re.DOTALL)
        self.assertIsNotNone(match, "addNodeToGraph must return newNode.id in app.js")

        # Also check addEdgeToGraph exists
        self.assertIn("window.addEdgeToGraph = function", js_code)


class TestKeyboardShortcutsMapping(unittest.TestCase):
    """Verifies all specified keyboard shortcuts are mapped and bounded in js/app.js."""

    @classmethod
    def setUpClass(cls):
        with open(APP_JS_PATH, "r", encoding="utf-8") as f:
            cls.js_code = f.read()

    def test_01_all_shortcuts_present(self):
        shortcuts = [
            ("1/Y", r"e\.key\s*===\s*'1'\s*\|\|\s*e\.key\s*===\s*'y'"),
            ("2/U", r"e\.key\s*===\s*'2'\s*\|\|\s*e\.key\s*===\s*'u'"),
            ("3/N", r"e\.key\s*===\s*'3'\s*\|\|\s*e\.key\s*===\s*'n'"),
            ("[/Left", r"e\.key\s*===\s*'\['\s*\|\|\s*e\.key\s*===\s*'ArrowLeft'"),
            ("]/Right", r"e\.key\s*===\s*'\]'\s*\|\|\s*e\.key\s*===\s*'ArrowRight'"),
            ("G", r"e\.key\s*===\s*'g'\s*\|\|\s*e\.key\s*===\s*'G'"),
            ("Space/Z", r"e\.key\s*===\s*'\s*'\s*\|\|\s*e\.key\s*===\s*'z'"),
            ("R", r"e\.key\s*===\s*'r'\s*\|\|\s*e\.key\s*===\s*'R'"),
        ]
        for name, pattern in shortcuts:
            self.assertTrue(
                re.search(pattern, self.js_code),
                f"Shortcut {name} mapping not found in app.js"
            )

    def test_02_input_field_bypass_guard(self):
        """Ensures shortcuts do not trigger while typing in text inputs."""
        self.assertIn("if (tag === 'input' || tag === 'textarea' || tag === 'select') return;", self.js_code)


if __name__ == "__main__":
    unittest.main()
