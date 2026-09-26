/*
 * Optional account & preference sync.
 *
 * An account does one thing: it keeps a copy of the user's display preferences on the server so
 * they follow the user between computers. Preferences always live in localStorage first; the
 * account just mirrors the keys listed in SYNC_KEYS. Nothing else (searches, investigation graph,
 * notes) ever leaves the browser.
 *
 * The whole feature stays invisible unless the server answers /api/auth/me, so opening
 * index.html straight from disk, or hosting it statically, shows no sign-in button at all.
 */
(function () {
  'use strict';

  const SYNC_KEYS = new Set([
    'bubbsy_sort_mode',
    'bubbsy_custom_layout',
    'bubbsy_favorites',
    'bubbsy_theme',
    'bubbsy_typography',
    'bubbsy_ui_mode',
    'bubbsy_settings',
    'bubbsy_user_bookmarks'
  ]);
  const SYNC_PREFIXES = ['widget_collapsed_'];

  // Local bookkeeping, never synced.
  const SYNCED_AT_KEY = 'bubbsy_prefs_synced_at'; // server updatedAt this browser last matched
  const DIRTY_AT_KEY = 'bubbsy_prefs_dirty_at';   // last local change to a synced key
  const OFFER_DISMISSED_KEY = 'bubbsy_sync_offer_dismissed';
  const RELOAD_GUARD_KEY = 'bubbsy_prefs_reloaded_for';
  const PENDING_NOTICE_KEY = 'bubbsy_account_notice';

  const state = { available: false, user: null, googleClientId: null, pushTimer: null, googleReady: false };

  const $ = (id) => document.getElementById(id);

  function isSyncedKey(key) {
    return SYNC_KEYS.has(key) || SYNC_PREFIXES.some(p => String(key).startsWith(p));
  }

  // --- storage helpers (never throw: private windows can block storage) ---
  const rawSet = Storage.prototype.setItem;
  const rawRemove = Storage.prototype.removeItem;
  function lsGet(key) { try { return localStorage.getItem(key); } catch (e) { return null; } }
  function lsSet(key, value) { try { rawSet.call(localStorage, key, value); } catch (e) {} }
  function lsRemove(key) { try { rawRemove.call(localStorage, key); } catch (e) {} }
  function num(key) { return parseInt(lsGet(key) || '0', 10) || 0; }

  // Watch writes to synced keys wherever they happen in the app, so every preference change is
  // mirrored without threading sync calls through the rest of the code.
  function noteLocalChange(key) {
    if (!isSyncedKey(key)) return;
    lsSet(DIRTY_AT_KEY, String(Date.now()));
    schedulePush();
  }
  try {
    // Only real changes count: the app rewrites some keys (e.g. the theme) on every load, and
    // treating those as edits would let a stale browser overwrite newer prefs from another computer.
    Storage.prototype.setItem = function (key, value) {
      const isLocal = this === window.localStorage;
      const prev = isLocal ? this.getItem(key) : null;
      rawSet.call(this, key, value);
      if (isLocal && prev !== String(value)) noteLocalChange(key);
    };
    Storage.prototype.removeItem = function (key) {
      const isLocal = this === window.localStorage;
      const existed = isLocal && this.getItem(key) !== null;
      rawRemove.call(this, key);
      if (existed) noteLocalChange(key);
    };
  } catch (e) {}

  function collectPrefs() {
    const prefs = {};
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (isSyncedKey(key)) prefs[key] = localStorage.getItem(key);
      }
    } catch (e) {}
    return prefs;
  }

  function samePrefs(a, b) {
    const ka = Object.keys(a || {}).sort();
    const kb = Object.keys(b || {}).sort();
    return ka.length === kb.length && ka.every((k, i) => k === kb[i] && a[k] === b[k]);
  }

  // The server copy is a full snapshot: synced keys it lacks are removed locally too.
  function applyPrefs(prefs) {
    Object.keys(collectPrefs()).forEach(key => { if (!(key in prefs)) lsRemove(key); });
    Object.keys(prefs).forEach(key => {
      if (!isSyncedKey(key)) return;
      if (prefs[key] === null) lsRemove(key); else lsSet(key, prefs[key]);
    });
  }

  function reloadWithNotice(message, serverUpdatedAt) {
    try {
      if (sessionStorage.getItem(RELOAD_GUARD_KEY) === String(serverUpdatedAt)) return; // never loop
      sessionStorage.setItem(RELOAD_GUARD_KEY, String(serverUpdatedAt));
      sessionStorage.setItem(PENDING_NOTICE_KEY, message);
    } catch (e) {}
    window.location.reload();
  }

  // --- API ---
  async function api(path, body) {
    const opts = { credentials: 'same-origin', headers: {} };
    if (body !== undefined) {
      opts.method = 'POST';
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
    const res = await fetch(path, opts);
    let data = {};
    try { data = await res.json(); } catch (e) {}
    if (!res.ok) {
      const err = new Error(data.error || `Request failed (${res.status})`);
      err.status = res.status;
      throw err;
    }
    return data;
  }

  function toast(msg, type) {
    if (typeof window.showToast === 'function') window.showToast(msg, type);
  }

  function schedulePush() {
    if (!state.user) return;
    clearTimeout(state.pushTimer);
    state.pushTimer = setTimeout(() => pushPrefs(false), 1200);
  }

  async function pushPrefs(announce) {
    if (!state.user) return;
    clearTimeout(state.pushTimer);
    try {
      const res = await api('/api/prefs', { prefs: collectPrefs() });
      lsSet(SYNCED_AT_KEY, String(res.updatedAt));
      lsRemove(DIRTY_AT_KEY);
      renderSyncStatus();
      if (announce) toast('Preferences saved to your account');
    } catch (e) {
      if (e.status === 401) { setUser(null); return; }
      renderSyncStatus('Could not sync just now — your changes are safe in this browser and will sync next time.');
    }
  }

  // Reconcile this browser with the server copy. Newest side wins.
  async function reconcile(server) {
    const serverAt = server.updatedAt || 0;
    const syncedAt = num(SYNCED_AT_KEY);
    const dirtyAt = num(DIRTY_AT_KEY);

    if (!server.prefs) {
      await pushPrefs(false); // first sync for this account: upload what this browser has
      return;
    }
    if (serverAt > syncedAt && serverAt >= dirtyAt) {
      lsSet(SYNCED_AT_KEY, String(serverAt));
      lsRemove(DIRTY_AT_KEY);
      if (!samePrefs(server.prefs, collectPrefs())) {
        applyPrefs(server.prefs);
        reloadWithNotice('Loaded your saved preferences', serverAt);
      }
      return;
    }
    if (dirtyAt > syncedAt) await pushPrefs(false);
  }

  // --- UI ---
  function setUser(user) {
    state.user = user;
    const label = $('account-btn-label');
    const btn = $('btn-account');
    if (label) label.textContent = user ? 'Synced' : 'Sign in';
    if (btn) {
      btn.classList.toggle('is-signed-in', !!user);
      btn.title = user ? `Signed in as ${user.email} — preferences sync across computers` : 'Sign in to save your preferences across computers';
      btn.setAttribute('aria-label', user ? `Account: signed in as ${user.email}` : 'Account: sign in to sync preferences');
    }
    const out = $('account-signed-out');
    const inn = $('account-signed-in');
    if (out) out.hidden = !!user;
    if (inn) inn.hidden = !user;
    if (user && $('account-email-display')) $('account-email-display').textContent = user.email;
    renderSyncStatus();
  }

  function renderSyncStatus(message) {
    const el = $('account-sync-status');
    if (!el) return;
    if (message) { el.textContent = message; return; }
    const at = num(SYNCED_AT_KEY);
    el.textContent = at ? `Last synced ${new Date(at).toLocaleString()}.` : 'Not synced yet.';
  }

  let authTab = 'login';
  function setTab(tab) {
    authTab = tab;
    document.querySelectorAll('.account-tab').forEach(t => {
      const active = t.getAttribute('data-account-tab') === tab;
      t.classList.toggle('active', active);
      t.setAttribute('aria-selected', String(active));
    });
    $('account-submit').textContent = tab === 'signup' ? 'Create account' : 'Sign in';
    $('account-password').setAttribute('autocomplete', tab === 'signup' ? 'new-password' : 'current-password');
    $('account-password-hint').hidden = tab !== 'signup';
    showError('');
  }

  function showError(msg) {
    const el = $('account-error');
    if (!el) return;
    el.textContent = msg;
    el.hidden = !msg;
  }

  function openAccountModal(tab) {
    const modal = $('modal-account');
    if (!modal) return;
    if (tab) setTab(tab);
    setUser(state.user);
    if (typeof window.openModal === 'function') window.openModal(modal); else modal.classList.add('active');
    if (!state.user) loadGoogle();
  }

  function closeAccountModal() {
    const modal = $('modal-account');
    if (!modal) return;
    if (typeof window.closeModal === 'function') window.closeModal(modal); else modal.classList.remove('active');
  }

  async function afterSignIn(data, isNewAccount) {
    setUser(data.user);
    closeAccountModal();
    if (data.prefs && !isNewAccount) {
      lsSet(SYNCED_AT_KEY, String(data.updatedAt));
      lsRemove(DIRTY_AT_KEY);
      if (!samePrefs(data.prefs, collectPrefs())) {
        applyPrefs(data.prefs);
        reloadWithNotice(`Signed in — loaded your saved preferences`, data.updatedAt);
        return;
      }
      toast(`Signed in as ${data.user.email}`);
    } else {
      await pushPrefs(false);
      toast(isNewAccount ? 'Account created — your preferences are now saved to it' : `Signed in as ${data.user.email}`);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const email = $('account-email').value.trim();
    const password = $('account-password').value;
    if (!email || !password) { showError('Enter your email and password.'); return; }
    const submit = $('account-submit');
    submit.disabled = true;
    showError('');
    try {
      const data = await api(authTab === 'signup' ? '/api/auth/signup' : '/api/auth/login', { email, password });
      $('account-password').value = '';
      await afterSignIn(data, authTab === 'signup');
    } catch (err) {
      showError(err.message);
    } finally {
      submit.disabled = false;
    }
  }

  function loadGoogle() {
    if (!state.googleClientId || state.googleReady) return;
    const wrap = $('account-google-wrap');
    const render = () => {
      if (!window.google || !google.accounts || !google.accounts.id) return;
      google.accounts.id.initialize({
        client_id: state.googleClientId,
        callback: async (resp) => {
          try {
            const data = await api('/api/auth/google', { credential: resp.credential });
            // A Google sign-in may create the account; either way an empty server copy gets this browser's prefs.
            await afterSignIn(data, !data.prefs);
          } catch (err) {
            showError(err.message);
          }
        }
      });
      google.accounts.id.renderButton($('account-google-btn'), { theme: 'filled_black', size: 'large', text: 'continue_with', shape: 'pill', width: 280 });
      state.googleReady = true;
      if (wrap) wrap.hidden = false;
    };
    if (window.google && window.google.accounts) { render(); return; }
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.onload = render;
    script.onerror = () => { if (wrap) wrap.hidden = true; };
    document.head.appendChild(script);
  }

  // Called by the app at moments of heavy customisation (e.g. saving a custom layout).
  function offerSync(context) {
    if (!state.available) return;
    if (state.user) { pushPrefs(true); return; }
    if (lsGet(OFFER_DISMISSED_KEY) === '1' || document.getElementById('sync-offer')) return;

    const card = document.createElement('div');
    card.className = 'sync-offer';
    card.id = 'sync-offer';
    card.setAttribute('role', 'status');
    card.innerHTML = `
      <p><strong>${context || 'Saved in this browser.'}</strong> Want it on your other computers too?
      A free account stores your preferences on our server — that's all it's used for.</p>
      <div class="sync-offer-actions">
        <button type="button" class="btn-icon sync-offer-yes">Create account</button>
        <button type="button" class="btn-icon sync-offer-no">No thanks</button>
      </div>`;
    document.body.appendChild(card);
    card.querySelector('.sync-offer-yes').addEventListener('click', () => { card.remove(); openAccountModal('signup'); });
    card.querySelector('.sync-offer-no').addEventListener('click', () => { card.remove(); lsSet(OFFER_DISMISSED_KEY, '1'); });
    setTimeout(() => card.remove(), 20000);
  }

  function wireUi() {
    $('btn-account')?.addEventListener('click', () => openAccountModal());
    $('form-account')?.addEventListener('submit', handleSubmit);
    document.querySelectorAll('.account-tab').forEach(t => t.addEventListener('click', () => setTab(t.getAttribute('data-account-tab'))));
    $('btn-account-sync')?.addEventListener('click', () => pushPrefs(true));
    $('btn-account-logout')?.addEventListener('click', async () => {
      try { await api('/api/auth/logout', {}); } catch (e) {}
      lsRemove(SYNCED_AT_KEY);
      setUser(null);
      closeAccountModal();
      toast('Signed out — your preferences stay in this browser');
    });
    $('btn-account-delete')?.addEventListener('click', async () => {
      if (!window.confirm('Permanently delete your account and the preferences stored on our server?')) return;
      try {
        await api('/api/auth/delete', {});
        lsRemove(SYNCED_AT_KEY);
        setUser(null);
        closeAccountModal();
        toast('Account deleted. Nothing about you is stored on our server any more.');
      } catch (e) {
        toast(e.message, 'error');
      }
    });
  }

  async function boot() {
    wireUi();
    try {
      const pending = sessionStorage.getItem(PENDING_NOTICE_KEY);
      if (pending) {
        sessionStorage.removeItem(PENDING_NOTICE_KEY);
        setTimeout(() => toast(pending), 600);
      }
    } catch (e) {}

    if (!window.location.protocol.startsWith('http')) return;
    let me;
    try {
      me = await api('/api/auth/me');
    } catch (e) {
      return; // no account backend here (static hosting): keep the feature hidden
    }
    if (!me || !me.accountsEnabled) return;
    state.available = true;
    state.googleClientId = me.googleClientId || null;
    const btn = $('btn-account');
    if (btn) btn.hidden = false;
    setUser(me.user || null);
    if (me.user) {
      try { await reconcile(await api('/api/prefs')); } catch (e) {}
    }
  }

  window.BubbsyAccount = { offerSync, open: openAccountModal, isSignedIn: () => !!state.user };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
