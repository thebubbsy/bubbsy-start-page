"""
Comprehensive E2E and Unit Test Suite for MailAccess Integration
Testing:
1. Name Consensus Engine & Multi-Signal Clustering
2. Defender's Brief Risk Calculator (0-100 Score & Threat Bands)
3. Mail Provider & Domain Harvester
4. Live Server Endpoints /api/email/investigate and /api/email/harvest
"""

import pytest
import threading
import urllib.request
import urllib.parse
import json
import time
import server
import mailaccess_engine

@pytest.fixture(scope="module")
def live_server():
    """Spawns live threading server on localhost port 7777."""
    t = threading.Thread(target=server.run_server, daemon=True)
    t.start()
    time.sleep(0.5)
    yield "http://127.0.0.1:7777"

# =========================================================================
# 1. NAME CONSENSUS ENGINE TESTS
# =========================================================================

def test_name_consensus_multiple_corroborated_signals():
    signals = [
        {'name': 'Linus Torvalds', 'weight': 0.90, 'source': 'Gravatar'},
        {'name': 'Linus Torvalds', 'weight': 0.85, 'source': 'GitHub Commit / API'},
        {'name': 'Linus Torvalds', 'weight': 0.85, 'source': 'Keybase Identity'}
    ]
    res = mailaccess_engine.compute_name_consensus(signals)
    assert res['consensus_name'] == 'Linus Torvalds'
    assert res['confidence_band'] == 'CONFIRMED'
    assert res['confidence_score'] >= 85
    assert len(res['sources']) == 3
    assert 'Gravatar' in res['sources']

def test_name_consensus_single_weak_signal():
    signals = [
        {'name': 'John Doe', 'weight': 0.65, 'source': 'Email Local Part Syntax'}
    ]
    res = mailaccess_engine.compute_name_consensus(signals)
    assert res['consensus_name'] == 'John Doe'
    assert res['confidence_band'] in ('POSSIBLE', 'PROBABLE')
    assert res['confidence_score'] < 85

def test_name_consensus_empty_signals():
    res = mailaccess_engine.compute_name_consensus([])
    assert res['consensus_name'] is None
    assert res['confidence_band'] == 'UNKNOWN'
    assert res['confidence_score'] == 0

def test_parse_name_from_email_local_part():
    assert mailaccess_engine.parse_name_from_email_local_part('linus.torvalds') == 'Linus Torvalds'
    assert mailaccess_engine.parse_name_from_email_local_part('tony_stark') == 'Tony Stark'
    assert mailaccess_engine.parse_name_from_email_local_part('matthew.bubb.sec') == 'Matthew Bubb Sec'

# =========================================================================
# 2. DEFENDER'S BRIEF RISK CALCULATOR TESTS
# =========================================================================

def test_defenders_brief_high_exposure_calculation():
    breaches = [
        {'title': 'Breach 1', 'data_classes': ['Passwords', 'Email Addresses']},
        {'title': 'Breach 2', 'data_classes': ['Bcrypt Hashes', 'Usernames']}
    ]
    accounts = [
        {'platform': 'GitHub', 'found': True},
        {'platform': 'Gravatar', 'found': True}
    ]
    provider_info = {
        'is_m365_tenant': True,
        'is_google_workspace': False,
        'is_disposable': False
    }
    name_consensus = {
        'consensus_name': 'Test Target',
        'confidence_band': 'CONFIRMED'
    }

    brief = mailaccess_engine.generate_defenders_brief(
        email='target@corp.com',
        domain='corp.com',
        provider_info=provider_info,
        accounts=accounts,
        breaches=breaches,
        name_consensus=name_consensus
    )

    assert brief['exposure_score'] >= 50
    assert brief['threat_level'] in ('HIGH EXPOSURE', 'CRITICAL EXPOSURE')
    assert len(brief['findings']) >= 3
    assert len(brief['countermeasures']) >= 2

def test_defenders_brief_clean_target_low_exposure():
    brief = mailaccess_engine.generate_defenders_brief(
        email='clean_target@custom.com',
        domain='custom.com',
        provider_info={'is_m365_tenant': False, 'is_google_workspace': False, 'is_disposable': False},
        accounts=[],
        breaches=[],
        name_consensus={'consensus_name': None, 'confidence_band': 'UNKNOWN'}
    )
    assert brief['exposure_score'] <= 25
    assert brief['threat_level'] == 'LOW EXPOSURE'

# =========================================================================
# 3. DOMAIN HARVESTER & PROVIDER INSPECTION TESTS
# =========================================================================

def test_inspect_mail_provider_disposable():
    info = mailaccess_engine.inspect_mail_provider('mailinator.com')
    assert info['is_disposable'] is True

def test_inspect_mail_provider_australian():
    info = mailaccess_engine.inspect_mail_provider('anu.edu.au')
    assert info['is_australian_domain'] is True

def test_harvest_domain_emails():
    harvest = mailaccess_engine.harvest_domain_emails('atlassian.com')
    assert harvest['status'] == 'success'
    assert harvest['total_discovered'] >= 10
    assert len(harvest['naming_conventions']) >= 3
    assert any('security@atlassian.com' in e['email'] for e in harvest['discovered_emails'])

# =========================================================================
# 4. SERVER REST API ENDPOINT CONTRACT TESTS
# =========================================================================

def test_api_email_investigate_endpoint(live_server):
    url = f"{live_server}/api/email/investigate?email=torvalds@linux-foundation.org"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert data['status'] == 'success'
        assert data['email'] == 'torvalds@linux-foundation.org'
        assert 'name_consensus' in data
        assert 'defenders_brief' in data
        assert 'accounts' in data
        assert 'breaches' in data

def test_api_email_harvest_endpoint(live_server):
    url = f"{live_server}/api/email/harvest?domain=anu.edu.au"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert data['status'] == 'success'
        assert data['domain'] == 'anu.edu.au'
        assert data['total_discovered'] >= 10
        assert len(data['discovered_emails']) >= 10

def test_api_email_investigate_missing_param(live_server):
    url = f"{live_server}/api/email/investigate"
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(url)
    assert exc_info.value.code == 400

def test_api_email_harvest_missing_param(live_server):
    url = f"{live_server}/api/email/harvest"
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(url)
    assert exc_info.value.code == 400
