/**
 * Tests for the Cloudflare Pages Functions (accounts, prefs, admin, tracker), run with Node's
 * built-in test runner against an in-memory SQLite database that mimics the D1 API.
 *
 *   node --test tests/functions/
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';

import * as auth from '../../functions/api/auth/[action].js';
import * as prefs from '../../functions/api/prefs.js';
import * as analytics from '../../functions/api/admin/analytics.js';
import * as clear from '../../functions/api/admin/clear.js';
import * as track from '../../functions/api/track.js';
import { verifyPassword, hashPassword } from '../../lib/cf-accounts.js';

// Minimal D1 stand-in: prepare().bind().run()/first()/all() and db.batch().
function makeD1() {
  const sqlite = new DatabaseSync(':memory:');
  const stmt = (sql, args = []) => ({
    bind: (...a) => stmt(sql, a),
    async run() { sqlite.prepare(sql).run(...args); return { success: true }; },
    async first() { return sqlite.prepare(sql).get(...args) ?? null; },
    async all() { return { results: sqlite.prepare(sql).all(...args) }; },
    _exec() { sqlite.prepare(sql).run(...args); },
  });
  return {
    prepare: (sql) => stmt(sql),
    async batch(list) { for (const s of list) s._exec(); return []; },
    _sqlite: sqlite,
  };
}

const ORIGIN = 'https://bubbsy.example';

function req(method, path, { body, cookie, headers = {} } = {}) {
  const h = new Headers({ 'cf-connecting-ip': headers.ip || '203.0.113.9', ...headers });
  if (cookie) h.set('Cookie', cookie);
  if (body !== undefined) h.set('Content-Type', 'application/json');
  return new Request(ORIGIN + path, { method, headers: h, body: body === undefined ? undefined : JSON.stringify(body) });
}

async function call(mod, method, path, opts = {}, env, params = {}) {
  const handler = method === 'GET' ? mod.onRequestGet : mod.onRequestPost;
  const res = await handler({ request: req(method, path, opts), env, params });
  const text = await res.text();
  return { status: res.status, body: text ? JSON.parse(text) : {}, cookie: res.headers.get('Set-Cookie') };
}

const authCall = (method, action, opts, env) => call(auth, method, `/api/auth/${action}`, opts, env, { action });

test('signup, session cookie, prefs round trip, logout', async () => {
  const env = { DB: makeD1() };
  let r = await authCall('GET', 'me', {}, env);
  assert.equal(r.status, 200);
  assert.equal(r.body.accountsEnabled, true);
  assert.equal(r.body.user, null);
  assert.equal(r.body.googleClientId, null);

  r = await authCall('POST', 'signup', { body: { email: 'Jane@Example.com', password: 'correct horse' } }, env);
  assert.equal(r.status, 200);
  assert.equal(r.body.user.email, 'jane@example.com');
  assert.match(r.cookie, /HttpOnly/);
  assert.match(r.cookie, /Secure/);
  assert.match(r.cookie, /SameSite=Lax/);
  const cookie = r.cookie.split(';')[0];

  // The raw token is never stored, only its hash.
  const rows = env.DB._sqlite.prepare('SELECT token_hash FROM sessions').all();
  assert.equal(rows.length, 1);
  assert.notEqual(rows[0].token_hash, cookie.split('=')[1]);

  r = await authCall('GET', 'me', { cookie }, env);
  assert.equal(r.body.user.email, 'jane@example.com');

  const saved = { bubbsy_sort_mode: 'custom', bubbsy_theme: 'matrix' };
  r = await call(prefs, 'POST', '/api/prefs', { cookie, body: { prefs: saved } }, env);
  assert.equal(r.status, 200);
  r = await call(prefs, 'GET', '/api/prefs', { cookie }, env);
  assert.deepEqual(r.body.prefs, saved);

  r = await authCall('POST', 'logout', { cookie, body: {} }, env);
  assert.match(r.cookie, /Max-Age=0/);
  r = await call(prefs, 'GET', '/api/prefs', { cookie }, env);
  assert.equal(r.status, 401);
});

test('login rejects wrong password and duplicate signup', async () => {
  const env = { DB: makeD1() };
  await authCall('POST', 'signup', { body: { email: 'a@b.co', password: 'password123' } }, env);
  assert.equal((await authCall('POST', 'signup', { body: { email: 'a@b.co', password: 'password123' } }, env)).status, 409);
  assert.equal((await authCall('POST', 'login', { body: { email: 'a@b.co', password: 'wrong-pass' } }, env)).status, 401);
  assert.equal((await authCall('POST', 'login', { body: { email: 'a@b.co', password: 'password123' } }, env)).status, 200);
  assert.equal((await authCall('POST', 'signup', { body: { email: 'nope', password: 'password123' } }, env)).status, 400);
  assert.equal((await authCall('POST', 'signup', { body: { email: 'c@d.co', password: 'short' } }, env)).status, 400);
});

test('login is rate limited per IP', async () => {
  const env = { DB: makeD1() };
  for (let i = 0; i < 10; i++) {
    await authCall('POST', 'login', { body: { email: 'x@y.co', password: 'wrong-pass' } }, env);
  }
  const r = await authCall('POST', 'login', { body: { email: 'x@y.co', password: 'wrong-pass' } }, env);
  assert.equal(r.status, 429);
  // A different IP is unaffected.
  const other = await authCall('POST', 'login', { body: { email: 'x@y.co', password: 'wrong-pass' }, headers: { ip: '198.51.100.7' } }, env);
  assert.equal(other.status, 401);
});

test('cross-site POSTs are refused', async () => {
  const env = { DB: makeD1() };
  const r = await authCall('POST', 'signup', { body: { email: 'e@f.co', password: 'password123' }, headers: { Origin: 'https://evil.example' } }, env);
  assert.equal(r.status, 403);
});

test('delete removes the account and its prefs', async () => {
  const env = { DB: makeD1() };
  const s = await authCall('POST', 'signup', { body: { email: 'del@me.co', password: 'password123' } }, env);
  const cookie = s.cookie.split(';')[0];
  await call(prefs, 'POST', '/api/prefs', { cookie, body: { prefs: { bubbsy_theme: 'amber' } } }, env);
  assert.equal((await authCall('POST', 'delete', { cookie, body: {} }, env)).status, 200);
  assert.equal(env.DB._sqlite.prepare('SELECT COUNT(*) AS n FROM users').get().n, 0);
  assert.equal(env.DB._sqlite.prepare('SELECT COUNT(*) AS n FROM prefs').get().n, 0);
});

test('google sign-in is off without a client id and reports it when set', async () => {
  const env = { DB: makeD1() };
  assert.equal((await authCall('POST', 'google', { body: { credential: 'x' } }, env)).status, 503);
  const me = await authCall('GET', 'me', {}, { ...env, GOOGLE_CLIENT_ID: 'abc.apps.googleusercontent.com' });
  assert.equal(me.body.googleClientId, 'abc.apps.googleusercontent.com');
});

test('password hashes interoperate with accounts.py format', async () => {
  const stored = await hashPassword('s3cret-pass');
  assert.match(stored, /^pbkdf2_sha256\$100000\$[0-9a-f]{32}\$[0-9a-f]{64}$/);
  assert.ok(await verifyPassword('s3cret-pass', stored));
  assert.ok(!(await verifyPassword('wrong', stored)));
});

test('admin is switched off without ADMIN_PASSWORD and the old default no longer works', async () => {
  const env = { DB: makeD1() };
  const oldDefault = { Authorization: 'Basic ' + btoa('user:hacker') };
  let r = await call(analytics, 'GET', '/api/admin/analytics', { headers: oldDefault }, env);
  assert.equal(r.status, 503);
  r = await call(analytics, 'GET', '/api/admin/analytics?u=user&p=hacker', {}, env);
  assert.equal(r.status, 503);

  const withSecret = { ...env, ADMIN_PASSWORD: 'a-long-owner-secret' };
  r = await call(analytics, 'GET', '/api/admin/analytics', { headers: oldDefault }, withSecret);
  assert.equal(r.status, 401);
  r = await call(clear, 'POST', '/api/admin/clear', { headers: oldDefault, body: {} }, withSecret);
  assert.equal(r.status, 401);

  const good = { Authorization: 'Basic ' + btoa('admin:a-long-owner-secret') };
  r = await call(analytics, 'GET', '/api/admin/analytics', { headers: good }, withSecret);
  assert.equal(r.status, 200);
  assert.equal(r.body.authorized, true);
});

test('admin password guessing is rate limited', async () => {
  const env = { DB: makeD1(), ADMIN_PASSWORD: 'a-long-owner-secret' };
  const bad = { Authorization: 'Basic ' + btoa('admin:guess') };
  for (let i = 0; i < 10; i++) await call(analytics, 'GET', '/api/admin/analytics', { headers: bad }, env);
  const r = await call(analytics, 'GET', '/api/admin/analytics', { headers: { Authorization: 'Basic ' + btoa('admin:a-long-owner-secret') } }, env);
  assert.equal(r.status, 429);
});

test('tracker caps field sizes and uses server time', async () => {
  const env = { DB: makeD1() };
  const r = await call(track, 'POST', '/api/track', {
    body: { session_id: 's1', element_text: 'x'.repeat(5000), target_href: 'y'.repeat(5000), timestamp: '1999-01-01T00:00:00Z' },
  }, env);
  assert.equal(r.status, 200);
  const row = env.DB._sqlite.prepare('SELECT * FROM clicks').get();
  assert.equal(row.element_text.length, 200);
  assert.equal(row.target_href.length, 500);
  assert.notEqual(row.timestamp, '1999-01-01T00:00:00Z');
});
