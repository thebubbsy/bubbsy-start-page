"""
Backend coverage for optional accounts and synced preferences (accounts.py + /api/auth, /api/prefs).
"""
import http.cookiejar
import json
import os
import shutil
import urllib.error
import urllib.request
import uuid

import accounts


def _client():
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)), jar


def _call(opener, url, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', **(headers or {})})
    try:
        with opener.open(req) as resp:
            return resp.status, json.loads(resp.read() or b'{}'), resp.headers
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}'), e.headers


def _email():
    return f'test-{uuid.uuid4().hex[:10]}@example.com'


def test_me_reports_accounts_enabled_and_signed_out(live_server):
    opener, _ = _client()
    status, body, _ = _call(opener, f'{live_server}/api/auth/me')
    assert status == 200
    assert body['accountsEnabled'] is True
    assert body['user'] is None


def test_signup_sets_httponly_session_and_prefs_round_trip(live_server):
    opener, _ = _client()
    email = _email()
    status, body, headers = _call(opener, f'{live_server}/api/auth/signup', {'email': email.upper(), 'password': 'correct horse'})
    assert status == 200
    assert body['user']['email'] == email  # normalised to lower case
    assert body['prefs'] is None
    cookie = headers.get('Set-Cookie')
    assert 'HttpOnly' in cookie and 'SameSite=Lax' in cookie

    prefs = {'bubbsy_sort_mode': 'custom', 'bubbsy_custom_layout': json.dumps({'v': 1, 'columns': [[1, 2]]})}
    status, saved, _ = _call(opener, f'{live_server}/api/prefs', {'prefs': prefs})
    assert status == 200 and saved['updatedAt'] > 0

    status, got, _ = _call(opener, f'{live_server}/api/prefs')
    assert status == 200
    assert got['prefs'] == prefs
    assert got['updatedAt'] == saved['updatedAt']


def test_login_logout_and_wrong_password(live_server):
    opener, _ = _client()
    email = _email()
    _call(opener, f'{live_server}/api/auth/signup', {'email': email, 'password': 'password123'})
    _call(opener, f'{live_server}/api/auth/logout', {})
    status, body, _ = _call(opener, f'{live_server}/api/auth/me')
    assert body['user'] is None

    status, body, _ = _call(opener, f'{live_server}/api/auth/login', {'email': email, 'password': 'nope-nope'})
    assert status == 401

    status, body, _ = _call(opener, f'{live_server}/api/auth/login', {'email': email, 'password': 'password123'})
    assert status == 200 and body['user']['email'] == email


def test_signup_validation(live_server):
    opener, _ = _client()
    assert _call(opener, f'{live_server}/api/auth/signup', {'email': 'not-an-email', 'password': 'password123'})[0] == 400
    assert _call(opener, f'{live_server}/api/auth/signup', {'email': _email(), 'password': 'short'})[0] == 400
    email = _email()
    assert _call(opener, f'{live_server}/api/auth/signup', {'email': email, 'password': 'password123'})[0] == 200
    assert _call(_client()[0], f'{live_server}/api/auth/signup', {'email': email, 'password': 'password123'})[0] == 409


def test_prefs_require_sign_in(live_server):
    opener, _ = _client()
    assert _call(opener, f'{live_server}/api/prefs')[0] == 401
    assert _call(opener, f'{live_server}/api/prefs', {'prefs': {}})[0] == 401


def test_prefs_reject_non_text_values_and_oversize(live_server):
    opener, _ = _client()
    _call(opener, f'{live_server}/api/auth/signup', {'email': _email(), 'password': 'password123'})
    assert _call(opener, f'{live_server}/api/prefs', {'prefs': {'k': {'nested': 1}}})[0] == 400
    big = {'k': 'x' * (accounts.MAX_PREFS_BYTES + 10)}
    assert _call(opener, f'{live_server}/api/prefs', {'prefs': big})[0] == 413


def test_cross_site_post_is_refused(live_server):
    opener, _ = _client()
    _call(opener, f'{live_server}/api/auth/signup', {'email': _email(), 'password': 'password123'})
    status, body, _ = _call(opener, f'{live_server}/api/prefs', {'prefs': {}}, {'Origin': 'https://evil.example'})
    assert status == 403


def test_delete_account_removes_everything(live_server):
    opener, _ = _client()
    email = _email()
    _call(opener, f'{live_server}/api/auth/signup', {'email': email, 'password': 'password123'})
    _call(opener, f'{live_server}/api/prefs', {'prefs': {'bubbsy_theme': 'matrix'}})
    assert _call(opener, f'{live_server}/api/auth/delete', {})[0] == 200
    assert _call(opener, f'{live_server}/api/auth/me')[1]['user'] is None
    # The email is free again, and the old prefs are gone.
    status, body, _ = _call(_client()[0], f'{live_server}/api/auth/signup', {'email': email, 'password': 'password123'})
    assert status == 200 and body['prefs'] is None


def test_google_sign_in_is_off_without_client_id(live_server):
    opener, _ = _client()
    status, body, _ = _call(opener, f'{live_server}/api/auth/google', {'credential': 'x'})
    assert status == 503


def test_database_files_are_never_served(live_server):
    target = os.path.join(accounts.ROOT_DIR, 'data', 'leak-check.db')
    shutil.copy(accounts.db_path(), target)
    try:
        for path in ('/data/leak-check.db', '/data/leak%2Dcheck.DB'):
            try:
                urllib.request.urlopen(f'{live_server}{path}')
                raise AssertionError(f'{path} was served')
            except urllib.error.HTTPError as e:
                assert e.code == 404
    finally:
        os.remove(target)


def test_passwords_are_hashed_not_stored():
    stored = accounts.hash_password('s3cret-pass')
    assert 's3cret-pass' not in stored
    assert accounts.verify_password('s3cret-pass', stored)
    assert not accounts.verify_password('wrong', stored)
