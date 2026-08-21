import pytest
import urllib.parse
import threading
import time
import json
import re

import server

class TestEdgeCasesAndMaliciousInputs:
    """Stress tests empty, whitespace, special character, XSS, injection, and unicode queries."""

    def test_empty_query_and_names(self):
        """Query with empty string and no names should return 0 candidates gracefully."""
        params = {'query': [''], 'names': [''], 'locations': [''], 'org': [''], 'platform': ['github']}
        names_list = [n.strip() for n in params.get('names', [''])[0].split(',') if n.strip()]
        assert names_list == []
        probes = server.generate_probe_variations("", names_list, [], [])
        assert isinstance(probes, list)

    def test_spaces_only(self):
        """Query and parameters with only whitespace should be safely stripped and handled."""
        probes = server.generate_probe_variations("    ", ["   ", " \t "], ["   "], ["   "])
        assert isinstance(probes, list)
        assert len(probes) == 0

    def test_special_characters_and_symbols(self):
        """Query with ASCII symbols and punctuation should not crash."""
        payload = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        probes = server.generate_probe_variations(payload, [payload], [payload], [payload])
        assert isinstance(probes, list)
        for p in probes:
            assert isinstance(p, str)

    def test_xss_and_injection_payloads(self):
        """XSS and SQL injection payloads should not cause exceptions or crashes."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "\"><img src=x onerror=alert(1)>",
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "../../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\cmd.exe",
            "%00%0d%0a",
            "\x00\r\n\t"
        ]
        for payload in xss_payloads:
            probes = server.generate_probe_variations(payload, [payload], [payload], [payload])
            assert isinstance(probes, list)
            cand = {
                'key': 'test',
                'handle': payload,
                'display_name': payload,
                'company': payload,
                'website': 'https://example.com/' + payload,
                'avatar_url': 'https://example.com/avatar/' + payload,
                'location': payload,
                'bio': payload
            }
            enriched = server.enrich_candidate(cand)
            assert 'reverse_image_search' in enriched
            assert 'email_permutations' in enriched
            assert 'inferred_timezone' in enriched
            assert 'abn_search_url' in enriched
            assert 'asic_search_url' in enriched

    def test_unicode_cjk_emojis_rtl(self):
        """Unicode characters (emojis, CJK, Cyrillic, Arabic, Accents) should not cause encoding failures."""
        unicode_samples = [
            "🧑‍💻_ninja",
            "🚀🔥_dev",
            "李小龙",
            "Иван_Иванов",
            "محمد_أحمد",
            "René François Müller",
            "José María"
        ]
        for sample in unicode_samples:
            probes = server.generate_probe_variations(sample, [sample], [sample], [sample])
            assert isinstance(probes, list)
            
            cand = {
                'handle': sample,
                'display_name': sample,
                'company': sample,
                'avatar_url': f"https://example.com/{sample}.png"
            }
            enriched = server.enrich_candidate(cand)
            assert enriched['display_name'] == sample
            assert 'google_lens' in enriched['reverse_image_search']

    def test_extremely_long_strings(self):
        """Inputs with 5000+ characters should be processed without ReDoS or buffer exhaustion."""
        long_str = "a" * 5000
        probes = server.generate_probe_variations(long_str, [long_str], [long_str], [long_str])
        assert isinstance(probes, list)
        assert len(probes) <= 10

        cand = {'handle': long_str[:50], 'display_name': long_str, 'company': long_str}
        enriched = server.enrich_candidate(cand)
        assert isinstance(enriched['email_permutations'], list)


class TestQueryExpansionLogic:
    """Stress tests probe variation generation with multiple names, locations, and organizations."""

    def test_conflicting_multiple_names(self):
        """Multiple names should generate diverse and deduplicated probe variations."""
        names = ["Linus Torvalds", "Steve Jobs", "Bill Gates", "Ada Lovelace", "Alan Turing"]
        probes = server.generate_probe_variations("target", names, ["Sydney"], ["Linux Foundation"])
        assert len(probes) <= 10
        assert "target" in probes
        assert "linustorvalds" in probes
        assert "linus_torvalds" in probes
        assert "linus.torvalds" in probes
        assert "ltorvalds" in probes
        assert len(probes) == len(set(probes))  # All variations must be unique

    def test_names_with_hyphens_apostrophes_and_punctuation(self):
        """Names with hyphens (Jean-Luc) and apostrophes (O'Connor) should produce valid handles."""
        names = ["Mary-Kate Olsen", "Tim O'Connor", "Dr. John H. Watson"]
        probes = server.generate_probe_variations("mko", names, [], [])
        assert "mko" in probes
        assert "marykateolsen" in probes
        assert "timoconnor" in probes
        for p in probes:
            assert "'" not in p
            assert " " not in p

    def test_probe_variations_bounds(self):
        """Ensure probe variations is always capped at max 10 items."""
        names = [f"Firstname{i} Lastname{i}" for i in range(20)]
        probes = server.generate_probe_variations("base", names, [], [])
        assert len(probes) <= 10


class TestReverseImageSearchEncoding:
    """Tests URL encoding and link structure for reverse image search engines."""

    def test_valid_avatar_url_encodings(self):
        """Avatar URLs with spaces, query params, and special characters must be properly percent-encoded."""
        avatar = "https://avatars.githubusercontent.com/u/1024025?v=4&s=400#frag"
        res = server.build_reverse_image_search(avatar)
        
        assert 'google_lens' in res
        assert 'yandex' in res
        assert 'tineye' in res
        assert 'bing' in res
        assert 'pimeyes' in res

        encoded = urllib.parse.quote(avatar, safe='')
        assert res['google_lens'] == f"https://lens.google.com/uploadbyurl?url={encoded}"
        assert res['yandex'] == f"https://yandex.com/images/search?rpt=imageview&url={encoded}"
        assert res['tineye'] == f"https://tineye.com/search?url={encoded}"
        assert res['bing'] == f"https://www.bing.com/images/search?view=detailv2&iss=sbi&FORM=SBIHMP&sbisrc=UrlPaste&q=imgurl:{encoded}"
        assert res['pimeyes'] == "https://pimeyes.com/en"

    def test_empty_and_none_avatar_url(self):
        """Empty or None avatar URL should return an empty dictionary."""
        assert server.build_reverse_image_search("") == {}
        assert server.build_reverse_image_search(None) == {}

    def test_spaces_in_avatar_url(self):
        """Spaces in avatar URL should be quoted cleanly."""
        avatar = "https://example.com/my avatar path/pic 1.png"
        res = server.build_reverse_image_search(avatar)
        assert " " not in res['google_lens']
        assert "%20" in res['google_lens'] or "+" in res['google_lens']


class TestEmailPermutationMatrix:
    """Tests combinatorial email generation, domain parsing, and deduplication."""

    def test_standard_full_name_and_company_domain(self):
        """Standard name + company should generate standard corporate permutations."""
        perms = server.generate_candidate_emails(
            display_name="Linus Torvalds",
            handle="torvalds",
            company="Linux Foundation",
            website="https://kernel.org"
        )
        assert len(perms) <= 8
        assert "linus.torvalds@kernel.org" in perms
        assert "linustorvalds@kernel.org" in perms
        assert "ltorvalds@kernel.org" in perms
        assert "linus_torvalds@kernel.org" in perms
        assert "linus@kernel.org" in perms
        assert "torvalds.linus@kernel.org" in perms
        assert "torvalds@kernel.org" in perms
        assert "torvalds@gmail.com" in perms
        assert len(perms) == len(set(perms))

    def test_company_fallback_domain_inference(self):
        """When website is empty, infer domain from company type."""
        p1 = server.generate_candidate_emails("John Doe", "johnd", "Apache Foundation", "")
        assert any("@apachefoundation.org" in e for e in p1)

        p2 = server.generate_candidate_emails("John Doe", "johnd", "Harvard Edu", "")
        assert any("@harvardedu.edu" in e for e in p2)

        p3 = server.generate_candidate_emails("John Doe", "johnd", "CSIRO Australia Gov", "")
        assert any("@csiroaustraliagov.gov.au" in e for e in p3)

        p4 = server.generate_candidate_emails("John Doe", "johnd", "Acme Corporation", "")
        assert any("@acmecorporation.com" in e for e in p4)

    def test_single_word_display_name(self):
        """Single-word display name (e.g. 'Torvalds') should produce valid permutations."""
        perms = server.generate_candidate_emails("Torvalds", "torvalds", "Kernel Org", "kernel.org")
        assert len(perms) <= 8
        assert "torvalds@kernel.org" in perms
        assert "torvalds@gmail.com" in perms
        assert len(perms) == len(set(perms))

    def test_no_name_only_handle(self):
        """Handle only (no display name or name equals handle) should generate fallback webmail."""
        perms = server.generate_candidate_emails("", "sec_hunter", "", "")
        assert "sec_hunter@gmail.com" in perms
        assert "sec_hunter@protonmail.com" in perms
        assert "sec_hunter@outlook.com" in perms
        assert len(perms) == len(set(perms))

    def test_complex_website_urls(self):
        """Websites with protocols, ports, subdomains, and paths should extract clean domain."""
        perms = server.generate_candidate_emails(
            "Alice Smith", "asmith", "Test Co", "https://www.sub.example.com.au:8443/about?v=1"
        )
        assert any("@sub.example.com.au" in e for e in perms)

    def test_corporate_search_urls(self):
        """ABN and ASIC search URLs must be properly formed and quoted."""
        abn, asic = server.build_corporate_search_urls("Atlassian Pty Ltd", "Scott Farquhar")
        assert abn == "https://abr.business.gov.au/Search/Results?SearchText=Atlassian%20Pty%20Ltd"
        assert "searchTerm=Atlassian%20Pty%20Ltd" in asic

        abn_none, asic_none = server.build_corporate_search_urls("", "")
        assert abn_none is None
        assert asic_none is None


class TestTimezoneChronolocation:
    """Tests accuracy of Australian and international timezone chronolocation heuristics."""

    def test_australian_sydney_melbourne_brisbane_canberra_hobart(self):
        """Eastern Australian cities & states map to Australia/Sydney."""
        eastern_samples = [
            "Sydney, Australia",
            "Sydney, NSW",
            "New South Wales",
            "Melbourne, VIC",
            "Victoria, Australia",
            "Brisbane, Queensland",
            "Brisbane, QLD",
            "Canberra, ACT",
            "Hobart, Tasmania",
            "Hobart, TAS"
        ]
        for sample in eastern_samples:
            tz = server.infer_timezone_chronolocation(sample, "")
            assert tz == "Australia/Sydney (AEST/AEDT, UTC+10/+11)", f"Failed for {sample}: got {tz}"

    def test_australian_adelaide_darwin(self):
        """Central Australian cities & states map to Australia/Adelaide."""
        central_samples = [
            "Adelaide, South Australia",
            "Adelaide, SA",
            "Darwin, Northern Territory",
            "Darwin, NT",
            "South Australia"
        ]
        for sample in central_samples:
            tz = server.infer_timezone_chronolocation(sample, "")
            assert tz == "Australia/Adelaide (ACST/ACDT, UTC+9:30/+10:30)", f"Failed for {sample}: got {tz}"

    def test_australian_perth(self):
        """Western Australian cities & states map to Australia/Perth."""
        western_samples = [
            "Perth, Western Australia",
            "Perth, WA",
            "Western Australia"
        ]
        for sample in western_samples:
            tz = server.infer_timezone_chronolocation(sample, "")
            assert tz == "Australia/Perth (AWST, UTC+8)", f"Failed for {sample}: got {tz}"

    def test_australian_general(self):
        """Generic Australia references fallback to Australia/Sydney."""
        general_samples = [
            "Australia",
            "Developer from Australia",
            "contact@company.com.au"
        ]
        for sample in general_samples:
            tz = server.infer_timezone_chronolocation(sample, "")
            assert "Australia" in tz

    def test_north_america_timezones(self):
        """North American cities map to corresponding PST/EST/CST/MST."""
        assert "America/Los_Angeles" in server.infer_timezone_chronolocation("San Francisco, CA")
        assert "America/Los_Angeles" in server.infer_timezone_chronolocation("Seattle, WA")
        assert "America/Los_Angeles" in server.infer_timezone_chronolocation("Portland, Oregon")
        assert "America/Los_Angeles" in server.infer_timezone_chronolocation("Vancouver, Canada")
        assert "America/New_York" in server.infer_timezone_chronolocation("New York, NY")
        assert "America/New_York" in server.infer_timezone_chronolocation("Boston, MA")
        assert "America/New_York" in server.infer_timezone_chronolocation("Toronto, Canada")
        assert "America/New_York" in server.infer_timezone_chronolocation("Washington DC")
        assert "America/Chicago" in server.infer_timezone_chronolocation("Chicago, IL")
        assert "America/Chicago" in server.infer_timezone_chronolocation("Austin, Texas")
        assert "America/Denver" in server.infer_timezone_chronolocation("Denver, Colorado")
        assert "America/Denver" in server.infer_timezone_chronolocation("Salt Lake City, Utah")

    def test_europe_uk_timezones(self):
        """European and UK cities map to Europe/London and Europe/Berlin."""
        assert "Europe/London" in server.infer_timezone_chronolocation("London, UK")
        assert "Europe/London" in server.infer_timezone_chronolocation("Dublin, Ireland")
        assert "Europe/London" in server.infer_timezone_chronolocation("Edinburgh, Scotland")
        assert "Europe/Berlin" in server.infer_timezone_chronolocation("Berlin, Germany")
        assert "Europe/Berlin" in server.infer_timezone_chronolocation("Paris, France")
        assert "Europe/Berlin" in server.infer_timezone_chronolocation("Amsterdam, Netherlands")
        assert "Europe/Berlin" in server.infer_timezone_chronolocation("Stockholm, Sweden")
        assert "Europe/Berlin" in server.infer_timezone_chronolocation("Zurich, Switzerland")
        assert "Europe/Berlin" in server.infer_timezone_chronolocation("Madrid, Spain")
        assert "Europe/Berlin" in server.infer_timezone_chronolocation("Rome, Italy")

    def test_asia_pacific_timezones(self):
        """Asian and Pacific metros map accurately."""
        assert "Asia/Tokyo" in server.infer_timezone_chronolocation("Tokyo, Japan")
        assert "Asia/Singapore" in server.infer_timezone_chronolocation("Singapore")
        assert "Asia/Singapore" in server.infer_timezone_chronolocation("Hong Kong")
        assert "Asia/Singapore" in server.infer_timezone_chronolocation("Taipei, Taiwan")
        assert "Asia/Singapore" in server.infer_timezone_chronolocation("Beijing, China")
        assert "Asia/Kolkata" in server.infer_timezone_chronolocation("Bengaluru, India")
        assert "Asia/Kolkata" in server.infer_timezone_chronolocation("Delhi, India")
        assert "Asia/Kolkata" in server.infer_timezone_chronolocation("Mumbai, India")
        assert "Pacific/Auckland" in server.infer_timezone_chronolocation("Auckland, New Zealand")

    def test_unspecified_or_empty_location(self):
        """Empty or unknown location returns UTC fallback."""
        assert server.infer_timezone_chronolocation("", "") == "UTC / Unspecified Location"
        assert server.infer_timezone_chronolocation(None, None) == "UTC / Unspecified Location"
        assert server.infer_timezone_chronolocation("Outer Space", "Alien bio") == "UTC / Unspecified Location"


class TestThreadingAndCacheConcurrency:
    """Stress tests thread-safe TTL cache under concurrent reads and writes."""

    def test_concurrent_cache_reads_and_writes(self):
        """50 concurrent threads writing and reading from SOCIAL_CACHE."""
        errors = []

        def worker(thread_id):
            try:
                for i in range(20):
                    key = f"key_{thread_id}_{i % 5}"
                    data = {'thread': thread_id, 'val': i, 'cached': False}
                    server.set_cached_candidates(key, data)
                    cached = server.get_cached_candidates(key)
                    assert cached is not None
                    assert cached['cached'] is True
                    assert cached['thread'] == thread_id
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Encountered {len(errors)} concurrency errors: {errors}"

    def test_cache_deep_copy_isolation(self):
        """Modifying data returned from get_cached_candidates must not mutate SOCIAL_CACHE entry."""
        key = "test_isolation_key"
        original_data = {'handle': 'torvalds', 'tags': ['kernel', 'c'], 'cached': False}
        server.set_cached_candidates(key, original_data)
        
        cached = server.get_cached_candidates(key)
        cached['tags'].append('mutated_tag')
        cached['handle'] = 'mutated_handle'
        
        second_fetch = server.get_cached_candidates(key)
        assert 'mutated_tag' not in second_fetch['tags']
        assert second_fetch['handle'] == 'torvalds'

    def test_cache_lru_pruning_under_pressure(self):
        """Writing more than 500 items into cache triggers pruning without raising exceptions."""
        for i in range(600):
            server.set_cached_candidates(f"pressure_key_{i}", {'i': i})
        
        with server.CACHE_LOCK:
            assert len(server.SOCIAL_CACHE) <= 501


class TestCandidateScrapersIntegrity:
    """Verifies that all 10 scrapers return well-formed candidate lists adhering to PROJECT.md schema."""

    def _verify_candidate_schema(self, cand):
        required_fields = [
            'key', 'platform', 'platform_id', 'category', 'handle', 'display_name',
            'url', 'avatar_url', 'bio', 'location', 'company', 'website', 'stats',
            'created_at', 'last_active', 'verified', 'cryptographic_proofs',
            'pgp_fingerprint', 'inferred_timezone', 'reverse_image_search',
            'email_permutations', 'abn_search_url', 'asic_search_url'
        ]
        for field in required_fields:
            assert field in cand, f"Missing required field '{field}' in candidate: {cand}"
        
        assert isinstance(cand['reverse_image_search'], dict)
        assert isinstance(cand['email_permutations'], list)
        assert isinstance(cand['cryptographic_proofs'], list)
        assert cand['avatar_url'].startswith('http') or cand['avatar_url'].startswith('https')

    def test_github_scraper_schema(self):
        cands = server.scrape_github_candidates("torvalds", ["Linus Torvalds"], ["Portland, OR"], ["Linux Foundation"], limit=3)
        assert len(cands) == 3
        for c in cands:
            self._verify_candidate_schema(c)

    def test_bluesky_scraper_schema(self):
        cands = server.scrape_bluesky_candidates("torvalds", ["Linus Torvalds"], ["Portland, OR"], ["Linux Foundation"], limit=3)
        assert len(cands) == 3
        for c in cands:
            self._verify_candidate_schema(c)

    def test_keybase_scraper_schema(self):
        cands = server.scrape_keybase_candidates("torvalds", ["Linus Torvalds"], ["Portland, OR"], ["Linux Foundation"], limit=3)
        assert len(cands) == 3
        for c in cands:
            self._verify_candidate_schema(c)

    def test_reddit_scraper_schema(self):
        cands = server.scrape_reddit_candidates("torvalds", ["Linus Torvalds"], ["Portland, OR"], ["Linux Foundation"], limit=3)
        assert len(cands) == 3
        for c in cands:
            self._verify_candidate_schema(c)

    def test_gitlab_scraper_schema(self):
        cands = server.scrape_gitlab_candidates("torvalds", ["Linus Torvalds"], ["Portland, OR"], ["Linux Foundation"], limit=3)
        assert len(cands) == 3
        for c in cands:
            self._verify_candidate_schema(c)

    def test_devto_scraper_schema(self):
        cands = server.scrape_devto_candidates("torvalds", ["Linus Torvalds"], ["Portland, OR"], ["Linux Foundation"], limit=3)
        assert len(cands) == 3
        for c in cands:
            self._verify_candidate_schema(c)

    def test_dockerhub_scraper_schema(self):
        cands = server.scrape_dockerhub_candidates("torvalds", ["Linus Torvalds"], ["Portland, OR"], ["Linux Foundation"], limit=3)
        assert len(cands) == 3
        for c in cands:
            self._verify_candidate_schema(c)

    def test_whirlpool_forum_scraper_schema(self):
        cands = server.scrape_forum_candidates("whirlpool", "torvalds", ["Linus Torvalds"], ["Sydney"], ["Linux Foundation"], limit=3)
        assert len(cands) == 3
        for c in cands:
            self._verify_candidate_schema(c)

    def test_ocau_forum_scraper_schema(self):
        cands = server.scrape_forum_candidates("ocau", "torvalds", ["Linus Torvalds"], ["Melbourne"], ["Linux Foundation"], limit=3)
        assert len(cands) == 3
        for c in cands:
            self._verify_candidate_schema(c)

    def test_ozbargain_forum_scraper_schema(self):
        cands = server.scrape_forum_candidates("ozbargain", "torvalds", ["Linus Torvalds"], ["Brisbane"], ["Linux Foundation"], limit=3)
        assert len(cands) == 3
        for c in cands:
            self._verify_candidate_schema(c)

    def test_gravatar_scraper_schema(self):
        cands = server.scrape_gravatar_candidates("torvalds", ["Linus Torvalds"], ["Portland, OR"], ["Linux Foundation"], limit=3)
        assert len(cands) == 3
        for c in cands:
            self._verify_candidate_schema(c)

    def test_scrape_all_platforms(self):
        cands = server.scrape_all_platform_candidates("torvalds", ["Linus Torvalds"], ["Portland, OR"], ["Linux Foundation"], limit=10)
        assert len(cands) == 10
        for c in cands:
            self._verify_candidate_schema(c)
