"""
Comprehensive E2E and Unit Test Suite for Domain Drop Sniper & Expiry Countdown Radar.
"""

import pytest
import threading
import urllib.request
import urllib.parse
import json
import time
import datetime
import server
import domain_drop_engine

# =========================================================================
# 1. LIFECYCLE & STATE MACHINE UNIT TESTS
# =========================================================================

def test_clean_domain_string():
    assert domain_drop_engine.clean_domain_string('https://www.example.com/path') == 'www.example.com'
    assert domain_drop_engine.clean_domain_string('http://sub.domain.com.au:8080?q=1') == 'sub.domain.com.au'
    assert domain_drop_engine.clean_domain_string('   google.com   ') == 'google.com'

def test_is_australian_domain():
    assert domain_drop_engine.is_australian_domain('cloudsec.com.au') is True
    assert domain_drop_engine.is_australian_domain('anu.edu.au') is True
    assert domain_drop_engine.is_australian_domain('google.com') is False
    assert domain_drop_engine.is_australian_domain('ai.io') is False

def test_lifecycle_stage_active():
    future_exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=120)
    res = domain_drop_engine.calculate_lifecycle_stage('example.com', future_exp, False)
    assert res['stage_code'] == 'ACTIVE_REGISTERED'
    assert res['stage_index'] == 0
    assert res['drop_seconds_remaining'] > 86400 * 120

def test_lifecycle_stage_australian_pending_delete():
    # 31 days expired on .au domain -> Pending delete (day 31-33)
    past_exp = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=31)
    res = domain_drop_engine.calculate_lifecycle_stage('expired.com.au', past_exp, True)
    assert res['stage_code'] == 'PENDING_DELETE'
    assert res['stage_index'] == 3
    assert res['is_dropping_soon'] is True
    assert '1:00 PM AEST' in res['status_description']

def test_lifecycle_stage_gtld_redemption():
    # 45 days expired on .com domain -> Redemption Period (day 30-60)
    past_exp = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=45)
    res = domain_drop_engine.calculate_lifecycle_stage('expired.com', past_exp, False)
    assert res['stage_code'] == 'REDEMPTION_PERIOD'
    assert res['stage_index'] == 2

def test_backorder_dispatch_matrix_australian():
    dispatch = domain_drop_engine.get_backorder_dispatch_matrix('test.com.au')
    provider_names = [p['name'] for p in dispatch['primary_providers']]
    assert 'Drop.com.au' in provider_names
    assert 'Netfleet.com.au' in provider_names
    assert len(dispatch['archive_intel']) >= 3

def test_backorder_dispatch_matrix_global():
    dispatch = domain_drop_engine.get_backorder_dispatch_matrix('globalbrand.com')
    provider_names = [p['name'] for p in dispatch['primary_providers']]
    assert 'DropCatch.com' in provider_names
    assert 'SnapNames' in provider_names
    assert 'NameJet' in provider_names

def test_trending_watchlist():
    res = domain_drop_engine.get_trending_dropping_watchlist()
    assert res['status'] == 'success'
    assert len(res['australian_drops']) >= 3
    assert len(res['global_drops']) >= 3
    assert res['total_monitored'] >= 6

# =========================================================================
# 2. REST API ENDPOINT CONTRACT TESTS
# =========================================================================

def test_api_domain_expiry_endpoint(live_server):
    url = f"{live_server}/api/domain/expiry?domain=google.com"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert data['status'] == 'success'
        assert data['domain'] == 'google.com'
        assert 'lifecycle' in data
        assert 'dispatch' in data
        assert 'countdown_formatted' in data['lifecycle']

def test_api_domain_expiry_australian(live_server):
    url = f"{live_server}/api/domain/expiry?domain=cloudsec.com.au"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert data['status'] == 'success'
        assert data['is_australian'] is True
        assert 'drop_timestamp_aest' in data['lifecycle']

def test_api_domain_drops_trending_endpoint(live_server):
    url = f"{live_server}/api/domain/drops/trending"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert data['status'] == 'success'
        assert 'australian_drops' in data
        assert 'global_drops' in data

def test_api_domain_expiry_missing_param(live_server):
    url = f"{live_server}/api/domain/expiry"
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(url)
    assert exc_info.value.code == 400
