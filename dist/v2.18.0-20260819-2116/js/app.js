/**
 * BUBBSY START PAGE | OSINT COMMAND ENGINE 2.18.0
 * 
 * Production Feature Stack:
 * 1. Voidtools Everything (ES) IPC/HTTP Bridge with Regex & Advanced Syntax
 * 2. Multi-Engine OSINT Pivot Matrix
 * 3. Threat Intel & CVE Live Radar Feed
 * 4. Global Keyboard Command Palette (Ctrl+K)
 * 5. Interactive Visual Investigation Link Graph
 * 6. Incident Workspace Snapshot & Markdown Export
 */

(function () {
  'use strict';

  // --- STATE ---
  let appData = window.BUBBSY_DATA || null;
  let activeSearchMode = 'filter'; // 'filter', 'everything', 'google', etc.
  let activeCategoryGroup = 'all';
  let activeEsFilter = 'all';
  let esStatus = { mode: 'offline', details: '' };
  let currentTheme = localStorage.getItem('bubbsy_theme') || 'default';
  let userBookmarks = JSON.parse(localStorage.getItem('bubbsy_user_bookmarks') || '[]');
  let userFavorites = JSON.parse(localStorage.getItem('bubbsy_favorites') || '[]');
  let hoveredLink = null;
  let radarFeedData = [];
  let investigationGraph = JSON.parse(localStorage.getItem('bubbsy_investigation_graph') || JSON.stringify({
    nodes: [
      { id: 'node_1', label: '1.1.1.1', type: 'ip', x: 250, y: 200, vx: 0, vy: 0, radius: 22, color: '#00f0ff' },
      { id: 'node_2', label: 'cloudflare-dns.com', type: 'domain', x: 420, y: 180, vx: 0, vy: 0, radius: 22, color: '#00ff9d' },
      { id: 'node_3', label: 'AS13335 (Cloudflare AU)', type: 'org', x: 330, y: 320, vx: 0, vy: 0, radius: 24, color: '#f59e0b' }
    ],
    edges: [
      { source: 'node_1', target: 'node_2', label: 'resolves_to' },
      { source: 'node_1', target: 'node_3', label: 'routed_by' }
    ]
  }));

  let settings = JSON.parse(localStorage.getItem('bubbsy_settings') || JSON.stringify({
    esHttpUrl: 'http://127.0.0.1:8080',
    esUsername: '',
    esPassword: '',
    defaultEngine: 'filter'
  }));

  // --- DOM ELEMENTS ---
  const elDashboardGrid = document.getElementById('dashboard-grid');
  const elMainSearch = document.getElementById('main-search');
  const elSearchTabs = document.getElementById('search-mode-tabs');
  const elEngineBadge = document.getElementById('current-engine-label');
  const elBtnSearchExec = document.getElementById('btn-search-exec');
  const elEsPanel = document.getElementById('es-results-panel');
  const elEsResultsList = document.getElementById('es-results-list');
  const elEsResultsCounter = document.getElementById('es-results-counter');
  const elEsStatusDot = document.getElementById('status-dot');
  const elEsStatusText = document.getElementById('es-status-text');
  const elEsStatusIndicator = document.getElementById('es-status-indicator');
  const elWorldClocks = document.getElementById('world-clocks-container');
  const elCategoryRibbon = document.getElementById('category-ribbon');
  const elToastContainer = document.getElementById('toast-container');
  const elBmCategorySelect = document.getElementById('bm-category');

  // New Overlays
  const elModalPalette = document.getElementById('modal-palette');
  const elPaletteInput = document.getElementById('palette-input');
  const elPaletteResults = document.getElementById('palette-results');
  const elModalPivot = document.getElementById('modal-pivot');
  const elPivotInput = document.getElementById('pivot-input');
  const elPivotTypeBadge = document.getElementById('pivot-type-badge');
  const elPivotMatrixActions = document.getElementById('pivot-matrix-actions');
  const elModalRadar = document.getElementById('modal-radar');
  const elRadarItemsList = document.getElementById('radar-items-list');
  const elRadarSearchInput = document.getElementById('radar-search-input');
  const elModalGraph = document.getElementById('modal-graph');
  const elCanvas = document.getElementById('investigation-canvas');
  const elModalExport = document.getElementById('modal-export');

  // --- INIT ---
  async function init() {
    applyTheme(currentTheme);

    // If served from local server, fetch latest data, check ES status and fetch radar
    if (window.location.protocol.startsWith('http')) {
      try {
        const res = await fetch('/api/data');
        if (res.ok) {
          appData = await res.json();
        }
      } catch (e) {
        console.warn('Using bundled offline dataset:', e);
      }
    }

    if (!appData) {
      showToast('⚠️ Failed to load OSINT dataset. Check data/osint_data.json', 'error');
      return;
    }

    renderDashboard();
    renderWorldClocks();
    setInterval(updateWorldClocks, 1000);
    checkEverythingStatus();
    populateCategorySelect();
    setupEventListeners();
    fetchThreatRadarFeed();

    // Set default search engine from settings
    if (settings.defaultEngine && settings.defaultEngine !== 'filter') {
      setSearchMode(settings.defaultEngine);
    }
  }

  // --- THEMES ---
  function applyTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('bubbsy_theme', theme);
  }

  function cycleTheme() {
    const themes = ['default', 'amber', 'matrix', 'dracula'];
    const nextIdx = (themes.indexOf(currentTheme) + 1) % themes.length;
    applyTheme(themes[nextIdx]);
    showToast(`HUD Theme: ${themes[nextIdx].toUpperCase()}`);
  }

  // --- TOAST NOTIFICATIONS ---
  function showToast(msg, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast-notice';
    toast.innerHTML = `<span>${msg}</span>`;
    elToastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 2200);
  }

  // --- WORLD CLOCKS ---
  function renderWorldClocks() {
    if (!appData.world_clocks || !appData.world_clocks.length) return;
    elWorldClocks.innerHTML = appData.world_clocks.map(c => `
      <div class="clock-item" data-tz="${c.timezone}">
        <span class="clock-city">${c.name}</span>
        <span class="clock-time">--:--:--</span>
      </div>
    `).join('');
    updateWorldClocks();
  }

  function updateWorldClocks() {
    const clockItems = elWorldClocks.querySelectorAll('.clock-item');
    const now = new Date();
    clockItems.forEach(item => {
      const tz = item.getAttribute('data-tz');
      try {
        const timeStr = new Intl.DateTimeFormat('en-US', {
          timeZone: tz,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        }).format(now);
        item.querySelector('.clock-time').textContent = timeStr;
      } catch (e) {
        item.querySelector('.clock-time').textContent = now.toTimeString().split(' ')[0];
      }
    });
  }

  // --- DASHBOARD RENDERING ---
  function renderDashboard() {
    elDashboardGrid.innerHTML = '';
    const columns = appData.columns || [];

    columns.forEach((col, colIdx) => {
      const colDiv = document.createElement('div');
      colDiv.className = 'column-stack';
      colDiv.setAttribute('data-col-index', colIdx);

      (col.widgets || []).forEach(w => {
        const card = createWidgetCard(w);
        colDiv.appendChild(card);
      });

      elDashboardGrid.appendChild(colDiv);
    });

    // Update counters
    document.getElementById('stats-total-tools').textContent = appData.total_links || '1,699';
    document.getElementById('stats-total-categories').textContent = appData.total_widgets || '89';
  }

  function createWidgetCard(w) {
    const card = document.createElement('div');
    card.className = 'widget-card';
    card.setAttribute('data-widget-id', w.id);
    card.setAttribute('data-group', w.group || 'tools_general');
    card.setAttribute('data-title', (w.title || '').toLowerCase());

    const isCollapsed = localStorage.getItem(`widget_collapsed_${w.id}`) === 'true';
    if (isCollapsed) card.classList.add('collapsed');

    // Header
    const header = document.createElement('div');
    header.className = 'widget-header';
    header.innerHTML = `
      <div class="widget-title-group">
        <span class="widget-indicator" style="background:${w.color || 'var(--accent-cyan)'};"></span>
        <h2 class="widget-title">${escapeHtml(w.title)}</h2>
        <span class="widget-badge">${(w.links || []).length}</span>
      </div>
      <button class="widget-collapse-btn" title="Collapse/Expand widget">▼</button>
    `;

    header.addEventListener('click', (e) => {
      card.classList.toggle('collapsed');
      localStorage.setItem(`widget_collapsed_${w.id}`, card.classList.contains('collapsed'));
    });

    // Body
    const body = document.createElement('div');
    body.className = 'widget-body';

    const ul = document.createElement('ul');
    ul.className = 'link-list';

    (w.links || []).forEach(link => {
      const li = document.createElement('li');
      li.className = 'link-item';
      li.setAttribute('data-link-title', (link.title || '').toLowerCase());
      li.setAttribute('data-link-desc', (link.description || '').toLowerCase());
      li.setAttribute('data-link-url', (link.url || '').toLowerCase());
      li.setAttribute('data-link-id', link.id || '');

      const isPinned = userFavorites.some(f => f.url === link.url || (link.id && f.id === link.id));
      if (isPinned) li.classList.add('is-pinned');

      const domain = link.domain || '';
      const initial = domain ? domain.charAt(0).toUpperCase() : '⚡';

      li.innerHTML = `
        <a href="${escapeHtml(link.url)}" target="_blank" rel="noopener noreferrer" class="link-anchor" title="${escapeHtml(link.description || link.title)}">
          <img 
            src="${escapeHtml(link.favicon)}" 
            class="link-favicon" 
            alt="" 
            loading="lazy"
            onerror="this.style.display='none'; this.nextElementSibling.style.display='inline-flex';"
          >
          <span class="link-fallback-icon" style="display:none;">${initial}</span>
          <span class="link-title">${escapeHtml(link.title)}</span>
          <span class="link-pin-indicator" style="${isPinned ? '' : 'display:none;'}">⭐</span>
        </a>
      `;

      // Track hovered link for mouse-hover keyboard shortcuts ('C' to copy URL, 'F'/'P' to pin/favorite)
      li.addEventListener('mouseenter', () => {
        hoveredLink = {
          url: link.url,
          title: link.title,
          description: link.description,
          id: link.id,
          element: li
        };
      });

      li.addEventListener('mouseleave', () => {
        if (hoveredLink && hoveredLink.element === li) {
          hoveredLink = null;
        }
      });

      ul.appendChild(li);
    });

    body.appendChild(ul);
    card.appendChild(header);
    card.appendChild(body);

    return card;
  }

  function populateCategorySelect() {
    elBmCategorySelect.innerHTML = '';
    const columns = appData.columns || [];
    columns.forEach(col => {
      col.widgets.forEach(w => {
        const opt = document.createElement('option');
        opt.value = w.id;
        opt.textContent = w.title;
        elBmCategorySelect.appendChild(opt);
      });
    });
  }

  // --- EVENT LISTENERS ---
  function setupEventListeners() {
    // Search input
    elMainSearch.addEventListener('input', (e) => {
      handleSearchInput(e.target.value);
    });

    elMainSearch.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        executeSearch();
      } else if (e.key === 'Escape') {
        clearSearch();
      }
    });

    elBtnSearchExec.addEventListener('click', executeSearch);

    // Search Tabs
    elSearchTabs.addEventListener('click', (e) => {
      const tab = e.target.closest('.search-tab');
      if (!tab) return;
      const mode = tab.getAttribute('data-mode');
      setSearchMode(mode);
    });

    // Category Ribbon Filter
    elCategoryRibbon.addEventListener('click', (e) => {
      const pill = e.target.closest('.cat-pill');
      if (!pill) return;
      document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeCategoryGroup = pill.getAttribute('data-filter-group');
      filterByCategory(activeCategoryGroup);
    });

    // Bang chips in ribbon
    document.querySelectorAll('.bang-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const bang = chip.getAttribute('data-bang');
        elMainSearch.value = bang;
        elMainSearch.focus();
        handleSearchInput(bang);
      });
    });

    // Advanced Everything Syntax Pills
    document.querySelectorAll('.es-syntax-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const syn = pill.getAttribute('data-syntax');
        setSearchMode('everything');
        elMainSearch.value = syn + ' ';
        elMainSearch.focus();
        runEverythingSearch(elMainSearch.value.trim());
      });
    });

    // Action buttons in Top Nav
    document.getElementById('btn-toggle-es').addEventListener('click', () => {
      if (activeSearchMode === 'everything') {
        setSearchMode('filter');
      } else {
        setSearchMode('everything');
        elMainSearch.focus();
      }
    });

    document.getElementById('btn-palette').addEventListener('click', openCommandPalette);
    document.getElementById('btn-open-pivot').addEventListener('click', () => openPivotMatrix());
    document.getElementById('btn-open-radar').addEventListener('click', openThreatRadar);
    document.getElementById('btn-open-graph').addEventListener('click', openInvestigationGraph);
    document.getElementById('btn-open-export').addEventListener('click', openSessionExport);

    document.getElementById('btn-theme-picker').addEventListener('click', cycleTheme);
    document.getElementById('btn-custom-bookmark').addEventListener('click', () => {
      document.getElementById('modal-custom-bookmark').classList.add('active');
    });

    document.getElementById('btn-close-bm').addEventListener('click', () => {
      document.getElementById('modal-custom-bookmark').classList.remove('active');
    });
    document.getElementById('btn-cancel-bm').addEventListener('click', () => {
      document.getElementById('modal-custom-bookmark').classList.remove('active');
    });

    document.getElementById('form-custom-bookmark').addEventListener('submit', handleAddCustomBookmark);

    // Settings Modal
    document.getElementById('btn-settings').addEventListener('click', () => {
      document.getElementById('cfg-es-url').value = settings.esHttpUrl || 'http://127.0.0.1:8080';
      document.getElementById('cfg-es-user').value = settings.esUsername || '';
      document.getElementById('cfg-es-pass').value = settings.esPassword || '';
      document.getElementById('cfg-default-engine').value = settings.defaultEngine || 'filter';
      document.getElementById('modal-settings').classList.add('active');
    });

    document.getElementById('btn-close-settings').addEventListener('click', () => {
      document.getElementById('modal-settings').classList.remove('active');
    });

    document.getElementById('btn-toggle-pass-visibility').addEventListener('click', () => {
      const passInput = document.getElementById('cfg-es-pass');
      const btn = document.getElementById('btn-toggle-pass-visibility');
      if (passInput.type === 'password') {
        passInput.type = 'text';
        btn.textContent = '🔒';
      } else {
        passInput.type = 'password';
        btn.textContent = '👁️';
      }
    });

    document.getElementById('btn-test-es-conn').addEventListener('click', handleTestEverythingConnection);

    document.getElementById('btn-save-settings').addEventListener('click', () => {
      settings.esHttpUrl = document.getElementById('cfg-es-url').value.trim() || 'http://127.0.0.1:8080';
      settings.esUsername = document.getElementById('cfg-es-user').value.trim();
      settings.esPassword = document.getElementById('cfg-es-pass').value.trim();
      settings.defaultEngine = document.getElementById('cfg-default-engine').value;
      localStorage.setItem('bubbsy_settings', JSON.stringify(settings));
      document.getElementById('modal-settings').classList.remove('active');
      showToast('Settings saved successfully!');
      checkEverythingStatus();
    });

    document.getElementById('btn-export-backup').addEventListener('click', exportBackupJson);
    document.getElementById('btn-reset-default').addEventListener('click', () => {
      if (confirm('Reset all bookmarks and settings to factory defaults?')) {
        localStorage.clear();
        location.reload();
      }
    });

    // ES Filter Chips in panel
    document.querySelectorAll('.es-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.es-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeEsFilter = btn.getAttribute('data-es-filter');
        if (elMainSearch.value.trim()) {
          runEverythingSearch(elMainSearch.value.trim());
        }
      });
    });

    // Global Hotkeys & Hover Actions
    window.addEventListener('keydown', (e) => {
      const isInputActive = document.activeElement && (
        document.activeElement.tagName === 'INPUT' || 
        document.activeElement.tagName === 'TEXTAREA' || 
        document.activeElement.isContentEditable
      );

      // Global Command Palette shortcut (Ctrl+K or Cmd+K)
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        openCommandPalette();
        return;
      }

      // Search focus hotkeys
      if (!isInputActive) {
        if (e.key === '/') {
          e.preventDefault();
          elMainSearch.focus();
          elMainSearch.select();
          return;
        }
      }

      // Mouse-hover shortcut actions: 'C' to copy URL, 'F' or 'P' to pin/favorite
      if (hoveredLink && !isInputActive) {
        const key = e.key.toLowerCase();
        
        if (key === 'c') {
          e.preventDefault();
          navigator.clipboard.writeText(hoveredLink.url);
          
          hoveredLink.element.classList.remove('pulse-copy');
          void hoveredLink.element.offsetWidth; // trigger DOM reflow
          hoveredLink.element.classList.add('pulse-copy');
          
          showToast(`📋 Copied URL: ${hoveredLink.title}`);
        } else if (key === 'f' || key === 'p') {
          e.preventDefault();
          toggleFavoriteLink(hoveredLink);
        }
      }
    });
  }

  function toggleFavoriteLink(linkObj) {
    const idx = userFavorites.findIndex(f => f.url === linkObj.url || (linkObj.id && f.id === linkObj.id));
    const isNowPinned = (idx === -1);

    if (isNowPinned) {
      userFavorites.push({
        id: linkObj.id || Date.now(),
        title: linkObj.title,
        url: linkObj.url,
        description: linkObj.description || ''
      });
      linkObj.element.classList.add('is-pinned');
      const pinIcon = linkObj.element.querySelector('.link-pin-indicator');
      if (pinIcon) pinIcon.style.display = '';
      showToast(`⭐ Pinned: ${linkObj.title}`);
    } else {
      userFavorites.splice(idx, 1);
      linkObj.element.classList.remove('is-pinned');
      const pinIcon = linkObj.element.querySelector('.link-pin-indicator');
      if (pinIcon) pinIcon.style.display = 'none';
      showToast(`Unpinned: ${linkObj.title}`);
    }

    localStorage.setItem('bubbsy_favorites', JSON.stringify(userFavorites));

    linkObj.element.classList.remove('pulse-pin');
    void linkObj.element.offsetWidth;
    linkObj.element.classList.add('pulse-pin');

    const activePill = document.querySelector('.cat-pill.active');
    if (activePill && activePill.getAttribute('data-filter-group') === 'favorites') {
      filterByCategory('favorites');
    }
  }

  function setSearchMode(mode) {
    activeSearchMode = mode;
    document.querySelectorAll('.search-tab').forEach(t => {
      t.classList.toggle('active', t.getAttribute('data-mode') === mode);
    });

    if (mode === 'filter') {
      elEngineBadge.textContent = '🔍 FILTER';
      elEngineBadge.style.color = 'var(--accent-cyan)';
      elMainSearch.placeholder = 'Fuzzy search 1,699+ OSINT, Australian & AI tools... (Press / to focus, Ctrl+K for Palette)';
      elEsPanel.classList.remove('visible');
    } else if (mode === 'everything') {
      elEngineBadge.textContent = '⚡ EVERYTHING';
      elEngineBadge.style.color = 'var(--accent-green)';
      elMainSearch.placeholder = 'Instant search local files & dossiers with Voidtools Everything...';
      elEsPanel.classList.add('visible');
      if (elMainSearch.value.trim()) {
        runEverythingSearch(elMainSearch.value.trim());
      }
    } else if (['chatgpt', 'claude', 'deepseek', 'perplexity', 'genspark', 'phind', 'huggingface'].includes(mode)) {
      elEngineBadge.textContent = `AI: ${mode.toUpperCase()}`;
      elEngineBadge.style.color = 'var(--accent-green)';
      elMainSearch.placeholder = `Query ${mode.toUpperCase()}... (Press Enter)`;
      elEsPanel.classList.remove('visible');
    } else {
      elEngineBadge.textContent = `🌐 ${mode.toUpperCase()}`;
      elEngineBadge.style.color = 'var(--accent-blue)';
      elMainSearch.placeholder = `Search with ${mode.toUpperCase()}... (Press Enter)`;
      elEsPanel.classList.remove('visible');
    }
  }

  let searchDebounceTimer = null;
  function handleSearchInput(val) {
    clearTimeout(searchDebounceTimer);

    // Check for Bang syntax (e.g., !es, !abn, !trove, !austlii, !gpt, !claude, !deepseek, !ppx, !shodan, !dork)
    if (val.startsWith('!')) {
      const match = val.match(/^!([a-zA-Z0-9]+)\s*(.*)$/);
      if (match) {
        const bang = match[1].toLowerCase();
        const query = match[2];
        const bangMap = {
          'es': 'everything',
          'everything': 'everything',
          'gpt': 'chatgpt',
          'chatgpt': 'chatgpt',
          'claude': 'claude',
          'sonnet': 'claude',
          'deepseek': 'deepseek',
          'r1': 'deepseek',
          'ppx': 'perplexity',
          'perplexity': 'perplexity',
          'genspark': 'genspark',
          'spark': 'genspark',
          'phind': 'phind',
          'hf': 'huggingface',
          'huggingface': 'huggingface',
          'abn': 'abn',
          'abr': 'abn',
          'trove': 'trove',
          'nla': 'trove',
          'austlii': 'austlii',
          'law': 'austlii',
          'g': 'google',
          'google': 'google',
          'dork': 'google',
          'ddg': 'duckduckgo',
          'shodan': 'shodan',
          'censys': 'censys',
          'vt': 'virustotal',
          'gh': 'github',
          'archive': 'archive'
        };
        if (bangMap[bang] && bangMap[bang] !== activeSearchMode) {
          setSearchMode(bangMap[bang]);
          elMainSearch.value = query;
          val = query;
        }
      }
    }

    if (activeSearchMode === 'everything') {
      searchDebounceTimer = setTimeout(() => {
        runEverythingSearch(val.trim());
      }, 180);
    } else if (activeSearchMode === 'filter') {
      searchDebounceTimer = setTimeout(() => {
        filterDashboardBookmarks(val.trim());
      }, 100);
    }
  }

  function executeSearch() {
    const query = elMainSearch.value.trim();
    if (!query) return;

    if (activeSearchMode === 'everything') {
      runEverythingSearch(query);
      return;
    }

    if (activeSearchMode === 'filter') {
      filterDashboardBookmarks(query);
      return;
    }

    // Web Search Engine Launch
    const engine = (appData.search_engines || []).find(e => e.id === activeSearchMode);
    if (engine && engine.url) {
      const targetUrl = engine.url.replace('%s', encodeURIComponent(query));
      window.open(targetUrl, '_blank', 'noopener,noreferrer');
    } else {
      // Default to Google
      window.open(`https://www.google.com/search?q=${encodeURIComponent(query)}`, '_blank', 'noopener,noreferrer');
    }
  }

  function clearSearch() {
    elMainSearch.value = '';
    filterDashboardBookmarks('');
    elEsPanel.classList.remove('visible');
    elMainSearch.blur();
  }

  // --- CLIENT FUZZY FILTER ---
  function filterDashboardBookmarks(query) {
    const q = query.toLowerCase();
    const cards = document.querySelectorAll('.widget-card');

    if (!q) {
      cards.forEach(card => {
        card.classList.remove('dimmed', 'highlight');
        card.style.display = '';
        card.querySelectorAll('.link-item').forEach(li => {
          li.style.display = '';
          const titleSpan = li.querySelector('.link-title');
          if (titleSpan) titleSpan.innerHTML = escapeHtml(titleSpan.textContent);
        });
      });
      return;
    }

    let matchCount = 0;

    cards.forEach(card => {
      const cardTitle = card.getAttribute('data-title') || '';
      const links = card.querySelectorAll('.link-item');
      let cardHasMatch = false;

      links.forEach(li => {
        const linkTitle = li.getAttribute('data-link-title') || '';
        const linkDesc = li.getAttribute('data-link-desc') || '';
        const linkUrl = li.getAttribute('data-link-url') || '';

        const isMatch = linkTitle.includes(q) || linkDesc.includes(q) || linkUrl.includes(q) || cardTitle.includes(q);

        if (isMatch) {
          cardHasMatch = true;
          matchCount++;
          li.style.display = '';
          const titleSpan = li.querySelector('.link-title');
          if (titleSpan) {
            titleSpan.innerHTML = highlightMatch(titleSpan.textContent, q);
          }
        } else {
          li.style.display = 'none';
        }
      });

      if (cardHasMatch) {
        card.style.display = '';
        card.classList.remove('dimmed', 'collapsed');
        card.classList.add('highlight');
      } else {
        card.style.display = 'none';
      }
    });

    if (matchCount === 0 && q) {
      showToast(`No local tools matched "${query}". Try Web Search tab.`, 'info');
    }
  }

  function filterByCategory(group) {
    const cards = document.querySelectorAll('.widget-card');
    cards.forEach(card => {
      if (group === 'all') {
        card.style.display = '';
        card.classList.remove('dimmed');
        card.querySelectorAll('.link-item').forEach(li => li.style.display = '');
      } else if (group === 'favorites') {
        const pinnedLinks = card.querySelectorAll('.link-item.is-pinned');
        if (pinnedLinks.length > 0) {
          card.style.display = '';
          card.classList.remove('dimmed');
          card.querySelectorAll('.link-item').forEach(li => {
            li.style.display = li.classList.contains('is-pinned') ? '' : 'none';
          });
        } else {
          card.style.display = 'none';
        }
      } else {
        const cardGroup = card.getAttribute('data-group');
        card.style.display = (cardGroup === group) ? '' : 'none';
        card.classList.remove('dimmed');
        card.querySelectorAll('.link-item').forEach(li => li.style.display = '');
      }
    });
  }

  function highlightMatch(text, query) {
    if (!query) return escapeHtml(text);
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return escapeHtml(text).replace(regex, '<mark class="search-match">$1</mark>');
  }

  // --- VOIDTOOLS EVERYTHING (ES) SEARCH ENGINE ---
  async function checkEverythingStatus() {
    elEsStatusText.textContent = 'DETECTING...';
    elEsStatusDot.className = 'status-dot';

    const p = new URLSearchParams({
      http_url: settings.esHttpUrl || 'http://127.0.0.1:8080',
      user: settings.esUsername || '',
      pass: settings.esPassword || ''
    });

    try {
      const res = await fetch(`/api/es/status?${p.toString()}`);
      if (res.ok) {
        const data = await res.json();
        esStatus = data;
        if (data.mode === 'http_server') {
          elEsStatusText.textContent = 'ONLINE (HTTP)';
          elEsStatusText.style.color = 'var(--accent-green)';
          elEsStatusDot.className = 'status-dot online';
        } else if (data.mode === 'auth_required' || data.auth_required) {
          elEsStatusText.textContent = 'AUTH REQUIRED';
          elEsStatusText.style.color = 'var(--accent-amber)';
          elEsStatusDot.className = 'status-dot ipc';
          elEsStatusIndicator.title = 'Click to configure Everything username & password';
        } else if (data.mode === 'cli_ipc') {
          elEsStatusText.textContent = 'ONLINE (CLI IPC)';
          elEsStatusText.style.color = 'var(--accent-amber)';
          elEsStatusDot.className = 'status-dot ipc';
        } else {
          elEsStatusText.textContent = 'STANDBY';
          elEsStatusText.style.color = 'var(--text-muted)';
          elEsStatusDot.className = 'status-dot';
        }
        return;
      }
    } catch (e) {
      // Direct browser fallback test
      try {
        const headers = {};
        if (settings.esUsername || settings.esPassword) {
          headers['Authorization'] = 'Basic ' + btoa(unescape(encodeURIComponent((settings.esUsername || '') + ':' + (settings.esPassword || ''))));
        }
        const res = await fetch(`${(settings.esHttpUrl || 'http://127.0.0.1:8080').replace(/\/+$/, '')}/?search=&json=1&count=1`, { headers });
        if (res.ok) {
          elEsStatusText.textContent = 'ONLINE (DIRECT)';
          elEsStatusText.style.color = 'var(--accent-green)';
          elEsStatusDot.className = 'status-dot online';
          return;
        } else if (res.status === 401) {
          elEsStatusText.textContent = 'AUTH REQUIRED';
          elEsStatusText.style.color = 'var(--accent-amber)';
          elEsStatusDot.className = 'status-dot ipc';
          return;
        }
      } catch (err) {}
    }

    elEsStatusText.textContent = 'STANDBY';
    elEsStatusDot.className = 'status-dot';
  }

  async function runEverythingSearch(query) {
    if (!query) {
      elEsResultsList.innerHTML = '<div class="es-empty-state">Type a query above to search all local files via Voidtools Everything.</div>';
      elEsResultsCounter.textContent = '(0 files)';
      return;
    }

    elEsResultsList.innerHTML = '<div class="es-empty-state" style="color:var(--accent-green);">⚡ Searching Voidtools Everything index...</div>';

    // Apply Filter presets
    let augmentedQuery = query;
    if (activeEsFilter === 'docs') augmentedQuery += ' ext:pdf;docx;doc;txt;xlsx;csv;pptx;md';
    else if (activeEsFilter === 'data') augmentedQuery += ' ext:json;py;js;html;css;sql;xml;yaml;yml';
    else if (activeEsFilter === 'archives') augmentedQuery += ' ext:zip;7z;rar;tar;gz;iso';
    else if (activeEsFilter === 'media') augmentedQuery += ' ext:jpg;jpeg;png;gif;mp4;mkv;avi;mp3;wav';

    try {
      let results = [];
      let total = 0;

      // Primary: query local backend proxy
      if (window.location.protocol.startsWith('http')) {
        const p = new URLSearchParams({
          q: augmentedQuery,
          max: '50',
          http_url: settings.esHttpUrl || 'http://127.0.0.1:8080',
          user: settings.esUsername || '',
          pass: settings.esPassword || ''
        });
        const url = `/api/es/search?${p.toString()}`;
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          if (data.source === 'auth_required') {
            elEsResultsList.innerHTML = `
              <div class="es-empty-state" style="color:var(--accent-amber);">
                <p style="font-size:1rem;font-weight:700;">🔒 Authentication Required (HTTP 401)</p>
                <p style="font-size:0.85rem;margin:8px 0;">Your Voidtools Everything HTTP Server requires credentials.</p>
                <button class="btn-search-exec" onclick="document.getElementById('btn-settings').click();" style="margin-top:8px;">
                  Open Settings to Enter Credentials
                </button>
              </div>
            `;
            elEsResultsCounter.textContent = '(auth required)';
            return;
          }
          results = data.results || [];
          total = data.total || results.length;
        }
      } else {
        // Direct browser query to Everything HTTP Server
        const headers = {};
        if (settings.esUsername || settings.esPassword) {
          headers['Authorization'] = 'Basic ' + btoa(unescape(encodeURIComponent((settings.esUsername || '') + ':' + (settings.esPassword || ''))));
        }
        const url = `${(settings.esHttpUrl || 'http://127.0.0.1:8080').replace(/\/+$/, '')}/?search=${encodeURIComponent(augmentedQuery)}&json=1&count=50`;
        const res = await fetch(url, { headers });
        if (res.status === 401) {
          elEsResultsList.innerHTML = `
            <div class="es-empty-state" style="color:var(--accent-amber);">
              <p style="font-size:1rem;font-weight:700;">🔒 Authentication Required (HTTP 401)</p>
              <button class="btn-search-exec" onclick="document.getElementById('btn-settings').click();" style="margin-top:8px;">
                Open Settings to Enter Credentials
              </button>
            </div>
          `;
          elEsResultsCounter.textContent = '(auth required)';
          return;
        }
        if (res.ok) {
          const data = await res.json();
          results = (data.results || []).map(r => ({
            name: r.name,
            path: r.path,
            full_path: r.path ? `${r.path}\\${r.name}` : r.name,
            size: r.size,
            date_modified: r.date_modified,
            is_folder: r.type === 'folder',
            ext: (r.name.split('.').pop() || '').toLowerCase()
          }));
          total = data.totalResults || results.length;
        }
      }

      renderEverythingResults(results, total, query);
    } catch (e) {
      elEsResultsList.innerHTML = `<div class="es-empty-state" style="color:#f43f5e;">⚠️ Error connecting to Everything search backend: ${escapeHtml(e.message)}</div>`;
    }
  }

  function renderEverythingResults(results, total, query) {
    elEsResultsCounter.textContent = `(${total.toLocaleString()} files)`;

    if (!results || !results.length) {
      elEsResultsList.innerHTML = `<div class="es-empty-state">No local files found matching "<strong>${escapeHtml(query)}</strong>"</div>`;
      return;
    }

    elEsResultsList.innerHTML = results.map(item => {
      const ext = item.ext || (item.is_folder ? 'DIR' : 'FILE');
      const iconClass = item.is_folder ? 'es-file-icon folder' : 'es-file-icon';
      return `
        <div class="es-result-row" data-file-path="${escapeHtml(item.full_path)}">
          <div class="es-file-info">
            <div class="${iconClass}">${escapeHtml(ext.slice(0, 4).toUpperCase())}</div>
            <div class="es-file-names">
              <div class="es-file-name" title="${escapeHtml(item.name)}">${highlightMatch(item.name, query)}</div>
              <div class="es-file-path" title="${escapeHtml(item.path)}">${escapeHtml(item.path)}</div>
            </div>
          </div>
          <div class="es-actions">
            <button class="btn-es-action btn-open-file" title="Launch / Open file in default application">Open</button>
            <button class="btn-es-action btn-reveal-file" title="Reveal in Windows Explorer">Explorer</button>
            <button class="btn-es-action btn-copy-path" title="Copy absolute path">Copy</button>
          </div>
        </div>
      `;
    }).join('');

    // Attach row actions
    elEsResultsList.querySelectorAll('.es-result-row').forEach(row => {
      const filePath = row.getAttribute('data-file-path');
      row.querySelector('.btn-open-file').addEventListener('click', () => handleOpenFile(filePath, 'open'));
      row.querySelector('.btn-reveal-file').addEventListener('click', () => handleOpenFile(filePath, 'explorer'));
      row.querySelector('.btn-copy-path').addEventListener('click', () => {
        navigator.clipboard.writeText(filePath);
        showToast('Path copied to clipboard!');
      });
    });
  }

  async function handleOpenFile(filePath, action = 'open') {
    if (!window.location.protocol.startsWith('http')) {
      showToast('Opening files via OS requires running through local server (start_bubbsy.bat)', 'error');
      return;
    }
    try {
      const res = await fetch('/api/es/open', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: filePath, action: action })
      });
      const data = await res.json();
      if (res.ok) {
        showToast(action === 'explorer' ? 'Revealed in Windows Explorer' : 'File opened in default viewer');
      } else {
        showToast(`Failed: ${data.error}`, 'error');
      }
    } catch (e) {
      showToast(`Error opening file: ${e.message}`, 'error');
    }
  }

  async function handleTestEverythingConnection() {
    const statusMsg = document.getElementById('es-test-status-msg');
    statusMsg.textContent = 'Testing connection...';
    statusMsg.style.color = 'var(--text-muted)';

    const httpUrl = document.getElementById('cfg-es-url').value.trim() || 'http://127.0.0.1:8080';
    const user = document.getElementById('cfg-es-user').value.trim();
    const pass = document.getElementById('cfg-es-pass').value.trim();

    const p = new URLSearchParams({
      http_url: httpUrl,
      user: user,
      pass: pass
    });

    try {
      const res = await fetch(`/api/es/status?${p.toString()}`);
      if (res.ok) {
        const data = await res.json();
        if (data.http_ok) {
          statusMsg.textContent = '✅ Connected successfully to Everything HTTP server!';
          statusMsg.style.color = 'var(--accent-green)';
        } else if (data.auth_required) {
          statusMsg.textContent = '⚠️ HTTP 401 Unauthorized: Invalid username or password.';
          statusMsg.style.color = 'var(--accent-amber)';
        } else if (data.cli_ok) {
          statusMsg.textContent = '✅ Connected via es.exe CLI IPC bridge.';
          statusMsg.style.color = 'var(--accent-green)';
        } else {
          statusMsg.textContent = `❌ Offline: ${data.details.http || data.details.cli || 'Could not connect'}`;
          statusMsg.style.color = '#f43f5e';
        }
      }
    } catch (e) {
      statusMsg.textContent = `❌ Connection error: ${e.message}`;
      statusMsg.style.color = '#f43f5e';
    }
  }

  // =========================================================================
  // 1. GLOBAL COMMAND PALETTE (CTRL+K)
  // =========================================================================
  function openCommandPalette() {
    elModalPalette.classList.add('active');
    elPaletteInput.value = '';
    renderPaletteResults('');
    setTimeout(() => elPaletteInput.focus(), 50);
  }

  let paletteSelectedIndex = 0;
  function renderPaletteResults(query) {
    const q = query.toLowerCase().trim();
    const items = [];

    // 1. Core Quick Actions
    const actions = [
      { id: 'act_dorks', title: '🎯 Threat Dork & Attack Surface Generator', category: 'ACTIONS', icon: '🎯', action: () => openDorkGenerator() },
      { id: 'act_geo', title: '📍 Australian Cadastre & Geo-Coordinate Recon', category: 'ACTIONS', icon: '📍', action: () => openGeoRecon() },
      { id: 'act_pivot', title: '🎯 Open OSINT Pivot Matrix', category: 'ACTIONS', icon: '🎯', action: () => openPivotMatrix() },
      { id: 'act_radar', title: '📡 Open Threat Intel & CVE Live Radar', category: 'ACTIONS', icon: '📡', action: () => openThreatRadar() },
      { id: 'act_graph', title: '🕸️ Open Visual Investigation Link Graph', category: 'ACTIONS', icon: '🕸️', action: () => openInvestigationGraph() },
      { id: 'act_export', title: '📦 Export Incident Session & Markdown Dossier', category: 'ACTIONS', icon: '📦', action: () => openSessionExport() },
      { id: 'act_tour', title: '❓ Replay Interactive Mission Briefing Tour', category: 'ACTIONS', icon: '❓', action: () => startOnboardingTour() },
      { id: 'act_theme', title: '🎨 Switch HUD Theme (Cyber / Matrix / Dracula)', category: 'ACTIONS', icon: '🎨', action: () => cycleTheme() },
      { id: 'act_es', title: '⚡ Voidtools Everything Local Search', category: 'ACTIONS', icon: '⚡', action: () => { setSearchMode('everything'); elMainSearch.focus(); } }
    ];

    actions.forEach(a => {
      if (!q || a.title.toLowerCase().includes(q)) items.push(a);
    });

    // 2. Search over all tools across all categories
    if (appData && appData.columns) {
      appData.columns.forEach(col => {
        (col.widgets || []).forEach(w => {
          (w.links || []).forEach(link => {
            if (!q || link.title.toLowerCase().includes(q) || (link.description && link.description.toLowerCase().includes(q)) || w.title.toLowerCase().includes(q)) {
              items.push({
                id: `tool_${link.url}`,
                title: link.title,
                category: w.title,
                url: link.url,
                icon: link.title.startsWith('[AUS]') ? '🇦🇺' : (w.group === 'ai_hub' ? '🤖' : '🌐'),
                action: () => window.open(link.url, '_blank', 'noopener,noreferrer')
              });
            }
          });
        });
      });
    }

    paletteSelectedIndex = 0;
    const renderLimit = q ? 30 : 15;
    const displayItems = items.slice(0, renderLimit);

    if (!displayItems.length) {
      elPaletteResults.innerHTML = `<div class="es-empty-state">No matching tools or actions found for "<strong>${escapeHtml(query)}</strong>"</div>`;
      return;
    }

    let currentCategory = '';
    let html = '';

    displayItems.forEach((item, idx) => {
      if (item.category !== currentCategory) {
        currentCategory = item.category;
        html += `<div class="palette-category-header">${escapeHtml(currentCategory)}</div>`;
      }

      html += `
        <div class="palette-item ${idx === 0 ? 'palette-selected' : ''}" data-palette-idx="${idx}">
          <div class="palette-item-left">
            <span class="palette-item-icon">${item.icon || '⚡'}</span>
            <span class="palette-item-title">${highlightMatch(item.title, q)}</span>
          </div>
          <span class="palette-item-tag">${escapeHtml(item.category)}</span>
        </div>
      `;
    });

    elPaletteResults.innerHTML = html;

    // Attach click events
    elPaletteResults.querySelectorAll('.palette-item').forEach((row, idx) => {
      row.addEventListener('click', () => {
        elModalPalette.classList.remove('active');
        displayItems[idx].action();
      });
      row.addEventListener('mouseenter', () => {
        elPaletteResults.querySelectorAll('.palette-item').forEach(r => r.classList.remove('palette-selected'));
        row.classList.add('palette-selected');
        paletteSelectedIndex = idx;
      });
    });

    // Keyboard navigation inside Palette Input
    elPaletteInput.onkeydown = (e) => {
      const rows = elPaletteResults.querySelectorAll('.palette-item');
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        paletteSelectedIndex = (paletteSelectedIndex + 1) % displayItems.length;
        updatePaletteSelection(rows);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        paletteSelectedIndex = (paletteSelectedIndex - 1 + displayItems.length) % displayItems.length;
        updatePaletteSelection(rows);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (displayItems[paletteSelectedIndex]) {
          elModalPalette.classList.remove('active');
          displayItems[paletteSelectedIndex].action();
        }
      } else if (e.key === 'Escape') {
        elModalPalette.classList.remove('active');
      }
    };
  }

  function updatePaletteSelection(rows) {
    rows.forEach((r, idx) => {
      r.classList.toggle('palette-selected', idx === paletteSelectedIndex);
      if (idx === paletteSelectedIndex) {
        r.scrollIntoView({ block: 'nearest' });
      }
    });
  }

  // =========================================================================
  // 2. OSINT PIVOT MATRIX
  // =========================================================================
  function openPivotMatrix(targetValue = '') {
    elModalPivot.classList.add('active');
    if (targetValue) {
      elPivotInput.value = targetValue;
    }
    handlePivotInputChange(elPivotInput.value.trim());
    setTimeout(() => elPivotInput.focus(), 50);
  }

  function detectIndicatorType(val) {
    if (!val) return 'EMPTY';
    val = val.trim();
    if (/^(?:\d{1,3}\.){3}\d{1,3}$/.test(val)) return 'IP';
    if (/^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{40}$|^[a-fA-F0-9]{64}$/.test(val)) return 'HASH';
    if (/^CVE-\d{4}-\d{4,7}$/i.test(val)) return 'CVE';
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) return 'EMAIL';
    if (/^(\d\s*){9,11}$/.test(val)) return 'AU_ABN';
    if (/^[a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+$/.test(val)) return 'DOMAIN';
    return 'GENERIC';
  }

  function handlePivotInputChange(val) {
    const type = detectIndicatorType(val);
    elPivotTypeBadge.textContent = type === 'EMPTY' ? 'ENTER TARGET' : `TYPE: ${type}`;

    if (!val) {
      elPivotMatrixActions.innerHTML = `
        <div class="es-empty-state" style="grid-column:1/-1;">
          Enter any IP address, domain, file hash, email, CVE, or Australian ABN/ACN to generate real-time OSINT pivots.
        </div>
      `;
      return;
    }

    const encoded = encodeURIComponent(val);
    let categories = [];

    if (type === 'IP') {
      categories = [
        {
          name: '🌐 Network & Host Intel',
          pivots: [
            { name: 'Shodan Host Lookup', url: `https://www.shodan.io/host/${val}` },
            { name: 'Censys Host Search', url: `https://search.censys.io/hosts/${val}` },
            { name: 'AbuseIPDB Reputation', url: `https://www.abuseipdb.com/check/${val}` },
            { name: 'GreyNoise Visualizer', url: `https://viz.greynoise.io/ip/${val}` },
            { name: 'IPinfo Geolocation', url: `https://ipinfo.io/${val}` }
          ]
        },
        {
          name: '🛡️ Threat & Malware Pivots',
          pivots: [
            { name: 'VirusTotal IP Report', url: `https://www.virustotal.com/gui/ip-address/${val}` },
            { name: 'ThreatMiner IP Details', url: `https://www.threatminer.org/host.php?q=${val}` },
            { name: 'AlienVault OTX Pulse', url: `https://otx.alienvault.com/indicator/ip/${val}` }
          ]
        },
        {
          name: '🇦🇺 Australian & APNIC Routing',
          pivots: [
            { name: 'APNIC WHOIS Lookup', url: `https://wq.apnic.net/static/search.html?query=${val}` },
            { name: 'Aussie Broadband Looking Glass', url: `https://looking-glass.aussiebroadband.com.au/` }
          ]
        }
      ];
    } else if (type === 'DOMAIN') {
      categories = [
        {
          name: '🔗 Domain & Passive DNS',
          pivots: [
            { name: 'urlscan.io Submission', url: `https://urlscan.io/search/#${encoded}` },
            { name: 'VirusTotal Domain Report', url: `https://www.virustotal.com/gui/domain/${val}` },
            { name: 'SecurityTrails DNS History', url: `https://securitytrails.com/domain/${val}/dns` },
            { name: 'crt.sh Certificate Search', url: `https://crt.sh/?q=${encoded}` }
          ]
        },
        {
          name: '🇦🇺 Australian Registrar Intel',
          pivots: [
            { name: 'auDA .au WHOIS Search', url: `https://www.auda.org.au/tools/whois` },
            { name: 'ABN Lookup Associated Entity', url: `https://abr.business.gov.au/Search/ResultsActive?SearchText=${encoded}` }
          ]
        },
        {
          name: '🏛️ Web Archive & History',
          pivots: [
            { name: 'Wayback Machine History', url: `https://web.archive.org/web/*/${val}` },
            { name: 'Trove Australian Web Archive', url: `https://trove.nla.gov.au/search/category/websites?keyword=${encoded}` }
          ]
        }
      ];
    } else if (type === 'HASH') {
      categories = [
        {
          name: '🦠 Malware & Binary Repos',
          pivots: [
            { name: 'VirusTotal Hash Analysis', url: `https://www.virustotal.com/gui/file/${val}` },
            { name: 'MalwareBazaar Sample Search', url: `https://bazaar.abuse.ch/sample/${val}/` },
            { name: 'Hybrid Analysis Sandbox', url: `https://www.hybrid-analysis.com/sample/${val}` },
            { name: 'Any.Run Interactive Sandbox', url: `https://app.any.run/submissions/#search=${encoded}` }
          ]
        }
      ];
    } else if (type === 'CVE') {
      categories = [
        {
          name: '⚠️ Vulnerability & Exploit Databases',
          pivots: [
            { name: 'NIST National Vulnerability Database', url: `https://nvd.nist.gov/vuln/detail/${val}` },
            { name: 'CVE Details Exploit Vector', url: `https://www.cvedetails.com/cve/${val}/` },
            { name: 'VulnCheck Community Exploit Feed', url: `https://vulncheck.com/` },
            { name: 'ExploitDB Zero-Day Exploits', url: `https://www.exploit-db.com/search?cve=${val.replace(/CVE-/i, '')}` }
          ]
        }
      ];
    } else if (type === 'AU_ABN') {
      categories = [
        {
          name: '🇦🇺 Australian Corporate Registry',
          pivots: [
            { name: 'ABN Lookup Official Register', url: `https://abr.business.gov.au/Search/ResultsActive?SearchText=${encoded}` },
            { name: 'ASIC Connect Company Lookup', url: `https://connectonline.asic.gov.au/` },
            { name: 'AFSA Bankruptcy Register (NPII)', url: `https://www.afsa.gov.au/` },
            { name: 'AusTender Contract History', url: `https://www.tenders.gov.au/` }
          ]
        }
      ];
    } else {
      categories = [
        {
          name: '🔍 Universal Multi-Engine Pivot',
          pivots: [
            { name: 'Google Dorking Search', url: `https://www.google.com/search?q=${encoded}` },
            { name: 'Trove Australian Archives', url: `https://trove.nla.gov.au/search/category/newspapers?keyword=${encoded}` },
            { name: 'AusLII Court Judgments', url: `http://www.austlii.edu.au/cgi-bin/sinosrch.cgi?query=${encoded}` },
            { name: 'GitHub Code Repositories', url: `https://github.com/search?q=${encoded}&type=code` },
            { name: 'Shodan General Search', url: `https://www.shodan.io/search?query=${encoded}` }
          ]
        }
      ];
    }

    elPivotMatrixActions.innerHTML = categories.map(cat => `
      <div class="pivot-category-card">
        <div class="pivot-card-header">${escapeHtml(cat.name)}</div>
        <div class="pivot-btn-chips-container">
          ${cat.pivots.map(p => `
            <button class="pivot-btn-chip" onclick="window.open('${p.url}', '_blank', 'noopener,noreferrer');">
              <span>${escapeHtml(p.name)}</span>
              <span>↗</span>
            </button>
          `).join('')}
        </div>
      </div>
    `).join('');
  }

  // =========================================================================
  // 3. THREAT INTEL & CVE LIVE RADAR
  // =========================================================================
  async function fetchThreatRadarFeed() {
    try {
      const res = await fetch('/api/radar/feed?limit=40');
      if (res.ok) {
        const data = await res.json();
        radarFeedData = data.feed || [];
        document.getElementById('radar-live-badge').textContent = `FEED: ${data.source.toUpperCase()}`;
      }
    } catch (e) {
      console.warn('Threat radar fetch error:', e);
    }
  }

  function openThreatRadar() {
    elModalRadar.classList.add('active');
    renderRadarItems(elRadarSearchInput.value.trim());
  }

  function renderRadarItems(filter = '') {
    const f = filter.toLowerCase();
    const filtered = radarFeedData.filter(i => 
      !f || i.id.toLowerCase().includes(f) || i.title.toLowerCase().includes(f) || (i.vendor && i.vendor.toLowerCase().includes(f)) || i.description.toLowerCase().includes(f)
    );

    if (!filtered.length) {
      elRadarItemsList.innerHTML = `<div class="es-empty-state">No vulnerabilities match filter "${escapeHtml(filter)}"</div>`;
      return;
    }

    elRadarItemsList.innerHTML = filtered.map(item => `
      <div class="radar-item">
        <div class="radar-item-header">
          <span class="radar-item-title">${escapeHtml(item.title)}</span>
          <span class="radar-badge ${item.severity === 'CRITICAL' ? 'critical' : 'high'}">
            ${item.ransomware ? '⚡ RANSOMWARE' : item.severity}
          </span>
        </div>
        <p class="radar-desc">${escapeHtml(item.description)}</p>
        <div class="radar-meta">
          <span>📅 Added: ${item.date || 'Recent'}</span>
          <span>🏛️ Vendor: ${escapeHtml(item.vendor || 'Unknown')}</span>
          <a href="${item.url}" target="_blank" rel="noopener noreferrer" style="color:var(--accent-cyan);margin-left:auto;text-decoration:none;">View Advisory ↗</a>
          <button class="btn-icon" style="padding:1px 6px;font-size:0.65rem;" onclick="addNodeToGraph('${item.id}', 'cve');">🕸️ To Graph</button>
        </div>
      </div>
    `).join('');
  }

  // =========================================================================
  // 4. VISUAL INVESTIGATION LINK GRAPH (CANVAS SIMULATION)
  // =========================================================================
  let graphAnimationId = null;
  let isGraphConnectMode = false;
  let connectSourceNode = null;
  let draggedNode = null;
  let graphOffset = { x: 0, y: 0 };
  let graphScale = 1.0;
  let isPanningCanvas = false;
  let panStart = { x: 0, y: 0 };

  function openInvestigationGraph() {
    elModalGraph.classList.add('active');
    setTimeout(() => {
      resizeCanvas();
      startGraphSimulation();
    }, 50);
  }

  function resizeCanvas() {
    const wrapper = document.getElementById('graph-canvas-wrapper');
    elCanvas.width = wrapper.clientWidth;
    elCanvas.height = wrapper.clientHeight;
  }

  function startGraphSimulation() {
    if (graphAnimationId) cancelAnimationFrame(graphAnimationId);

    const ctx = elCanvas.getContext('2d');
    const nodes = investigationGraph.nodes;
    const edges = investigationGraph.edges;

    function renderLoop() {
      // Physics Simulation Step
      const k = 0.05; // spring constant
      const rep = 800; // repulsion
      const damping = 0.85;

      // 1. Node Repulsion
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[j].x - nodes[i].x;
          const dy = nodes[j].y - nodes[i].y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          if (dist < 400) {
            const force = rep / (dist * dist);
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;
            nodes[i].vx -= fx;
            nodes[i].vy -= fy;
            nodes[j].vx += fx;
            nodes[j].vy += fy;
          }
        }
      }

      // 2. Edge Spring Force
      edges.forEach(e => {
        const s = nodes.find(n => n.id === e.source);
        const t = nodes.find(n => n.id === e.target);
        if (s && t) {
          const dx = t.x - s.x;
          const dy = t.y - s.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = (dist - 140) * k;
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          s.vx += fx;
          s.vy += fy;
          t.vx -= fx;
          t.vy -= fy;
        }
      });

      // 3. Update Positions
      nodes.forEach(n => {
        if (n !== draggedNode) {
          n.vx *= damping;
          n.vy *= damping;
          n.x += n.vx;
          n.y += n.vy;
        }
      });

      // Clear & Draw
      ctx.clearRect(0, 0, elCanvas.width, elCanvas.height);
      ctx.save();
      ctx.translate(graphOffset.x, graphOffset.y);
      ctx.scale(graphScale, graphScale);

      // Draw Edges
      edges.forEach(e => {
        const s = nodes.find(n => n.id === e.source);
        const t = nodes.find(n => n.id === e.target);
        if (s && t) {
          ctx.beginPath();
          ctx.moveTo(s.x, s.y);
          ctx.lineTo(t.x, t.y);
          ctx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
          ctx.lineWidth = 2;
          ctx.stroke();

          // Edge Label
          if (e.label) {
            const mx = (s.x + t.x) / 2;
            const my = (s.y + t.y) / 2;
            ctx.fillStyle = '#64748b';
            ctx.font = '10px monospace';
            ctx.fillText(e.label, mx, my - 4);
          }
        }
      });

      // Draw Nodes
      nodes.forEach(n => {
        // Outer halo
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + 4, 0, Math.PI * 2);
        ctx.fillStyle = n.color ? `${n.color}22` : 'rgba(0, 240, 255, 0.15)';
        ctx.fill();

        // Node Circle
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#0a101f';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = n.color || 'var(--accent-cyan)';
        ctx.stroke();

        // Node Label
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(n.label, n.x, n.y + n.radius + 14);

        // Node Type Icon / Initials
        ctx.fillStyle = n.color || 'var(--accent-cyan)';
        ctx.font = '10px monospace';
        ctx.fillText(n.type.toUpperCase().slice(0, 3), n.x, n.y + 3);
      });

      ctx.restore();
      graphAnimationId = requestAnimationFrame(renderLoop);
    }

    renderLoop();
  }

  window.addNodeToGraph = function(label, type = 'ip') {
    if (!label) return;
    const colors = {
      ip: '#00f0ff',
      domain: '#00ff9d',
      hash: '#ec4899',
      email: '#a855f7',
      person: '#3b82f6',
      org: '#f59e0b',
      cve: '#f43f5e',
      aus: '#10b981'
    };

    const newNode = {
      id: `node_${Date.now()}`,
      label: label,
      type: type,
      x: elCanvas.width / 2 + (Math.random() * 80 - 40),
      y: elCanvas.height / 2 + (Math.random() * 80 - 40),
      vx: 0,
      vy: 0,
      radius: 22,
      color: colors[type] || '#00f0ff'
    };

    investigationGraph.nodes.push(newNode);
    localStorage.setItem('bubbsy_investigation_graph', JSON.stringify(investigationGraph));
    showToast(`Added entity to graph: ${label}`);
  };

  // Canvas Mouse Interactions
  elCanvas.addEventListener('mousedown', (e) => {
    const rect = elCanvas.getBoundingClientRect();
    const mouseX = (e.clientX - rect.left - graphOffset.x) / graphScale;
    const mouseY = (e.clientY - rect.top - graphOffset.y) / graphScale;

    const clicked = investigationGraph.nodes.find(n => {
      const dx = n.x - mouseX;
      const dy = n.y - mouseY;
      return Math.sqrt(dx * dx + dy * dy) <= n.radius;
    });

    if (clicked) {
      if (isGraphConnectMode) {
        if (!connectSourceNode) {
          connectSourceNode = clicked;
          showToast(`Connecting: Select target node for ${clicked.label}`);
        } else if (connectSourceNode !== clicked) {
          investigationGraph.edges.push({
            source: connectSourceNode.id,
            target: clicked.id,
            label: 'connected_to'
          });
          localStorage.setItem('bubbsy_investigation_graph', JSON.stringify(investigationGraph));
          showToast(`Connected ${connectSourceNode.label} &rarr; ${clicked.label}`);
          isGraphConnectMode = false;
          connectSourceNode = null;
        }
      } else {
        draggedNode = clicked;
      }
    } else {
      isPanningCanvas = true;
      panStart = { x: e.clientX - graphOffset.x, y: e.clientY - graphOffset.y };
    }
  });

  window.addEventListener('mousemove', (e) => {
    if (draggedNode) {
      const rect = elCanvas.getBoundingClientRect();
      draggedNode.x = (e.clientX - rect.left - graphOffset.x) / graphScale;
      draggedNode.y = (e.clientY - rect.top - graphOffset.y) / graphScale;
      draggedNode.vx = 0;
      draggedNode.vy = 0;
    } else if (isPanningCanvas) {
      graphOffset.x = e.clientX - panStart.x;
      graphOffset.y = e.clientY - panStart.y;
    }
  });

  window.addEventListener('mouseup', () => {
    draggedNode = null;
    isPanningCanvas = false;
  });

  elCanvas.addEventListener('dblclick', (e) => {
    const rect = elCanvas.getBoundingClientRect();
    const mouseX = (e.clientX - rect.left - graphOffset.x) / graphScale;
    const mouseY = (e.clientY - rect.top - graphOffset.y) / graphScale;

    const clicked = investigationGraph.nodes.find(n => {
      const dx = n.x - mouseX;
      const dy = n.y - mouseY;
      return Math.sqrt(dx * dx + dy * dy) <= n.radius;
    });

    if (clicked) {
      openPivotMatrix(clicked.label);
    }
  });

  elCanvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    graphScale = Math.max(0.3, Math.min(3.0, graphScale * zoomFactor));
  });

  // Graph Toolbar Buttons
  document.getElementById('btn-graph-add-node').addEventListener('click', () => {
    const label = document.getElementById('graph-new-node-label').value.trim();
    const type = document.getElementById('graph-new-node-type').value;
    if (label) {
      addNodeToGraph(label, type);
      document.getElementById('graph-new-node-label').value = '';
    }
  });

  document.getElementById('btn-graph-connect-mode').addEventListener('click', () => {
    isGraphConnectMode = !isGraphConnectMode;
    connectSourceNode = null;
    showToast(isGraphConnectMode ? '🔗 Click source node then target node to connect' : 'Connection mode cancelled');
  });

  document.getElementById('btn-graph-clear').addEventListener('click', () => {
    if (confirm('Clear all nodes and edges in graph?')) {
      investigationGraph.nodes = [];
      investigationGraph.edges = [];
      localStorage.setItem('bubbsy_investigation_graph', JSON.stringify(investigationGraph));
      showToast('Investigation graph cleared');
    }
  });

  document.getElementById('btn-graph-export-png').addEventListener('click', () => {
    const dataUrl = elCanvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = `bubbsy_graph_${Date.now()}.png`;
    a.click();
    showToast('Exported graph screenshot as PNG');
  });

  // =========================================================================
  // 5. INCIDENT SESSION & MARKDOWN EXPORT
  // =========================================================================
  function openSessionExport() {
    elModalExport.classList.add('active');
  }

  document.getElementById('btn-export-markdown-file').addEventListener('click', () => {
    const caseName = document.getElementById('export-case-name').value.trim() || 'Bubbsy Incident Report';
    const notes = document.getElementById('export-case-notes').value.trim() || 'No analyst notes recorded.';

    let md = `# 🛡️ ${caseName}\n\n`;
    md += `**Generated:** ${new Date().toISOString()}\n`;
    md += `**Platform:** Bubbsy Start Page | OSINT Command Hub 2.18.0\n\n`;
    md += `## 📝 Executive Summary & Analyst Notes\n\n${notes}\n\n`;

    md += `## 🎯 Indicators of Compromise & Graph Entities\n\n`;
    md += `| Type | Indicator / Entity | Connected Edges |\n| :--- | :--- | :--- |\n`;

    investigationGraph.nodes.forEach(n => {
      const connections = investigationGraph.edges
        .filter(e => e.source === n.id || e.target === n.id)
        .map(e => {
          const other = investigationGraph.nodes.find(o => o.id === (e.source === n.id ? e.target : e.source));
          return `${e.label} &rarr; ${other ? other.label : '?'}`;
        }).join(', ');

      md += `| **${n.type.toUpperCase()}** | \`${n.label}\` | ${connections || 'None'} |\n`;
    });

    md += `\n## ⭐ Pinned Tools & Methodology References\n\n`;
    userFavorites.forEach(f => {
      md += `- [${f.title}](${f.url}) ${f.description ? '— ' + f.description : ''}\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${caseName.toLowerCase().replace(/[^a-z0-9]/g, '_')}.md`;
    a.click();
    showToast('Exported incident dossier to Markdown!');
  });

  document.getElementById('btn-export-json-workspace').addEventListener('click', () => {
    const snapshot = {
      caseName: document.getElementById('export-case-name').value.trim(),
      notes: document.getElementById('export-case-notes').value.trim(),
      graph: investigationGraph,
      favorites: userFavorites,
      customBookmarks: userBookmarks,
      settings: settings,
      timestamp: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bubbsy_workspace_${Date.now()}.bubbsy.json`;
    a.click();
    showToast('Saved JSON workspace snapshot!');
  });

  document.getElementById('import-workspace-file').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target.result);
        if (data.graph) {
          investigationGraph = data.graph;
          localStorage.setItem('bubbsy_investigation_graph', JSON.stringify(investigationGraph));
        }
        if (data.favorites) {
          userFavorites = data.favorites;
          localStorage.setItem('bubbsy_favorites', JSON.stringify(userFavorites));
        }
        if (data.caseName) document.getElementById('export-case-name').value = data.caseName;
        if (data.notes) document.getElementById('export-case-notes').value = data.notes;

        showToast('Workspace snapshot restored successfully!');
        renderDashboard();
      } catch (err) {
        showToast('Invalid workspace snapshot file format', 'error');
      }
    };
    reader.readAsText(file);
  });

  // Export/Import Backup JSON
  function exportBackupJson() {
    const data = {
      userFavorites,
      userBookmarks,
      settings,
      investigationGraph
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bubbsy_backup_${Date.now()}.json`;
    a.click();
    showToast('Backup JSON exported');
  }

  function handleAddCustomBookmark(e) {
    e.preventDefault();
    const title = document.getElementById('bm-title').value.trim();
    const url = document.getElementById('bm-url').value.trim();
    const desc = document.getElementById('bm-desc').value.trim();
    const catId = parseInt(document.getElementById('bm-category').value, 10);

    const newLink = {
      id: Date.now(),
      title: title,
      url: url,
      description: desc,
      domain: extractDomain(url),
      favicon: `https://f.start.me/${extractDomain(url)}`
    };

    userBookmarks.push({ ...newLink, widgetId: catId });
    localStorage.setItem('bubbsy_user_bookmarks', JSON.stringify(userBookmarks));

    // Append into active dashboard memory
    if (appData && appData.columns) {
      for (const col of appData.columns) {
        const w = col.widgets.find(item => item.id === catId);
        if (w) {
          w.links.push(newLink);
          break;
        }
      }
    }

    document.getElementById('modal-custom-bookmark').classList.remove('active');
    document.getElementById('form-custom-bookmark').reset();
    renderDashboard();
    showToast(`Added: ${title}`);
  }

  // --- MODAL CLOSERS ---
  document.getElementById('btn-close-pivot').addEventListener('click', () => elModalPivot.classList.remove('active'));
  document.getElementById('btn-close-radar').addEventListener('click', () => elModalRadar.classList.remove('active'));
  document.getElementById('btn-close-graph').addEventListener('click', () => {
    elModalGraph.classList.remove('active');
    if (graphAnimationId) cancelAnimationFrame(graphAnimationId);
  });
  document.getElementById('btn-close-export').addEventListener('click', () => elModalExport.classList.remove('active'));

  document.getElementById('pivot-input').addEventListener('input', (e) => handlePivotInputChange(e.target.value));
  document.getElementById('btn-pivot-clear').addEventListener('click', () => {
    elPivotInput.value = '';
    handlePivotInputChange('');
    elPivotInput.focus();
  });

  document.getElementById('btn-pivot-all').addEventListener('click', () => {
    const chips = elPivotMatrixActions.querySelectorAll('.pivot-btn-chip');
    if (!chips.length) {
      showToast('Enter a target indicator first');
      return;
    }
    chips.forEach(chip => chip.click());
    showToast(`Launched ${chips.length} OSINT pivots!`);
  });

  // =========================================================================
  // 7. THREAT DORK & ATTACK SURFACE GENERATOR
  // =========================================================================
  const elModalDorks = document.getElementById('modal-dorks');
  const elDorkTargetInput = document.getElementById('dork-target-input');
  const elDorkPresetsContainer = document.getElementById('dork-presets-container');

  function openDorkGenerator() {
    elModalDorks.classList.add('active');
    renderDorkPresets(elDorkTargetInput.value.trim());
    setTimeout(() => elDorkTargetInput.focus(), 50);
  }

  function renderDorkPresets(targetDomain = '') {
    const t = targetDomain ? targetDomain.trim() : '';
    const sitePrefix = t ? `site:${t} ` : '';

    const dorkGroups = [
      {
        name: '🇦🇺 Australian Gov & Sensitive Records',
        items: [
          { name: 'Confidential PDF Documents', query: `${t ? `site:${t}` : 'site:gov.au'} filetype:pdf ("confidential" OR "restricted" OR "not for public release")` },
          { name: 'Exposed Environment Files (.env)', query: `${t ? `site:${t}` : 'site:gov.au'} filetype:env OR filetype:yml "DB_PASSWORD"` },
          { name: 'Sensitive Spreadsheets (Salaries / PII)', query: `${t ? `site:${t}` : 'site:gov.au'} filetype:xlsx OR filetype:csv ("salary" OR "password" OR "tfn")` },
          { name: 'Open Directory File Indexes', query: `${t ? `site:${t}` : 'site:gov.au'} intitle:"index of" "backup" OR "dump"` }
        ]
      },
      {
        name: '☁️ Cloud Buckets & Database Dumps',
        items: [
          { name: 'AWS S3 Exposed Storage', query: `site:s3.amazonaws.com "${t || 'backup'}"` },
          { name: 'SQL Database Dumps', query: `${sitePrefix}filetype:sql "INSERT INTO" ("admin" OR "password" OR "users")` },
          { name: 'Exposed Git Repositories', query: `${sitePrefix}intitle:"index of" ".git/config"` },
          { name: 'KeePass Password Vaults', query: `${sitePrefix}filetype:kdbx OR filetype:kdb` }
        ]
      },
      {
        name: '🌐 Shodan & Port Attack Surface',
        items: [
          { name: 'Exposed RDP Port 3389', query: t ? `hostname:"${t}" port:3389` : 'port:3389 country:"AU"', isShodan: true },
          { name: 'Open SCADA / Industrial ICS', query: t ? `org:"${t}" port:502` : 'port:502 country:"AU"', isShodan: true },
          { name: 'Admin Dashboards (Grafana / Kibana)', query: t ? `hostname:"${t}" http.title:"Dashboard"` : 'http.title:"Dashboard" country:"AU"', isShodan: true }
        ]
      },
      {
        name: '🐙 GitHub Secret Dorks',
        items: [
          { name: 'API Keys & Secrets in .env', query: `${t || 'org:australian-gov'} filename:.env "SECRET_KEY"`, isGithub: true },
          { name: 'Exposed RSA Private Keys', query: `${t || 'org:australian-gov'} filename:id_rsa`, isGithub: true },
          { name: 'AWS Credentials File', query: `${t || 'org:australian-gov'} path:.aws/credentials`, isGithub: true }
        ]
      }
    ];

    elDorkPresetsContainer.innerHTML = dorkGroups.map(grp => `
      <div class="pivot-category-card">
        <div class="pivot-card-header">${escapeHtml(grp.name)}</div>
        <div class="pivot-btn-chips-container">
          ${grp.items.map(item => `
            <div class="pivot-btn-chip" style="flex-direction:column;align-items:flex-start;gap:3px;">
              <div style="display:flex;justify-content:space-between;width:100%;">
                <span style="font-weight:600;color:var(--text-primary);">${escapeHtml(item.name)}</span>
                <span style="display:flex;gap:6px;">
                  <button class="btn-icon" style="padding:0 4px;font-size:0.62rem;" onclick="navigator.clipboard.writeText('${escapeRegex(item.query)}'); showToast('Dork copied!');">📋</button>
                  <button class="btn-icon" style="padding:0 4px;font-size:0.62rem;color:var(--accent-cyan);" onclick="executeDork('${encodeURIComponent(item.query)}', ${item.isShodan ? "'shodan'" : (item.isGithub ? "'github'" : "'google'")});">⚡ Run</button>
                </span>
              </div>
              <code style="font-size:0.68rem;color:var(--text-muted);word-break:break-all;">${escapeHtml(item.query)}</code>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
  }

  window.executeDork = function(encodedQuery, engine = 'google') {
    const q = decodeURIComponent(encodedQuery);
    if (engine === 'shodan') {
      window.open(`https://www.shodan.io/search?query=${encodeURIComponent(q)}`, '_blank', 'noopener,noreferrer');
    } else if (engine === 'github') {
      window.open(`https://github.com/search?q=${encodeURIComponent(q)}&type=code`, '_blank', 'noopener,noreferrer');
    } else {
      window.open(`https://www.google.com/search?q=${encodeURIComponent(q)}`, '_blank', 'noopener,noreferrer');
    }
  };

  document.getElementById('btn-open-dorks').addEventListener('click', openDorkGenerator);
  document.getElementById('btn-close-dorks').addEventListener('click', () => elModalDorks.classList.remove('active'));
  document.getElementById('dork-target-input').addEventListener('input', (e) => renderDorkPresets(e.target.value));
  document.getElementById('btn-clear-dork-target').addEventListener('click', () => {
    elDorkTargetInput.value = '';
    renderDorkPresets('');
    elDorkTargetInput.focus();
  });

  // =========================================================================
  // 8. AUSTRALIAN CADASTRE & GEO-COORDINATE RECON
  // =========================================================================
  const elModalGeo = document.getElementById('modal-geo');
  const elGeoCoordInput = document.getElementById('geo-coord-input');
  const elGeoMapActions = document.getElementById('geo-map-actions');

  function openGeoRecon(defaultCoords = '') {
    elModalGeo.classList.add('active');
    if (defaultCoords) elGeoCoordInput.value = defaultCoords;
    handleGeoParse(elGeoCoordInput.value.trim());
    setTimeout(() => elGeoCoordInput.focus(), 50);
  }

  function handleGeoParse(input = '') {
    let lat = -33.8688;
    let lon = 151.2093; // Sydney CBD default

    const match = input.match(/(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)/);
    if (match) {
      lat = parseFloat(match[1]);
      lon = parseFloat(match[2]);
    }

    const mapProviders = [
      {
        name: '🇦🇺 Official Australian Cadastre',
        items: [
          { name: 'NSW SIX Maps (Cadastral Boundaries)', url: `https://maps.six.nsw.gov.au/` },
          { name: 'VicPlan (Victoria Cadastre)', url: `https://mapshare.vic.gov.au/vicplan/` },
          { name: 'QLD Globe (Queensland Land)', url: `https://qldglobe.information.qld.gov.au/` },
          { name: 'National Map Australia', url: `https://nationalmap.gov.au/#share=s-coordinates` }
        ]
      },
      {
        name: '🛰️ Near-Realtime Satellite & 3D Imagery',
        items: [
          { name: 'Sentinel-2 EO Browser (Near Real-Time)', url: `https://apps.sentinel-hub.com/eo-browser/?lat=${lat}&lng=${lon}&zoom=14` },
          { name: 'Google Earth 3D Flyover', url: `https://earth.google.com/web/search/${lat},${lon}` },
          { name: 'OpenStreetMap Explorer', url: `https://www.openstreetmap.org/#map=16/${lat}/${lon}` },
          { name: 'Wigle.net WiFi Geolocation', url: `https://wigle.net/` }
        ]
      }
    ];

    elGeoMapActions.innerHTML = mapProviders.map(p => `
      <div class="pivot-category-card">
        <div class="pivot-card-header">${escapeHtml(p.name)}</div>
        <div class="pivot-btn-chips-container">
          ${p.items.map(item => `
            <button class="pivot-btn-chip" onclick="window.open('${item.url}', '_blank', 'noopener,noreferrer');">
              <span>${escapeHtml(item.name)}</span>
              <span>↗</span>
            </button>
          `).join('')}
        </div>
      </div>
    `).join('');
  }

  document.getElementById('btn-open-geo').addEventListener('click', () => openGeoRecon());
  document.getElementById('btn-close-geo').addEventListener('click', () => elModalGeo.classList.remove('active'));
  document.getElementById('btn-geo-parse').addEventListener('click', () => handleGeoParse(elGeoCoordInput.value.trim()));
  document.getElementById('geo-coord-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleGeoParse(elGeoCoordInput.value.trim());
  });

  document.getElementById('btn-geo-add-to-graph').addEventListener('click', () => {
    const val = elGeoCoordInput.value.trim() || '-33.8688, 151.2093';
    addNodeToGraph(`Geo: ${val}`, 'aus');
    openInvestigationGraph();
    elModalGeo.classList.remove('active');
  });

  // =========================================================================
  // 6. FIRST-TIME ONBOARDING TOUR CONTROLLER
  // =========================================================================
  const elModalTour = document.getElementById('modal-tour');
  const elTourSlideContainer = document.getElementById('tour-slide-container');
  const elTourDots = document.getElementById('tour-dots');
  const elBtnTourPrev = document.getElementById('btn-tour-prev');
  const elBtnTourNext = document.getElementById('btn-tour-next');
  const elBtnSkipTour = document.getElementById('btn-skip-tour');

  let currentTourSlide = 0;
  const tourSlides = [
    {
      icon: '🚀',
      title: 'Mission Briefing: Bubbsy Command Hub',
      desc: 'Welcome to your tactical OSINT & intelligence start page. Loaded with <strong>1,699+ verified tools</strong>, Australian corporate & legal registries, evergreen AI models, and sub-millisecond search.',
      box: '🇦🇺 Australian-First Hierarchy • ⚡ Voidtools Everything • 🤖 Clean AI Hub'
    },
    {
      icon: '🔍',
      title: 'Omnisearch & Quick Bang Operators',
      desc: 'Press <kbd class="hud-key">/</kbd> anywhere to focus the search bar. Use bang shortcuts to instantly route queries to specific intelligence providers:',
      box: '!es &lt;file&gt; • !abn &lt;entity&gt; • !trove &lt;archive&gt; • !gpt &lt;prompt&gt; • !shodan &lt;ip&gt;'
    },
    {
      icon: '⚡',
      title: 'Zero-Click Hover Hotkeys',
      desc: 'Keep your workspace clean without button clutter. Simply hover your mouse cursor over any tool:',
      box: 'Hover + C &rarr; Copy URL to Clipboard • Hover + F &rarr; Pin to ⭐ My Pinned'
    },
    {
      icon: '⌨️',
      title: 'Global Command Palette (Ctrl+K)',
      desc: 'Press <kbd class="hud-key cyan">Ctrl+K</kbd> (or <kbd>Cmd+K</kbd>) anywhere to open the Spotlight launcher. Fuzzy search across all tools, local files, and HUD commands in milliseconds.',
      box: 'Arrow Keys ↑ ↓ to navigate • Enter to Launch • ESC to Dismiss'
    },
    {
      icon: '🎯',
      title: 'Clue Whiteboard & Threat Pivoting',
      desc: 'Enter any IP, Domain, Hash, CVE, or ABN into the <strong>Pivot Matrix</strong> for instant multi-engine lookups. Connect clues together on the <strong>Link Graph</strong> and export incident dossiers to Markdown.',
      box: 'Multi-Engine Pivots • Interactive Node Canvas • 1-Click Markdown Export'
    },
    {
      icon: '🌐',
      title: 'Public Web & Desktop Ready',
      desc: 'Bubbsy is 100% self-contained and ready for public web hosting (GitHub Pages / Vercel / Netlify). When run locally with <code>start_bubbsy.bat</code>, Voidtools Everything local disk indexing unlocks automatically.',
      box: '⚡ Production Ready • 100% Offline Capable • Zero External Dependencies'
    }
  ];

  function startOnboardingTour() {
    currentTourSlide = 0;
    elModalTour.classList.add('active');
    renderTourSlide();
  }

  function renderTourSlide() {
    const s = tourSlides[currentTourSlide];
    elTourSlideContainer.innerHTML = `
      <div class="tour-slide active">
        <div class="tour-icon-box">${s.icon}</div>
        <div class="tour-slide-title">${s.title}</div>
        <p class="tour-slide-desc">${s.desc}</p>
        <div class="tour-slide-box">${s.box}</div>
      </div>
    `;

    // Update Dots
    const dots = elTourDots.querySelectorAll('.tour-dot');
    dots.forEach((d, idx) => {
      d.classList.toggle('active', idx === currentTourSlide);
    });

    // Update Buttons
    elBtnTourPrev.style.display = currentTourSlide > 0 ? '' : 'none';
    elBtnTourNext.textContent = currentTourSlide === tourSlides.length - 1 ? 'Get Started 🚀' : 'Next →';
  }

  function finishOnboardingTour() {
    elModalTour.classList.remove('active');
    localStorage.setItem('bubbsy_tour_seen', 'true');
    showToast('Welcome to Bubbsy Start Page! Press / or Ctrl+K to search.');
  }

  elBtnTourNext.addEventListener('click', () => {
    if (currentTourSlide < tourSlides.length - 1) {
      currentTourSlide++;
      renderTourSlide();
    } else {
      finishOnboardingTour();
    }
  });

  elBtnTourPrev.addEventListener('click', () => {
    if (currentTourSlide > 0) {
      currentTourSlide--;
      renderTourSlide();
    }
  });

  elBtnSkipTour.addEventListener('click', finishOnboardingTour);
  document.getElementById('btn-tour').addEventListener('click', startOnboardingTour);

  // Hook tour into init on first visit
  const prevInit = init;
  init = async function() {
    await prevInit();
    if (!localStorage.getItem('bubbsy_tour_seen')) {
      setTimeout(startOnboardingTour, 600);
    }
  };

  document.getElementById('palette-input').addEventListener('input', (e) => renderPaletteResults(e.target.value));
  document.getElementById('radar-search-input').addEventListener('input', (e) => renderRadarItems(e.target.value));
  document.getElementById('btn-refresh-radar').addEventListener('click', async () => {
    showToast('Refreshing threat radar feed...');
    await fetchThreatRadarFeed();
    renderRadarItems(elRadarSearchInput.value.trim());
  });

  // Helper Utilities
  function extractDomain(url) {
    try {
      let d = url.replace(/^https?:\/\//, '').split('/')[0].split('?')[0].split(':')[0];
      return d.toLowerCase();
    } catch (e) {
      return '';
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // Self Boot
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

