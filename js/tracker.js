/**
 * Anonymous click counter (Cloudflare Pages + D1).
 *
 * Records which buttons and links are used so the site can be improved: element type/id/label,
 * link target and page path, plus (added server-side) IP address, country and browser. Never
 * records what is typed into any field. Disclosed to users in the account window.
 */
(function () {
  'use strict';

  // 1. Session Lifecycle
  let sessionId = sessionStorage.getItem('bubbsy_telemetry_session');
  if (!sessionId) {
    sessionId = 'sess_' + Date.now().toString(36) + '_' + Math.random().toString(36).substring(2, 9);
    try {
      sessionStorage.setItem('bubbsy_telemetry_session', sessionId);
    } catch (e) {}
  }
  window.bubbsySessionId = sessionId;

  // 2. Dispatch Tracking Telemetry Event
  function dispatchClickTelemetry(element) {
    if (!element || element === document.body || element === document.documentElement) return;

    // Never record what people type: for form fields only the field's own label is sent, never
    // its value (search boxes hold investigation targets). Password fields are skipped entirely.
    if (element.type === 'password') return;
    const isField = /^(INPUT|TEXTAREA|SELECT)$/.test(element.tagName) || element.isContentEditable;

    // Find best descriptive text
    let label = isField
      ? (element.getAttribute('aria-label') || element.getAttribute('placeholder') || element.name || element.id || element.tagName).trim()
      : (element.innerText || element.getAttribute('aria-label') || element.title || '').trim();
    if (!label && element.querySelector('span, strong, svg title')) {
      label = (element.querySelector('span, strong, svg title')?.textContent || '').trim();
    }
    label = label.replace(/\s+/g, ' ').slice(0, 120);

    const payload = {
      session_id: sessionId,
      element_tag: element.tagName || '',
      element_id: element.id || '',
      element_classes: typeof element.className === 'string' ? element.className.slice(0, 100) : '',
      element_text: label,
      target_href: element.href || element.getAttribute('data-href') || '',
      page_path: window.location.pathname, // no query string or hash: those can carry searches
      timestamp: new Date().toISOString(),
    };

    const jsonStr = JSON.stringify(payload);

    try {
      if (navigator.sendBeacon) {
        const blob = new Blob([jsonStr], { type: 'application/json' });
        navigator.sendBeacon('/api/track', blob);
      } else {
        fetch('/api/track', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: jsonStr,
          keepalive: true,
        }).catch(() => {});
      }
    } catch (err) {
      // Fail silently without blocking UI
    }
  }

  // 3. Global Delegated Click Listener (Capture phase to guarantee receipt before navigation)
  document.addEventListener(
    'click',
    function (e) {
      if (!e.target) return;
      const interactive =
        e.target.closest(
          'a, button, input, [role="button"], .category-card, .bookmark-item, .shortcut-chip, .ai-recipe-pill, .ai-format-pill, .tab-item'
        ) || e.target;
      dispatchClickTelemetry(interactive);
    },
    { capture: true, passive: true }
  );

})();
