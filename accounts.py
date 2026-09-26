"""
Optional accounts for Bubbsy Start Page.

An account does exactly one thing: it stores a user's display preferences (catalogue order, custom
module layout, pinned tools, theme, typography...) on this server so they follow the user between
computers. Everything works without an account; preferences are then kept in the browser only.

What is stored, and nothing more:
  users     email, a salted PBKDF2 password hash (or the Google account id for Google sign-in)
  sessions  a SHA-256 hash of the session token (the raw token lives only in the user's cookie)
  prefs     one JSON blob of preferences per user

Standard library only (sqlite3, hashlib, secrets) so the server keeps its zero-dependency footprint.

Configuration (environment variables):
  BUBBSY_DB_PATH     where the SQLite file lives (default: ~/.bubbsy/accounts.db). Keep it outside
                     the served directory. On hosts with an
                     ephemeral filesystem point this at a persistent disk, or accounts reset on deploy.
  GOOGLE_CLIENT_ID   OAuth client id for "Sign in with Google". Unset = Google button hidden,
                     email + password sign-up still works.
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import threading
import time
import urllib.parse
import urllib.request

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Deliberately outside the repo: server.py serves the repo root as static files, so a database kept
# there could be downloaded by anyone. server.py also refuses database paths as a second guard.
DEFAULT_DB_PATH = os.path.join(os.path.expanduser('~'), '.bubbsy', 'accounts.db')

SESSION_COOKIE = 'bubbsy_session'
SESSION_TTL_SECONDS = 90 * 24 * 3600
PBKDF2_ITERATIONS = 310_000
MIN_PASSWORD_LENGTH = 8
MAX_PREFS_BYTES = 256 * 1024
EMAIL_RE = re.compile(r'^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s]{2,63}$')

GOOGLE_TOKENINFO_URL = 'https://oauth2.googleapis.com/tokeninfo'
GOOGLE_ISSUERS = ('accounts.google.com', 'https://accounts.google.com')


class AuthError(Exception):
    """A user-facing failure. `status` is the HTTP status to answer with."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def db_path():
    return os.environ.get('BUBBSY_DB_PATH') or DEFAULT_DB_PATH


PRIVATE_FILE_RE = re.compile(r'\.(db|sqlite3?)(-wal|-shm|-journal)?$', re.IGNORECASE)


def is_private_path(url_path):
    """True for request paths that must never be served as static files (account databases)."""
    return bool(PRIVATE_FILE_RE.search(urllib.parse.unquote(url_path or '').rstrip('/')))


def google_client_id():
    return (os.environ.get('GOOGLE_CLIENT_ID') or '').strip()


_init_lock = threading.Lock()
_initialised_paths = set()


def _connect():
    path = db_path()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    with _init_lock:
        if path not in _initialised_paths:
            conn.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS users (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    email         TEXT NOT NULL UNIQUE,
                    password_hash TEXT,
                    google_sub    TEXT UNIQUE,
                    created_at    INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    expires_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS prefs (
                    user_id    INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    data       TEXT NOT NULL,
                    updated_at INTEGER NOT NULL
                );
            """)
            _initialised_paths.add(path)
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


# --- Passwords --------------------------------------------------------------------------------

def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PBKDF2_ITERATIONS)
    return f'pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}'


def verify_password(password, stored):
    try:
        algo, iterations, salt_hex, digest_hex = stored.split('$')
        if algo != 'pbkdf2_sha256':
            return False
        digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                     bytes.fromhex(salt_hex), int(iterations))
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, AttributeError):
        return False


# Burned on unknown-email logins so response time does not reveal which emails have accounts.
_DUMMY_HASH = hash_password(secrets.token_hex(8))


def _normalise_email(email):
    email = (email or '').strip().lower()
    if not EMAIL_RE.match(email):
        raise AuthError('Please enter a valid email address.')
    return email


# --- Login rate limiting (in-memory, per client IP) --------------------------------------------

_attempts = {}
_attempts_lock = threading.Lock()
MAX_ATTEMPTS = 10
ATTEMPT_WINDOW_SECONDS = 15 * 60


def check_rate_limit(client_ip):
    now = time.time()
    with _attempts_lock:
        recent = [t for t in _attempts.get(client_ip, []) if now - t < ATTEMPT_WINDOW_SECONDS]
        _attempts[client_ip] = recent
        if len(recent) >= MAX_ATTEMPTS:
            raise AuthError('Too many attempts. Please wait a few minutes and try again.', 429)


def record_failed_attempt(client_ip):
    with _attempts_lock:
        _attempts.setdefault(client_ip, []).append(time.time())


# --- Users & sessions --------------------------------------------------------------------------

def _public_user(row):
    return {
        'id': row['id'],
        'email': row['email'],
        'hasPassword': bool(row['password_hash']),
        'google': bool(row['google_sub']),
        'createdAt': row['created_at'],
    }


def signup(email, password):
    email = _normalise_email(email)
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise AuthError(f'Password must be at least {MIN_PASSWORD_LENGTH} characters.')
    if len(password) > 1024:
        raise AuthError('Password is too long.')
    with _connect() as conn:
        if conn.execute('SELECT 1 FROM users WHERE email = ?', (email,)).fetchone():
            raise AuthError('An account with that email already exists. Try signing in.', 409)
        cur = conn.execute('INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)',
                           (email, hash_password(password), int(time.time())))
        row = conn.execute('SELECT * FROM users WHERE id = ?', (cur.lastrowid,)).fetchone()
        return _public_user(row)


def login(email, password):
    email = _normalise_email(email)
    with _connect() as conn:
        row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    if not row or not row['password_hash']:
        verify_password(password or '', _DUMMY_HASH)
        if row and row['google_sub']:
            raise AuthError('This account uses Google sign-in. Use the Google button instead.', 401)
        raise AuthError('Email or password is incorrect.', 401)
    if not verify_password(password or '', row['password_hash']):
        raise AuthError('Email or password is incorrect.', 401)
    return _public_user(row)


def verify_google_credential(credential):
    """Validates a Google Identity Services ID token via Google's tokeninfo endpoint."""
    client_id = google_client_id()
    if not client_id:
        raise AuthError('Google sign-in is not configured on this server.', 503)
    if not credential or not isinstance(credential, str):
        raise AuthError('Missing Google credential.')
    url = GOOGLE_TOKENINFO_URL + '?' + urllib.parse.urlencode({'id_token': credential})
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            info = json.loads(resp.read().decode('utf-8'))
    except Exception:
        raise AuthError('Google could not verify that sign-in. Please try again.', 401)
    if info.get('aud') != client_id or info.get('iss') not in GOOGLE_ISSUERS:
        raise AuthError('That Google sign-in was not issued for this site.', 401)
    if int(info.get('exp', 0)) < time.time():
        raise AuthError('That Google sign-in has expired. Please try again.', 401)
    if str(info.get('email_verified')).lower() != 'true' or not info.get('email'):
        raise AuthError('Your Google account email is not verified.', 401)
    return info['sub'], info['email'].lower()


def login_with_google(credential):
    sub, email = verify_google_credential(credential)
    with _connect() as conn:
        row = conn.execute('SELECT * FROM users WHERE google_sub = ?', (sub,)).fetchone()
        if not row:
            row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            if row:
                # Google has verified ownership of this email, so link it to the existing account.
                conn.execute('UPDATE users SET google_sub = ? WHERE id = ?', (sub, row['id']))
            else:
                cur = conn.execute('INSERT INTO users (email, google_sub, created_at) VALUES (?, ?, ?)',
                                   (email, sub, int(time.time())))
                row = {'id': cur.lastrowid}
            row = conn.execute('SELECT * FROM users WHERE id = ?', (row['id'],)).fetchone()
        return _public_user(row)


def _token_hash(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def create_session(user_id):
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    with _connect() as conn:
        conn.execute('DELETE FROM sessions WHERE expires_at < ?', (now,))
        conn.execute('INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)',
                     (_token_hash(token), user_id, now + SESSION_TTL_SECONDS))
    return token


def user_for_session(token):
    if not token:
        return None
    with _connect() as conn:
        row = conn.execute(
            'SELECT users.* FROM sessions JOIN users ON users.id = sessions.user_id '
            'WHERE sessions.token_hash = ? AND sessions.expires_at >= ?',
            (_token_hash(token), int(time.time()))).fetchone()
    return _public_user(row) if row else None


def destroy_session(token):
    if not token:
        return
    with _connect() as conn:
        conn.execute('DELETE FROM sessions WHERE token_hash = ?', (_token_hash(token),))


def delete_user(user_id):
    with _connect() as conn:
        conn.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        conn.execute('DELETE FROM prefs WHERE user_id = ?', (user_id,))
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))


# --- Preferences -------------------------------------------------------------------------------

def get_prefs(user_id):
    with _connect() as conn:
        row = conn.execute('SELECT data, updated_at FROM prefs WHERE user_id = ?', (user_id,)).fetchone()
    if not row:
        return {'prefs': None, 'updatedAt': 0}
    return {'prefs': json.loads(row['data']), 'updatedAt': row['updated_at']}


def save_prefs(user_id, prefs):
    if not isinstance(prefs, dict):
        raise AuthError('Preferences must be a JSON object.')
    for key, value in prefs.items():
        if not isinstance(key, str) or not (value is None or isinstance(value, str)):
            raise AuthError('Preferences must map names to text values.')
    data = json.dumps(prefs, separators=(',', ':'))
    if len(data.encode('utf-8')) > MAX_PREFS_BYTES:
        raise AuthError('Preferences are too large to save.', 413)
    updated_at = int(time.time() * 1000)
    with _connect() as conn:
        conn.execute('INSERT INTO prefs (user_id, data, updated_at) VALUES (?, ?, ?) '
                     'ON CONFLICT(user_id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at',
                     (user_id, data, updated_at))
    return {'updatedAt': updated_at}
