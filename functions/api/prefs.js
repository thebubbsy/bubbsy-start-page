/** GET /api/prefs → { prefs, updatedAt }; POST { prefs } → { updatedAt }. Signed-in users only. */
import * as A from '../../lib/cf-accounts.js';

async function currentUser(request, db) {
  await A.ensureSchema(db);
  return A.userForSession(db, A.sessionToken(request));
}

export async function onRequestGet({ request, env }) {
  if (!env.DB) return A.json({ error: 'Accounts are not available on this deployment.' }, 503);
  const user = await currentUser(request, env.DB);
  if (!user) return A.json({ error: 'Not signed in.' }, 401);
  return A.json(await A.getPrefs(env.DB, user.id));
}

export async function onRequestPost({ request, env }) {
  if (!env.DB) return A.json({ error: 'Accounts are not available on this deployment.' }, 503);
  try {
    if (!A.sameOrigin(request)) throw new A.AuthError('Cross-site request refused.', 403);
    const user = await currentUser(request, env.DB);
    if (!user) throw new A.AuthError('Not signed in.', 401);
    const body = await A.readJson(request);
    return A.json(await A.savePrefs(env.DB, user.id, body.prefs));
  } catch (e) {
    if (e instanceof A.AuthError) return A.json({ error: e.message }, e.status);
    console.error('[prefs]', e);
    return A.json({ error: 'Something went wrong on our side. Please try again.' }, 500);
  }
}
