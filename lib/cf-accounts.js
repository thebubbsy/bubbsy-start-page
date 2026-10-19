/**
 * Accounts, synced preferences and admin access for the Cloudflare Pages deployment.
 *
 * Mirrors accounts.py (used when running server.py / wsgi.py) so the site behaves the same on
 * every host. Storage is the D1 database bound as `DB` in wrangler.toml; tables are created on
 * first use, so there is no migration step.
 *
 * An account stores: email, a salted PBKDF2 password hash (or a Google account id), a hash of each
 * session token, and one JSON blob of display preferences. Nothing else.
 *
 * Environment (Cloudflare Pages → Settings → Variables and Secrets):
 *   GOOGLE_CLIENT_ID  optional; enables "Sign in with Google"
 *   ADMIN_PASSWORD    optional secret; enables the admin analytics area (off when unset)
 */

export const SESSION_COOKIE = 'bubbsy_session';
export const SESSION_TTL_SECONDS = 90 * 24 * 3600;
// Cloudflare Workers cap PBKDF2 at 100,000 iterations. Hashes carry their iteration count, so
// accounts.py verifies these and vice versa.
const PBKDF2_ITERATIONS = 100000;
const MIN_PASSWORD_LENGTH = 8;
export const MAX_PREFS_BYTES = 256 * 1024;
const EMAIL_RE = /^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s]{2,63}$/;
const MAX_ATTEMPTS = 10;
const ATTEMPT_WINDOW_SECONDS = 15 * 60;

export class AuthError extends Error {
  constructor(message, status = 400) {
    super(message);
    this.status = status;
  }
}

const enc = new TextEncoder();

function toHex(buf) {
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}

function fromHex(hex) {
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.substr(i * 2, 2), 16);
  return out;
}

function randomToken(bytes = 32) {
  const b = crypto.getRandomValues(new Uint8Array(bytes));
  return btoa(String.fromCharCode(...b)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function sha256Hex(text) {
  return toHex(await crypto.subtle.digest('SHA-256', enc.encode(text)));
}

// Constant-time comparison of two strings (compares their SHA-256 digests byte by byte).
export async function safeEqual(a, b) {
  const [ha, hb] = await Promise.all([sha256Hex(String(a)), sha256Hex(String(b))]);
  let diff = 0;
  for (let i = 0; i < ha.length; i++) diff |= ha.charCodeAt(i) ^ hb.charCodeAt(i);
  return diff === 0;
}

async function pbkdf2(password, salt, iterations) {
  const key = await crypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations }, key, 256);
  return toHex(bits);
}

export async function hashPassword(password) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  return `pbkdf2_sha256$${PBKDF2_ITERATIONS}$${toHex(salt)}$${await pbkdf2(password, salt, PBKDF2_ITERATIONS)}`;
}

export async function verifyPassword(password, stored) {
  try {
    const [algo, iterations, saltHex, digestHex] = String(stored).split('$');
    if (algo !== 'pbkdf2_sha256') return false;
    const n = parseInt(iterations, 10);
    if (!(n > 0 && n <= PBKDF2_ITERATIONS)) return false; // Workers refuse higher counts
    return safeEqual(await pbkdf2(password, fromHex(saltHex), n), digestHex);
  } catch (e) {
    return false;
  }
}

// --- Schema -------------------------------------------------------------------------------------

const readyDbs = new WeakSet(); // tables are created once per database binding per isolate
export async function ensureSchema(db) {
  if (readyDbs.has(db)) return;
  await db.batch([
    db.prepare(`CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT NOT NULL UNIQUE,
      password_hash TEXT,
      google_sub TEXT UNIQUE,
      created_at INTEGER NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS sessions (
      token_hash TEXT PRIMARY KEY,
      user_id INTEGER NOT NULL,
      expires_at INTEGER NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS prefs (
      user_id INTEGER PRIMARY KEY,
      data TEXT NOT NULL,
      updated_at INTEGER NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS auth_attempts (
      ip TEXT NOT NULL,
      scope TEXT NOT NULL,
      at INTEGER NOT NULL)`),
    db.prepare('CREATE INDEX IF NOT EXISTS idx_auth_attempts ON auth_attempts(ip, scope, at)'),
  ]);
  readyDbs.add(db);
}

// --- Rate limiting (shared across all edge locations via D1) ------------------------------------

export async function checkRateLimit(db, ip, scope) {
  const since = Math.floor(Date.now() / 1000) - ATTEMPT_WINDOW_SECONDS;
  const row = await db.prepare('SELECT COUNT(*) AS n FROM auth_attempts WHERE ip = ? AND scope = ? AND at > ?')
    .bind(ip, scope, since).first();
  if (row && row.n >= MAX_ATTEMPTS) {
    throw new AuthError('Too many attempts. Please wait a few minutes and try again.', 429);
  }
}

export async function recordFailedAttempt(db, ip, scope) {
  const now = Math.floor(Date.now() / 1000);
  await db.batch([
    db.prepare('INSERT INTO auth_attempts (ip, scope, at) VALUES (?, ?, ?)').bind(ip, scope, now),
    db.prepare('DELETE FROM auth_attempts WHERE at < ?').bind(now - ATTEMPT_WINDOW_SECONDS),
  ]);
}

// --- Users & sessions ---------------------------------------------------------------------------

function publicUser(row) {
  return {
    id: row.id,
    email: row.email,
    hasPassword: !!row.password_hash,
    google: !!row.google_sub,
    createdAt: row.created_at,
  };
}

function normaliseEmail(email) {
  const e = String(email || '').trim().toLowerCase();
  if (!EMAIL_RE.test(e)) throw new AuthError('Please enter a valid email address.');
  return e;
}

export async function signup(db, email, password) {
  email = normaliseEmail(email);
  if (typeof password !== 'string' || password.length < MIN_PASSWORD_LENGTH) {
    throw new AuthError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters.`);
  }
  if (password.length > 1024) throw new AuthError('Password is too long.');
  const existing = await db.prepare('SELECT id FROM users WHERE email = ?').bind(email).first();
  if (existing) throw new AuthError('An account with that email already exists. Try signing in.', 409);
  await db.prepare('INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)')
    .bind(email, await hashPassword(password), Math.floor(Date.now() / 1000)).run();
  return publicUser(await db.prepare('SELECT * FROM users WHERE email = ?').bind(email).first());
}

let dummyHash = null;
export async function login(db, email, password) {
  email = normaliseEmail(email);
  const row = await db.prepare('SELECT * FROM users WHERE email = ?').bind(email).first();
  if (!row || !row.password_hash) {
    // Burn the same work as a real check so timing doesn't reveal which emails exist.
    dummyHash = dummyHash || await hashPassword(randomToken(8));
    await verifyPassword(String(password || ''), dummyHash);
    if (row && row.google_sub) throw new AuthError('This account uses Google sign-in. Use the Google button instead.', 401);
    throw new AuthError('Email or password is incorrect.', 401);
  }
  if (!(await verifyPassword(String(password || ''), row.password_hash))) {
    throw new AuthError('Email or password is incorrect.', 401);
  }
  return publicUser(row);
}

export async function loginWithGoogle(db, env, credential, fetchImpl = fetch) {
  const clientId = (env.GOOGLE_CLIENT_ID || '').trim();
  if (!clientId) throw new AuthError('Google sign-in is not configured on this site.', 503);
  if (!credential || typeof credential !== 'string') throw new AuthError('Missing Google credential.');
  let info;
  try {
    const res = await fetchImpl('https://oauth2.googleapis.com/tokeninfo?id_token=' + encodeURIComponent(credential));
    if (!res.ok) throw new Error('tokeninfo ' + res.status);
    info = await res.json();
  } catch (e) {
    throw new AuthError('Google could not verify that sign-in. Please try again.', 401);
  }
  if (info.aud !== clientId || !['accounts.google.com', 'https://accounts.google.com'].includes(info.iss)) {
    throw new AuthError('That Google sign-in was not issued for this site.', 401);
  }
  if (parseInt(info.exp || '0', 10) < Date.now() / 1000) throw new AuthError('That Google sign-in has expired. Please try again.', 401);
  if (String(info.email_verified).toLowerCase() !== 'true' || !info.email) throw new AuthError('Your Google account email is not verified.', 401);

  const email = String(info.email).toLowerCase();
  let row = await db.prepare('SELECT * FROM users WHERE google_sub = ?').bind(info.sub).first();
  if (!row) {
    row = await db.prepare('SELECT * FROM users WHERE email = ?').bind(email).first();
    if (row) {
      // Google has verified ownership of this email, so link it to the existing account.
      await db.prepare('UPDATE users SET google_sub = ? WHERE id = ?').bind(info.sub, row.id).run();
    } else {
      await db.prepare('INSERT INTO users (email, google_sub, created_at) VALUES (?, ?, ?)')
        .bind(email, info.sub, Math.floor(Date.now() / 1000)).run();
    }
    row = await db.prepare('SELECT * FROM users WHERE email = ?').bind(email).first();
  }
  return publicUser(row);
}

export async function createSession(db, userId) {
  const token = randomToken(32);
  const now = Math.floor(Date.now() / 1000);
  await db.batch([
    db.prepare('DELETE FROM sessions WHERE expires_at < ?').bind(now),
    db.prepare('INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)')
      .bind(await sha256Hex(token), userId, now + SESSION_TTL_SECONDS),
  ]);
  return token;
}

export async function userForSession(db, token) {
  if (!token) return null;
  const row = await db.prepare(
    'SELECT users.* FROM sessions JOIN users ON users.id = sessions.user_id WHERE sessions.token_hash = ? AND sessions.expires_at >= ?'
  ).bind(await sha256Hex(token), Math.floor(Date.now() / 1000)).first();
  return row ? publicUser(row) : null;
}

export async function destroySession(db, token) {
  if (token) await db.prepare('DELETE FROM sessions WHERE token_hash = ?').bind(await sha256Hex(token)).run();
}

export async function deleteUser(db, userId) {
  await db.batch([
    db.prepare('DELETE FROM sessions WHERE user_id = ?').bind(userId),
    db.prepare('DELETE FROM prefs WHERE user_id = ?').bind(userId),
    db.prepare('DELETE FROM users WHERE id = ?').bind(userId),
  ]);
}

export async function getPrefs(db, userId) {
  const row = await db.prepare('SELECT data, updated_at FROM prefs WHERE user_id = ?').bind(userId).first();
  return row ? { prefs: JSON.parse(row.data), updatedAt: row.updated_at } : { prefs: null, updatedAt: 0 };
}

export async function savePrefs(db, userId, prefs) {
  if (!prefs || typeof prefs !== 'object' || Array.isArray(prefs)) throw new AuthError('Preferences must be a JSON object.');
  for (const [k, v] of Object.entries(prefs)) {
    if (typeof k !== 'string' || !(v === null || typeof v === 'string')) throw new AuthError('Preferences must map names to text values.');
  }
  const data = JSON.stringify(prefs);
  if (enc.encode(data).length > MAX_PREFS_BYTES) throw new AuthError('Preferences are too large to save.', 413);
  const updatedAt = Date.now();
  await db.prepare('INSERT INTO prefs (user_id, data, updated_at) VALUES (?, ?, ?) ' +
    'ON CONFLICT(user_id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at')
    .bind(userId, data, updatedAt).run();
  return { updatedAt };
}

// --- HTTP helpers -------------------------------------------------------------------------------

export function clientIp(request) {
  return request.headers.get('cf-connecting-ip') || (request.headers.get('x-forwarded-for') || '').split(',')[0].trim() || 'unknown';
}

export function sessionToken(request) {
  const cookie = request.headers.get('Cookie') || '';
  for (const part of cookie.split(';')) {
    const [k, ...v] = part.trim().split('=');
    if (k === SESSION_COOKIE) return v.join('=') || null;
  }
  return null;
}

export function sessionCookie(token, maxAge) {
  return `${SESSION_COOKIE}=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
}

// State-changing requests from another site are refused (the cookie is SameSite=Lax as well).
export function sameOrigin(request) {
  const origin = request.headers.get('Origin');
  if (!origin) return true;
  try {
    return new URL(origin).host === new URL(request.url).host;
  } catch (e) {
    return false;
  }
}

export function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...extraHeaders },
  });
}

export async function readJson(request) {
  const text = await request.text();
  if (text.length > MAX_PREFS_BYTES * 2) throw new AuthError('Request is too large.', 413);
  let data;
  try {
    data = JSON.parse(text || '{}');
  } catch (e) {
    throw new AuthError('Request body must be JSON.');
  }
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new AuthError('Request body must be a JSON object.');
  return data;
}

// --- Admin ---------------------------------------------------------------------------------------

/**
 * Admin access = the ADMIN_PASSWORD secret, sent as HTTP Basic auth (the username is ignored).
 * Returns null when allowed, otherwise the Response to send. With no ADMIN_PASSWORD configured the
 * admin area is switched off entirely rather than protected by a guessable default.
 */
export async function requireAdmin(request, env) {
  const expected = env.ADMIN_PASSWORD || '';
  if (!expected) {
    return json({ error: 'Admin is switched off. Set the ADMIN_PASSWORD secret in Cloudflare Pages to enable it.', disabled: true }, 503);
  }
  const db = env.DB;
  const ip = clientIp(request);
  if (db) {
    await ensureSchema(db);
    try {
      await checkRateLimit(db, ip, 'admin');
    } catch (e) {
      return json({ error: e.message }, e.status || 429);
    }
  }
  const header = request.headers.get('Authorization') || '';
  let password = '';
  if (header.startsWith('Basic ')) {
    try {
      const decoded = atob(header.slice(6));
      password = decoded.includes(':') ? decoded.slice(decoded.indexOf(':') + 1) : decoded;
    } catch (e) {}
  }
  if (password && await safeEqual(password, expected)) return null;
  if (db) await recordFailedAttempt(db, ip, 'admin');
  return json({ error: 'Wrong admin password.' }, 401);
}
