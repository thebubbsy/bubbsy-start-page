/**
 * /api/auth/me | signup | login | google | logout | delete
 * Same contract as accounts.handle_request in accounts.py. Logic lives in lib/cf-accounts.js.
 */
import * as A from '../../../lib/cf-accounts.js';

const ACTIONS = new Set(['me', 'signup', 'login', 'google', 'logout', 'delete']);

function noDb() {
  return A.json({ error: 'Accounts need the D1 database binding (DB) on this deployment.' }, 503);
}

export async function onRequestGet(context) {
  const { request, env, params } = context;
  if (params.action !== 'me') return A.json({ error: 'Not found.' }, 404);
  if (!env.DB) return A.json({ accountsEnabled: false, googleClientId: null, user: null });
  await A.ensureSchema(env.DB);
  const user = await A.userForSession(env.DB, A.sessionToken(request));
  return A.json({ accountsEnabled: true, googleClientId: (env.GOOGLE_CLIENT_ID || '').trim() || null, user });
}

export async function onRequestPost(context) {
  const { request, env, params } = context;
  const action = params.action;
  if (!ACTIONS.has(action) || action === 'me') return A.json({ error: 'Not found.' }, 404);
  if (!env.DB) return noDb();
  const db = env.DB;
  try {
    if (!A.sameOrigin(request)) throw new A.AuthError('Cross-site request refused.', 403);
    await A.ensureSchema(db);
    const body = await A.readJson(request);
    const ip = A.clientIp(request);

    if (action === 'signup' || action === 'login' || action === 'google') {
      await A.checkRateLimit(db, ip, 'login');
      let user;
      try {
        if (action === 'signup') user = await A.signup(db, body.email, body.password);
        else if (action === 'login') user = await A.login(db, body.email, body.password);
        else user = await A.loginWithGoogle(db, env, body.credential);
      } catch (e) {
        if (e instanceof A.AuthError) await A.recordFailedAttempt(db, ip, 'login');
        throw e;
      }
      const token = await A.createSession(db, user.id);
      return A.json({ user, ...(await A.getPrefs(db, user.id)) }, 200,
        { 'Set-Cookie': A.sessionCookie(token, A.SESSION_TTL_SECONDS) });
    }

    const token = A.sessionToken(request);
    if (action === 'logout') {
      await A.destroySession(db, token);
      return A.json({ status: 'signed_out' }, 200, { 'Set-Cookie': A.sessionCookie('', 0) });
    }

    const user = await A.userForSession(db, token);
    if (!user) throw new A.AuthError('Not signed in.', 401);
    await A.deleteUser(db, user.id); // action === 'delete'
    return A.json({ status: 'deleted' }, 200, { 'Set-Cookie': A.sessionCookie('', 0) });
  } catch (e) {
    if (e instanceof A.AuthError) return A.json({ error: e.message }, e.status);
    console.error('[accounts]', action, e);
    return A.json({ error: 'Something went wrong on our side. Please try again.' }, 500);
  }
}
