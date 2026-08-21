/**
 * BUBBSY START PAGE | OSINT COMMAND ENGINE 2.18.0
 * Clean WinUI 3 Monochrome Design - Zero Emojis
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

  // Overlays
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

  // WinUI 3 Star Icon SVG
  const STAR_SVG = `<svg width="11" height="11" viewBox="0 0 24 24" fill="#f59e0b"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;

  // --- INIT ---
  async function init() {
    applyTheme(currentTheme);

    // If served from local server, fetch latest data and check ES status
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
      showToast('[ERROR] Failed to load OSINT dataset. Check data/osint_data.json', 'error');
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
      const initial = domain ? domain.charAt(0).toUpperCase() : '•';

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
          <span class="link-pin-indicator" style="${isPinned ? '' : 'display:none;'}">${STAR_SVG}</span>
        </a>
      `;

      // Track hovered link for hotkeys
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
    let searchKeyboardNavIdx = -1;

    function clearKeyboardSearchSelection() {
      document.querySelectorAll('.link-item.keyboard-selected').forEach(li => li.classList.remove('keyboard-selected'));
    }

    function updateKeyboardSearchSelection(visibleLinks, idx) {
      clearKeyboardSearchSelection();
      if (visibleLinks[idx]) {
        visibleLinks[idx].classList.add('keyboard-selected');
        visibleLinks[idx].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    }

    elMainSearch.addEventListener('input', (e) => {
      searchKeyboardNavIdx = -1;
      clearKeyboardSearchSelection();
      handleSearchInput(e.target.value);
    });

    elMainSearch.addEventListener('keydown', (e) => {
      const val = elMainSearch.value;

      // Autocomplete Bang on Tab
      if (e.key === 'Tab' && val.startsWith('!')) {
        const activeChip = document.querySelector('.bang-chip.bang-active-match');
        if (activeChip) {
          e.preventDefault();
          elMainSearch.value = activeChip.getAttribute('data-bang');
          handleSearchInput(elMainSearch.value);
          return;
        }
      }

      // Arrow navigation over visible filtered tools in dashboard
      if (activeSearchMode === 'filter' && val.trim()) {
        const visibleLinks = Array.from(document.querySelectorAll('.link-item')).filter(li => li.style.display !== 'none');
        if (visibleLinks.length > 0) {
          if (e.key === 'ArrowDown') {
            e.preventDefault();
            searchKeyboardNavIdx = (searchKeyboardNavIdx + 1) % visibleLinks.length;
            updateKeyboardSearchSelection(visibleLinks, searchKeyboardNavIdx);
            return;
          } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            searchKeyboardNavIdx = (searchKeyboardNavIdx - 1 + visibleLinks.length) % visibleLinks.length;
            updateKeyboardSearchSelection(visibleLinks, searchKeyboardNavIdx);
            return;
          } else if (e.key === 'Enter' && searchKeyboardNavIdx >= 0) {
            e.preventDefault();
            const activeLink = visibleLinks[searchKeyboardNavIdx];
            if (activeLink) {
              const a = activeLink.querySelector('a');
              if (a) window.open(a.href, '_blank', 'noopener,noreferrer');
            }
            return;
          }
        }
      }

      // Arrow navigation over Voidtools Everything search results
      if (activeSearchMode === 'everything' && val.trim()) {
        const rows = Array.from(document.querySelectorAll('.es-result-row'));
        if (rows.length > 0) {
          if (e.key === 'ArrowDown') {
            e.preventDefault();
            searchKeyboardNavIdx = (searchKeyboardNavIdx + 1) % rows.length;
            rows.forEach(r => r.classList.remove('es-selected'));
            rows[searchKeyboardNavIdx]?.classList.add('es-selected');
            rows[searchKeyboardNavIdx]?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            return;
          } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            searchKeyboardNavIdx = (searchKeyboardNavIdx - 1 + rows.length) % rows.length;
            rows.forEach(r => r.classList.remove('es-selected'));
            rows[searchKeyboardNavIdx]?.classList.add('es-selected');
            rows[searchKeyboardNavIdx]?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            return;
          } else if (e.key === 'Enter' && searchKeyboardNavIdx >= 0) {
            e.preventDefault();
            const activeRow = rows[searchKeyboardNavIdx];
            if (activeRow) {
              const filePath = activeRow.getAttribute('data-file-path');
              if (filePath) handleOpenFile(filePath, 'open');
            }
            return;
          }
        }
      }

      if (e.key === 'Enter') {
        executeSearch();
      } else if (e.key === 'Escape') {
        clearKeyboardSearchSelection();
        clearSearch();
      }
    });

    elBtnSearchExec.addEventListener('click', executeSearch);

    elSearchTabs.addEventListener('click', (e) => {
      const tab = e.target.closest('.search-tab');
      if (!tab) return;
      const mode = tab.getAttribute('data-mode');
      setSearchMode(mode);
    });

    elCategoryRibbon.addEventListener('click', (e) => {
      const pill = e.target.closest('.cat-pill');
      if (!pill) return;
      document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeCategoryGroup = pill.getAttribute('data-filter-group');
      filterByCategory(activeCategoryGroup);
    });

    document.querySelectorAll('.bang-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const bang = chip.getAttribute('data-bang');
        elMainSearch.value = bang;
        elMainSearch.focus();
        handleSearchInput(bang);
      });
    });

    document.querySelectorAll('.es-syntax-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const syn = pill.getAttribute('data-syntax');
        setSearchMode('everything');
        elMainSearch.value = syn + ' ';
        elMainSearch.focus();
        runEverythingSearch(elMainSearch.value.trim());
      });
    });

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
      passInput.type = passInput.type === 'password' ? 'text' : 'password';
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

    // Global Hotkeys
    window.addEventListener('keydown', (e) => {
      const isInputActive = document.activeElement && (
        document.activeElement.tagName === 'INPUT' || 
        document.activeElement.tagName === 'TEXTAREA' || 
        document.activeElement.isContentEditable
      );

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        openCommandPalette();
        return;
      }

      if (!isInputActive) {
        if (e.key === '/') {
          e.preventDefault();
          elMainSearch.focus();
          elMainSearch.select();
          return;
        } else if (e.key === '?' || (e.shiftKey && e.key === '/')) {
          e.preventDefault();
          openShortcutsModal();
          return;
        }
      }

      if (hoveredLink && !isInputActive) {
        const key = e.key.toLowerCase();
        if (key === 'c') {
          e.preventDefault();
          navigator.clipboard.writeText(hoveredLink.url);
          hoveredLink.element.classList.remove('pulse-copy');
          void hoveredLink.element.offsetWidth;
          hoveredLink.element.classList.add('pulse-copy');
          showToast(`[COPIED] ${hoveredLink.title}`);
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
      showToast(`[PINNED] ${linkObj.title}`);
    } else {
      userFavorites.splice(idx, 1);
      linkObj.element.classList.remove('is-pinned');
      const pinIcon = linkObj.element.querySelector('.link-pin-indicator');
      if (pinIcon) pinIcon.style.display = 'none';
      showToast(`[UNPINNED] ${linkObj.title}`);
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
      elEngineBadge.textContent = 'FILTER';
      elEngineBadge.style.color = 'var(--accent-cyan)';
      elMainSearch.placeholder = 'Fuzzy search 1,699+ OSINT, Australian & AI tools... (Press / to focus, Ctrl+K for Palette)';
      elEsPanel.classList.remove('visible');
    } else if (mode === 'everything') {
      elEngineBadge.textContent = 'EVERYTHING';
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
      elEngineBadge.textContent = mode.toUpperCase();
      elEngineBadge.style.color = 'var(--accent-blue)';
      elMainSearch.placeholder = `Search with ${mode.toUpperCase()}... (Press Enter)`;
      elEsPanel.classList.remove('visible');
    }
  }

  let searchDebounceTimer = null;
  function handleSearchInput(val) {
    clearTimeout(searchDebounceTimer);

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

        // Check for direct modal launcher bangs
        if (bang === 'user' || bang === 'recon') {
          elMainSearch.value = '';
          openSocialRecon(query);
          return;
        } else if (bang === 'corp' || bang === 'acn' || bang === 'abn') {
          elMainSearch.value = '';
          openCorpRecon(query);
          return;
        } else if (bang === 'defang' || bang === 'refang' || bang === 'ioc') {
          elMainSearch.value = '';
          openDefanger(query);
          return;
        } else if (bang === 'pivot') {
          elMainSearch.value = '';
          openPivotMatrix(query);
          return;
        } else if (bang === 'dorks' || bang === 'dork') {
          elMainSearch.value = '';
          if (query) elDorkTargetInput.value = query;
          openDorkGenerator();
          return;
        } else if (bang === 'geo') {
          elMainSearch.value = '';
          openGeoRecon(query);
          return;
        } else if (bang === 'graph') {
          elMainSearch.value = '';
          openInvestigationGraph();
          return;
        } else if (bang === 'radar' || bang === 'acsc') {
          elMainSearch.value = '';
          openThreatRadar();
          return;
        }

        if (bangMap[bang] && bangMap[bang] !== activeSearchMode) {
          setSearchMode(bangMap[bang]);
          elMainSearch.value = query;
          val = query;
        }
      }
    }

    // Dynamic bang chip matching and highlighting
    const bangChips = document.querySelectorAll('.bang-chip');
    if (val.startsWith('!')) {
      const typed = val.toLowerCase().trim();
      let firstFound = false;
      bangChips.forEach(chip => {
        const b = chip.getAttribute('data-bang').toLowerCase().trim();
        if (b.startsWith(typed) || typed.startsWith(b.split(' ')[0])) {
          chip.classList.add('bang-active-match');
          if (!firstFound) {
            chip.style.transform = 'scale(1.04)';
            firstFound = true;
          } else {
            chip.style.transform = '';
          }
        } else {
          chip.classList.remove('bang-active-match');
          chip.style.transform = '';
        }
      });
    } else {
      bangChips.forEach(chip => {
        chip.classList.remove('bang-active-match');
        chip.style.transform = '';
      });
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

    const engine = (appData.search_engines || []).find(e => e.id === activeSearchMode);
    if (engine && engine.url) {
      const targetUrl = engine.url.replace('%s', encodeURIComponent(query));
      window.open(targetUrl, '_blank', 'noopener,noreferrer');
    } else {
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
    const matchBadge = document.getElementById('search-live-matches');

    if (!q) {
      if (matchBadge) matchBadge.style.display = 'none';
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

    if (matchBadge) {
      matchBadge.style.display = 'inline-flex';
      matchBadge.textContent = `${matchCount} MATCH${matchCount === 1 ? '' : 'ES'}`;
      matchBadge.style.color = matchCount > 0 ? 'var(--accent-cyan)' : '#f43f5e';
      matchBadge.style.borderColor = matchCount > 0 ? 'var(--accent-cyan)' : '#f43f5e';
    }

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

    elEsResultsList.innerHTML = '<div class="es-empty-state" style="color:var(--accent-green);">Searching Voidtools Everything index...</div>';

    let augmentedQuery = query;
    if (activeEsFilter === 'docs') augmentedQuery += ' ext:pdf;docx;doc;txt;xlsx;csv;pptx;md';
    else if (activeEsFilter === 'data') augmentedQuery += ' ext:json;py;js;html;css;sql;xml;yaml;yml';
    else if (activeEsFilter === 'archives') augmentedQuery += ' ext:zip;7z;rar;tar;gz;iso';
    else if (activeEsFilter === 'media') augmentedQuery += ' ext:jpg;jpeg;png;gif;mp4;mkv;avi;mp3;wav';

    try {
      let results = [];
      let total = 0;

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
                <p style="font-size:1rem;font-weight:700;">[AUTH REQUIRED] HTTP 401</p>
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
        const headers = {};
        if (settings.esUsername || settings.esPassword) {
          headers['Authorization'] = 'Basic ' + btoa(unescape(encodeURIComponent((settings.esUsername || '') + ':' + (settings.esPassword || ''))));
        }
        const url = `${(settings.esHttpUrl || 'http://127.0.0.1:8080').replace(/\/+$/, '')}/?search=${encodeURIComponent(augmentedQuery)}&json=1&count=50`;
        const res = await fetch(url, { headers });
        if (res.status === 401) {
          elEsResultsList.innerHTML = `
            <div class="es-empty-state" style="color:var(--accent-amber);">
              <p style="font-size:1rem;font-weight:700;">[AUTH REQUIRED] HTTP 401</p>
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
      elEsResultsList.innerHTML = `<div class="es-empty-state" style="color:#f43f5e;">[ERROR] Connecting to Everything backend: ${escapeHtml(e.message)}</div>`;
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
            <button class="btn-es-action btn-open-file" title="Launch file in default viewer">Open</button>
            <button class="btn-es-action btn-reveal-file" title="Reveal in Windows Explorer">Explorer</button>
            <button class="btn-es-action btn-copy-path" title="Copy absolute path">Copy</button>
          </div>
        </div>
      `;
    }).join('');

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
      showToast('Opening files via OS requires running through local desktop server (start_bubbsy.bat)', 'error');
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
          statusMsg.textContent = '[OK] Connected successfully to Everything HTTP server';
          statusMsg.style.color = 'var(--accent-green)';
        } else if (data.auth_required) {
          statusMsg.textContent = '[AUTH REQUIRED] HTTP 401: Invalid username or password';
          statusMsg.style.color = 'var(--accent-amber)';
        } else if (data.cli_ok) {
          statusMsg.textContent = '[OK] Connected via es.exe CLI IPC bridge';
          statusMsg.style.color = 'var(--accent-green)';
        } else {
          statusMsg.textContent = `[OFFLINE] ${data.details.http || data.details.cli || 'Could not connect'}`;
          statusMsg.style.color = '#f43f5e';
        }
      }
    } catch (e) {
      statusMsg.textContent = `[ERROR] Connection error: ${e.message}`;
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

    const actions = [
      { id: 'act_social_recon', title: 'Social Handle & Username Recon Engine (Maigret / Sherlock)', category: 'ACTIONS', icon: 'RECON', action: () => openSocialRecon() },
      { id: 'act_corp', title: 'Australian Corporate & Beneficial Ownership Network (ASIC / ABN)', category: 'ACTIONS', icon: 'CORP', action: () => openCorpRecon() },
      { id: 'act_defang', title: 'Tactical Cyber Defang / Refang & Structured IOC Normalizer', category: 'ACTIONS', icon: 'DEFANG', action: () => openDefanger() },
      { id: 'act_acsc', title: '[AUS] ASD / ACSC Cyber Advisories & Essential 8 Matrix', category: 'ACTIONS', icon: 'ACSC', action: () => { openThreatRadar(); document.getElementById('tab-radar-acsc').click(); } },
      { id: 'act_dorks', title: 'Threat Dork & Attack Surface Generator', category: 'ACTIONS', icon: 'DORKS', action: () => openDorkGenerator() },
      { id: 'act_geo', title: 'Australian Cadastre & Geo-Coordinate Recon', category: 'ACTIONS', icon: 'GEO', action: () => openGeoRecon() },
      { id: 'act_pivot', title: 'OSINT Pivot Matrix', category: 'ACTIONS', icon: 'PIVOT', action: () => openPivotMatrix() },
      { id: 'act_radar', title: 'Threat Intel & CVE Live Radar', category: 'ACTIONS', icon: 'RADAR', action: () => openThreatRadar() },
      { id: 'act_graph', title: 'Visual Investigation Link Graph', category: 'ACTIONS', icon: 'GRAPH', action: () => openInvestigationGraph() },
      { id: 'act_export', title: 'Export Incident Session & Markdown Dossier', category: 'ACTIONS', icon: 'EXPORT', action: () => openSessionExport() },
      { id: 'act_tour', title: 'Replay Mission Briefing Tour', category: 'ACTIONS', icon: 'TOUR', action: () => startOnboardingTour() },
      { id: 'act_shortcuts', title: 'Keyboard Shortcuts & Bang Matrix Cheatsheet', category: 'ACTIONS', icon: 'KEYS', action: () => openShortcutsModal() },
      { id: 'act_theme', title: 'Switch HUD Theme (Cyber / Matrix / Dracula)', category: 'ACTIONS', icon: 'THEME', action: () => cycleTheme() },
      { id: 'act_es', title: 'Voidtools Everything Local Search', category: 'ACTIONS', icon: 'FILES', action: () => { setSearchMode('everything'); elMainSearch.focus(); } }
    ];

    actions.forEach(a => {
      if (!q || a.title.toLowerCase().includes(q)) items.push(a);
    });

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
                icon: link.title.startsWith('[AUS]') ? 'AUS' : (w.group === 'ai_hub' ? 'AI' : 'LINK'),
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
            <span class="palette-item-icon" style="font-family:var(--font-mono);font-size:0.62rem;font-weight:700;color:var(--accent-cyan);">[${item.icon || 'TOOL'}]</span>
            <span class="palette-item-title">${highlightMatch(item.title, q)}</span>
          </div>
          <span class="palette-item-tag">${escapeHtml(item.category)}</span>
        </div>
      `;
    });

    elPaletteResults.innerHTML = html;

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
    if (/^(?:\+?61|0)[2-478](?:[ -]?\d){8}$/.test(val)) return 'AU_PHONE';
    if (/^\+?\d{8,15}$/.test(val.replace(/[\s()-]/g, ''))) return 'PHONE';
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
          Enter any IP address, domain, file hash, email, phone number, CVE, or Australian ABN/ACN to generate real-time OSINT pivots.
        </div>
      `;
      return;
    }

    const encoded = encodeURIComponent(val);
    let categories = [];

    if (type === 'IP') {
      categories = [
        {
          name: 'Network & Host Intel',
          pivots: [
            { name: 'Shodan Host Lookup', url: `https://www.shodan.io/host/${val}` },
            { name: 'Censys Host Search', url: `https://search.censys.io/hosts/${val}` },
            { name: 'AbuseIPDB Reputation', url: `https://www.abuseipdb.com/check/${val}` },
            { name: 'GreyNoise Visualizer', url: `https://viz.greynoise.io/ip/${val}` },
            { name: 'IPinfo Geolocation', url: `https://ipinfo.io/${val}` }
          ]
        },
        {
          name: 'Threat & Malware Pivots',
          pivots: [
            { name: 'VirusTotal IP Report', url: `https://www.virustotal.com/gui/ip-address/${val}` },
            { name: 'ThreatMiner IP Details', url: `https://www.threatminer.org/host.php?q=${val}` },
            { name: 'AlienVault OTX Pulse', url: `https://otx.alienvault.com/indicator/ip/${val}` }
          ]
        },
        {
          name: 'Australian & APNIC Routing',
          pivots: [
            { name: 'APNIC WHOIS Lookup', url: `https://wq.apnic.net/static/search.html?query=${val}` },
            { name: 'Aussie Broadband Looking Glass', url: `https://looking-glass.aussiebroadband.com.au/` }
          ]
        }
      ];
    } else if (type === 'DOMAIN') {
      categories = [
        {
          name: 'Domain & Passive DNS',
          pivots: [
            { name: 'urlscan.io Submission', url: `https://urlscan.io/search/#${encoded}` },
            { name: 'VirusTotal Domain Report', url: `https://www.virustotal.com/gui/domain/${val}` },
            { name: 'SecurityTrails DNS History', url: `https://securitytrails.com/domain/${val}/dns` },
            { name: 'crt.sh Certificate Search', url: `https://crt.sh/?q=${encoded}` }
          ]
        },
        {
          name: 'Australian Registrar Intel',
          pivots: [
            { name: 'auDA .au WHOIS Search', url: `https://www.auda.org.au/tools/whois` },
            { name: 'ABN Lookup Associated Entity', url: `https://abr.business.gov.au/Search/ResultsActive?SearchText=${encoded}` }
          ]
        },
        {
          name: 'Web Archive & History',
          pivots: [
            { name: 'Wayback Machine History', url: `https://web.archive.org/web/*/${val}` }
          ]
        }
      ];
    } else if (type === 'HASH') {
      categories = [
        {
          name: 'Malware & Sandboxes',
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
          name: 'Vulnerability & Exploit Databases',
          pivots: [
            { name: 'NIST National Vulnerability Database', url: `https://nvd.nist.gov/vuln/detail/${val}` },
            { name: 'CVE Details Exploit Vector', url: `https://www.cvedetails.com/cve/${val}/` },
            { name: 'VulnCheck Community Exploit Feed', url: `https://vulncheck.com/` },
            { name: 'ExploitDB Zero-Day Exploits', url: `https://www.exploit-db.com/search?cve=${val.replace(/CVE-/i, '')}` }
          ]
        }
      ];
    } else if (type === 'EMAIL') {
      categories = [
        {
          name: 'Identity & Breach Intelligence',
          pivots: [
            { name: 'HaveIBeenPwned Check', url: `https://haveibeenpwned.com/account/${encoded}` },
            { name: 'Epieos Google & Social Lookup', url: `https://epieos.com/?q=${encoded}` },
            { name: 'Hunter.io Domain Search', url: `https://hunter.io/search/${encoded.split('%40')[1] || ''}` },
            { name: 'DeHashed Breach Records', url: `https://www.dehashed.com/search?query=${encoded}` }
          ]
        }
      ];
    } else if (type === 'AU_PHONE' || type === 'PHONE') {
      categories = [
        {
          name: 'Telephone & Identity Intelligence',
          pivots: [
            { name: 'Reverse Australia Directory', url: `https://www.reverseaustralia.com/lookup/${val.replace(/\s+/g, '')}` },
            { name: 'Truecaller Search', url: `https://www.truecaller.com/search/au/${val.replace(/[\s+]/g, '')}` },
            { name: 'Sync.me Phone Lookup', url: `https://sync.me/search/?number=${val.replace(/\s+/g, '')}` }
          ]
        }
      ];
    } else if (type === 'AU_ABN') {
      categories = [
        {
          name: 'Australian Corporate Registry',
          pivots: [
            { name: 'ABN Lookup Official Register', url: `https://abr.business.gov.au/Search/ResultsActive?SearchText=${encoded}` },
            { name: 'ASIC Connect Company Lookup', url: `https://connectonline.asic.gov.au/` },
            { name: 'AFSA Bankruptcy Register (NPII)', url: `https://www.afsa.gov.au/` },
            { name: 'AusTender Contract History', url: `https://www.tenders.gov.au/` },
            { name: 'OpenCorporates AU', url: `https://opencorporates.com/companies/au?q=${encoded}` }
          ]
        }
      ];
    } else {
      categories = [
        {
          name: 'Universal Multi-Engine Pivot',
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
  // 3. THREAT INTEL & CVE LIVE RADAR + ACSC AUSTRALIA
  // =========================================================================
  let activeRadarFeed = 'cisa'; // 'cisa' or 'acsc'
  let activeRadarCategoryFilter = 'all'; // 'all', 'ransomware', 'essential8', 'critical'
  let currentRenderedRadarItems = [];

  async function fetchThreatRadarFeed(feedType = activeRadarFeed) {
    activeRadarFeed = feedType;
    const endpoint = feedType === 'acsc' ? '/api/acsc/feed?limit=40' : '/api/radar/feed?limit=40';
    try {
      const res = await fetch(endpoint);
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
    let filtered = radarFeedData.filter(i => 
      !f || i.id.toLowerCase().includes(f) || i.title.toLowerCase().includes(f) || (i.vendor && i.vendor.toLowerCase().includes(f)) || (i.publisher && i.publisher.toLowerCase().includes(f)) || i.description.toLowerCase().includes(f) || (i.essential_eight_pillar && i.essential_eight_pillar.toLowerCase().includes(f))
    );

    if (activeRadarCategoryFilter === 'ransomware') {
      filtered = filtered.filter(i => i.ransomware || (i.description && i.description.toLowerCase().includes('ransomware')));
    } else if (activeRadarCategoryFilter === 'essential8') {
      filtered = filtered.filter(i => i.essential_eight_pillar);
    } else if (activeRadarCategoryFilter === 'critical') {
      filtered = filtered.filter(i => i.severity === 'CRITICAL' || i.severity === 'HIGH');
    }

    currentRenderedRadarItems = filtered;

    if (!filtered.length) {
      elRadarItemsList.innerHTML = `<div class="es-empty-state">No advisories match filter "${escapeHtml(filter)}" (${activeRadarCategoryFilter})</div>`;
      return;
    }

    elRadarItemsList.innerHTML = filtered.map(item => `
      <div class="radar-item">
        <div class="radar-item-header">
          <span class="radar-item-title">${escapeHtml(item.title)}</span>
          <span class="radar-badge ${item.severity === 'CRITICAL' ? 'critical' : 'high'}">
            ${item.ransomware ? 'RANSOMWARE' : item.severity}
          </span>
        </div>
        <p class="radar-desc">${escapeHtml(item.description)}</p>
        ${item.essential_eight_pillar ? `<div style="font-size:0.7rem;color:var(--accent-green);margin-bottom:6px;font-family:var(--font-mono);">[Essential 8] ${escapeHtml(item.essential_eight_pillar)}</div>` : ''}
        <div class="radar-meta">
          <span>Added: ${item.date || 'Recent'}</span>
          <span>${item.publisher ? `Publisher: ${escapeHtml(item.publisher)}` : `Vendor: ${escapeHtml(item.vendor || 'Unknown')}`}</span>
          <a href="${item.url}" target="_blank" rel="noopener noreferrer" style="color:var(--accent-cyan);margin-left:auto;text-decoration:none;">View Advisory ↗</a>
          <button class="btn-icon" style="padding:1px 6px;font-size:0.65rem;" onclick="addNodeToGraph('${item.id}', 'cve');">To Graph</button>
        </div>
      </div>
    `).join('');
  }

  document.querySelectorAll('.radar-pill-filter').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.radar-pill-filter').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeRadarCategoryFilter = pill.getAttribute('data-radar-filter') || 'all';
      renderRadarItems(elRadarSearchInput.value.trim());
    });
  });

  document.getElementById('btn-radar-copy-table').addEventListener('click', () => {
    if (!currentRenderedRadarItems.length) {
      showToast('No active advisories to export');
      return;
    }
    let md = `| ID / CVE | Advisory Title | Severity | Publisher / Source | Date | Advisory Link |\n`;
    md += `| :--- | :--- | :--- | :--- | :--- | :--- |\n`;
    currentRenderedRadarItems.forEach(i => {
      md += `| \`${i.id}\` | ${i.title.replace(/\|/g, '-')} | **${i.severity}** | ${i.publisher || i.vendor || 'Unknown'} | ${i.date || 'Recent'} | [View](${i.url}) |\n`;
    });
    navigator.clipboard.writeText(md);
    showToast(`Copied Markdown table with ${currentRenderedRadarItems.length} advisories!`);
  });

  document.getElementById('tab-radar-cisa').addEventListener('click', async () => {
    document.getElementById('tab-radar-cisa').classList.add('active');
    document.getElementById('tab-radar-acsc').classList.remove('active');
    await fetchThreatRadarFeed('cisa');
    renderRadarItems(elRadarSearchInput.value.trim());
  });

  document.getElementById('tab-radar-acsc').addEventListener('click', async () => {
    document.getElementById('tab-radar-acsc').classList.add('active');
    document.getElementById('tab-radar-cisa').classList.remove('active');
    await fetchThreatRadarFeed('acsc');
    renderRadarItems(elRadarSearchInput.value.trim());
  });

  // =========================================================================
  // 3B. SOCIAL HANDLE & USERNAME RECON ENGINE (SHERLOCK / MAIGRET)
  // =========================================================================
  const elModalSocialRecon = document.getElementById('modal-social-recon');
  const elSocialInput = document.getElementById('social-recon-input');
  const elSocialResults = document.getElementById('social-recon-results');
  let activeSocialCategoryFilter = 'all'; // 'all', 'australian', 'dev', 'social'

  function openSocialRecon(username = '') {
    elModalSocialRecon.classList.add('active');
    if (username) elSocialInput.value = username;
    renderSocialReconProfiles(elSocialInput.value.trim());
    setTimeout(() => elSocialInput.focus(), 50);
  }

  function renderSocialReconProfiles(username = '') {
    const u = username.trim();
    if (!u) {
      elSocialResults.innerHTML = `
        <div class="es-empty-state" style="grid-column:1/-1;">
          Enter any username, handle, or alias to generate cross-platform profile links and investigative pivot commands.
        </div>
      `;
      return;
    }

    let platformCategories = [
      {
        id: 'australian',
        name: 'Australian Networks & Forums',
        platforms: [
          { name: 'Whirlpool Forums', url: `https://forums.whirlpool.net.au/user/${u}` },
          { name: 'Overclockers AU (OCAU)', url: `https://forums.overclockers.com.au/members/?username=${u}` },
          { name: 'OzBargain Community', url: `https://www.ozbargain.com.au/user/${u}` },
          { name: 'Gumtree Australia User', url: `https://www.gumtree.com.au/s-user/${u}` }
        ]
      },
      {
        id: 'dev',
        name: 'Developer & Code Registries',
        platforms: [
          { name: 'GitHub Profile', url: `https://github.com/${u}` },
          { name: 'GitLab Profile', url: `https://gitlab.com/${u}` },
          { name: 'Docker Hub Repos', url: `https://hub.docker.com/u/${u}` },
          { name: 'PyPI Python Packages', url: `https://pypi.org/user/${u}` },
          { name: 'npm Package Author', url: `https://www.npmjs.com/~${u}` },
          { name: 'Stack Overflow User', url: `https://stackoverflow.com/users/${u}` }
        ]
      },
      {
        id: 'social',
        name: 'Social Media & Identity',
        platforms: [
          { name: 'Reddit Profile', url: `https://www.reddit.com/user/${u}` },
          { name: 'X / Twitter Profile', url: `https://x.com/${u}` },
          { name: 'Instagram Account', url: `https://www.instagram.com/${u}` },
          { name: 'TikTok Account', url: `https://www.tiktok.com/@${u}` },
          { name: 'LinkedIn Public Search', url: `https://www.linkedin.com/in/${u}` },
          { name: 'Telegram Handle', url: `https://t.me/${u}` },
          { name: 'Bluesky Profile', url: `https://bsky.app/profile/${u}.bsky.social` },
          { name: 'Keybase PGP Identity', url: `https://keybase.io/${u}` }
        ]
      }
    ];

    if (activeSocialCategoryFilter !== 'all') {
      platformCategories = platformCategories.filter(c => c.id === activeSocialCategoryFilter);
    }

    elSocialResults.innerHTML = platformCategories.map(cat => `
      <div class="pivot-category-card">
        <div class="pivot-card-header">${escapeHtml(cat.name)}</div>
        <div class="pivot-btn-chips-container">
          ${cat.platforms.map(p => `
            <button class="pivot-btn-chip social-target-chip" data-url="${p.url}" onclick="window.open('${p.url}', '_blank', 'noopener,noreferrer');">
              <span>${escapeHtml(p.name)}</span>
              <span>↗</span>
            </button>
          `).join('')}
        </div>
      </div>
    `).join('');
  }

  document.querySelectorAll('.social-pill-filter').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.social-pill-filter').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeSocialCategoryFilter = pill.getAttribute('data-social-filter') || 'all';
      renderSocialReconProfiles(elSocialInput.value.trim());
    });
  });

  document.getElementById('btn-open-social-recon').addEventListener('click', () => openSocialRecon());
  document.getElementById('btn-close-social-recon').addEventListener('click', () => elModalSocialRecon.classList.remove('active'));
  document.getElementById('btn-social-recon-search').addEventListener('click', () => renderSocialReconProfiles(elSocialInput.value));
  document.getElementById('social-recon-input').addEventListener('input', (e) => renderSocialReconProfiles(e.target.value));
  document.getElementById('social-recon-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') renderSocialReconProfiles(elSocialInput.value);
  });

  document.getElementById('btn-social-copy-sherlock').addEventListener('click', () => {
    const u = elSocialInput.value.trim() || 'target_user';
    const cmd = `sherlock ${u} --print-found\nmaigret ${u} --tags general,australia --pdf`;
    navigator.clipboard.writeText(cmd);
    showToast(`Copied Sherlock/Maigret syntax for "${u}"`);
  });

  document.getElementById('btn-social-add-to-graph').addEventListener('click', () => {
    const u = elSocialInput.value.trim() || 'target_user';
    addNodeToGraph(`User: ${u}`, 'person');
    openInvestigationGraph();
    elModalSocialRecon.classList.remove('active');
  });

  document.getElementById('btn-social-launch-all').addEventListener('click', () => {
    const chips = elSocialResults.querySelectorAll('.social-target-chip');
    if (!chips.length) {
      showToast('Enter a username first');
      return;
    }
    chips.forEach(c => {
      const url = c.getAttribute('data-url');
      if (url) window.open(url, '_blank', 'noopener,noreferrer');
    });
    showToast(`Launched ${chips.length} profile searches!`);
  });

  // =========================================================================
  // 3C. AUSTRALIAN CORPORATE & BENEFICIAL OWNERSHIP NETWORK
  // =========================================================================
  const elModalCorp = document.getElementById('modal-corp');
  const elCorpInput = document.getElementById('corp-input');
  const elCorpResultsGrid = document.getElementById('corp-results-grid');

  const elCorpValidationBadge = document.getElementById('corp-validation-badge');

  function validateABN(rawDigits) {
    const d = rawDigits.replace(/\D/g, '');
    if (d.length !== 11) return false;
    const weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19];
    let sum = (parseInt(d[0], 10) - 1) * weights[0];
    for (let i = 1; i < 11; i++) {
      sum += parseInt(d[i], 10) * weights[i];
    }
    return sum % 89 === 0;
  }

  function validateACN(rawDigits) {
    const d = rawDigits.replace(/\D/g, '');
    if (d.length !== 9) return false;
    const weights = [8, 7, 6, 5, 4, 3, 2, 1];
    let sum = 0;
    for (let i = 0; i < 8; i++) {
      sum += parseInt(d[i], 10) * weights[i];
    }
    const rem = sum % 10;
    const check = (10 - rem) % 10;
    return parseInt(d[8], 10) === check;
  }

  function openCorpRecon(query = '') {
    elModalCorp.classList.add('active');
    if (query) elCorpInput.value = query;
    renderCorpRecon(elCorpInput.value.trim());
    setTimeout(() => elCorpInput.focus(), 50);
  }

  function renderCorpRecon(query = '') {
    const q = query.trim();
    const digitsOnly = q.replace(/\D/g, '');

    if (elCorpValidationBadge) {
      if (!q) {
        elCorpValidationBadge.style.display = 'none';
      } else if (digitsOnly.length === 11) {
        const isValid = validateABN(digitsOnly);
        const formatted = `${digitsOnly.slice(0, 2)} ${digitsOnly.slice(2, 5)} ${digitsOnly.slice(5, 8)} ${digitsOnly.slice(8, 11)}`;
        elCorpValidationBadge.style.display = 'inline-flex';
        elCorpValidationBadge.textContent = isValid ? `[VALID ABN: ${formatted}]` : `[CHECKSUM FAILED: ${formatted}]`;
        elCorpValidationBadge.style.color = isValid ? 'var(--accent-green)' : '#f43f5e';
        elCorpValidationBadge.style.borderColor = isValid ? 'var(--accent-green)' : '#f43f5e';
      } else if (digitsOnly.length === 9) {
        const isValid = validateACN(digitsOnly);
        const formatted = `${digitsOnly.slice(0, 3)} ${digitsOnly.slice(3, 6)} ${digitsOnly.slice(6, 9)}`;
        elCorpValidationBadge.style.display = 'inline-flex';
        elCorpValidationBadge.textContent = isValid ? `[VALID ACN: ${formatted}]` : `[CHECKSUM FAILED: ${formatted}]`;
        elCorpValidationBadge.style.color = isValid ? 'var(--accent-green)' : '#f43f5e';
        elCorpValidationBadge.style.borderColor = isValid ? 'var(--accent-green)' : '#f43f5e';
      } else {
        elCorpValidationBadge.style.display = 'inline-flex';
        elCorpValidationBadge.textContent = `[ENTITY: ${q.slice(0, 20)}]`;
        elCorpValidationBadge.style.color = 'var(--accent-cyan)';
        elCorpValidationBadge.style.borderColor = 'var(--accent-cyan)';
      }
    }

    if (!q) {
      elCorpResultsGrid.innerHTML = `
        <div class="es-empty-state" style="grid-column:1/-1;">
          Enter any Australian Company Name, ABN (11 digits), or ACN (9 digits) to generate multi-agency corporate intelligence pivots.
        </div>
      `;
      return;
    }

    const encoded = encodeURIComponent(q);

    const corpCategories = [
      {
        name: 'Official Australian Corporate Registries',
        pivots: [
          { name: 'ABN Lookup (Active Register)', url: `https://abr.business.gov.au/Search/ResultsActive?SearchText=${encoded}` },
          { name: 'ASIC Connect Search (ACN / Org)', url: `https://connectonline.asic.gov.au/` },
          { name: 'OpenCorporates AU Corporate Lineage', url: `https://opencorporates.com/companies/au?q=${encoded}` },
          { name: 'ATO Business Portal & GST Status', url: `https://abr.business.gov.au/` }
        ]
      },
      {
        name: 'Government Procurement & Contracts',
        pivots: [
          { name: 'AusTender Federal Contract Awards', url: `https://www.tenders.gov.au/Search/CnSearch?Keywords=${encoded}` },
          { name: 'NSW eTendering Supplier Records', url: `https://www.tenders.nsw.gov.au/` },
          { name: 'Buying for Victoria Procurement Search', url: `https://www.tenders.vic.gov.au/` },
          { name: 'Digital Marketplace (DTA) Seller Directory', url: `https://marketplace.service.gov.au/search/sellers?query=${encoded}` }
        ]
      },
      {
        name: 'Legal, Compliance & Insolvency Intel',
        pivots: [
          { name: 'AFSA National Insolvency Index (NPII)', url: `https://www.afsa.gov.au/` },
          { name: 'ASIC Published Insolvency Notices', url: `https://insolvencynotices.asic.gov.au/` },
          { name: 'AusLII Case Judgments & Rulings', url: `http://www.austlii.edu.au/cgi-bin/sinosrch.cgi?query=${encoded}` },
          { name: 'ACCC Mergers & Public Registers', url: `https://www.accc.gov.au/public-registers` }
        ]
      }
    ];

    elCorpResultsGrid.innerHTML = corpCategories.map(cat => `
      <div class="pivot-category-card">
        <div class="pivot-card-header">${escapeHtml(cat.name)}</div>
        <div class="pivot-btn-chips-container">
          ${cat.pivots.map(p => `
            <button class="pivot-btn-chip corp-target-chip" data-url="${p.url}" onclick="window.open('${p.url}', '_blank', 'noopener,noreferrer');">
              <span>${escapeHtml(p.name)}</span>
              <span>↗</span>
            </button>
          `).join('')}
        </div>
      </div>
    `).join('');
  }

  document.getElementById('btn-open-corp').addEventListener('click', () => openCorpRecon());
  document.getElementById('btn-close-corp').addEventListener('click', () => elModalCorp.classList.remove('active'));
  document.getElementById('btn-corp-search').addEventListener('click', () => renderCorpRecon(elCorpInput.value));
  document.getElementById('corp-input').addEventListener('input', (e) => renderCorpRecon(e.target.value));
  document.getElementById('corp-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') renderCorpRecon(elCorpInput.value);
  });

  document.getElementById('btn-corp-add-to-graph').addEventListener('click', () => {
    const q = elCorpInput.value.trim() || 'Target Corp';
    addNodeToGraph(`Corp: ${q}`, 'org');
    openInvestigationGraph();
    elModalCorp.classList.remove('active');
  });

  document.getElementById('btn-corp-launch-all').addEventListener('click', () => {
    const chips = elCorpResultsGrid.querySelectorAll('.corp-target-chip');
    if (!chips.length) {
      showToast('Enter an entity name first');
      return;
    }
    chips.forEach(c => {
      const url = c.getAttribute('data-url');
      if (url) window.open(url, '_blank', 'noopener,noreferrer');
    });
    showToast(`Launched ${chips.length} corporate registries!`);
  });

  // =========================================================================
  // 3D. TACTICAL CYBER DEFANG / REFANG & IOC NORMALIZER
  // =========================================================================
  const elModalDefang = document.getElementById('modal-defang');
  const elDefangRawInput = document.getElementById('defang-raw-input');
  const elDefangOutput = document.getElementById('defang-output');
  const elDefangSummary = document.getElementById('defang-ioc-summary');

  let extractedIocCache = [];
  let lastExtractedIOCs = { ips: [], domains: [], hashes: [], emails: [] };
  let activeDefangFilter = 'all';

  function openDefanger(rawText = '') {
    elModalDefang.classList.add('active');
    if (rawText) elDefangRawInput.value = rawText;
    setTimeout(() => elDefangRawInput.focus(), 50);
  }

  function defangString(text) {
    return text
      .replace(/https?:\/\//gi, (m) => m.toLowerCase().replace('http', 'hxxp'))
      .replace(/\./g, '[.]')
      .replace(/@/g, '[@]')
      .replace(/:\/\//g, '[://]');
  }

  function refangString(text) {
    return text
      .replace(/hxxps?:\/\//gi, (m) => m.toLowerCase().replace('hxxp', 'http'))
      .replace(/\[\.\]|\(\.\)|\{\.\}/g, '.')
      .replace(/\[@\]|\(@\)|\{@\}/g, '@')
      .replace(/\[:\/\/\]/g, '://');
  }

  function extractAllIOCs(text) {
    const refanged = refangString(text);
    const results = {
      ips: [],
      domains: [],
      hashes: [],
      emails: []
    };

    // IPv4
    const ipRegex = /\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g;
    const ips = refanged.match(ipRegex) || [];
    results.ips = [...new Set(ips)];

    // Hashes (MD5, SHA1, SHA256)
    const hashRegex = /\b[a-fA-F0-9]{64}\b|\b[a-fA-F0-9]{40}\b|\b[a-fA-F0-9]{32}\b/g;
    const hashes = refanged.match(hashRegex) || [];
    results.hashes = [...new Set(hashes)];

    // Emails
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g;
    const emails = refanged.match(emailRegex) || [];
    results.emails = [...new Set(emails)];

    // Domains
    const domainRegex = /\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:com|org|net|gov|edu|au|io|uk|de|ru|cn|xyz|top|info|biz|me|online|site|live)\b/gi;
    const rawDomains = refanged.match(domainRegex) || [];
    const validDomains = rawDomains.filter(d => !results.ips.includes(d) && !results.emails.some(e => e.includes(d)));
    results.domains = [...new Set(validDomains)];

    return results;
  }

  function renderDefangOutput() {
    const iocs = lastExtractedIOCs;
    let out = '';

    if (activeDefangFilter === 'all') {
      out = '=== EXTRACTED STRUCTURED IOCS ===\n\n';
      if (iocs.ips.length) out += `[IP ADDRESSES] (${iocs.ips.length})\n` + iocs.ips.map(i => `  ${i}`).join('\n') + '\n\n';
      if (iocs.domains.length) out += `[DOMAINS] (${iocs.domains.length})\n` + iocs.domains.map(d => `  ${d}`).join('\n') + '\n\n';
      if (iocs.hashes.length) out += `[HASHES] (${iocs.hashes.length})\n` + iocs.hashes.map(h => `  ${h}`).join('\n') + '\n\n';
      if (iocs.emails.length) out += `[EMAILS] (${iocs.emails.length})\n` + iocs.emails.map(e => `  ${e}`).join('\n') + '\n\n';
    } else if (activeDefangFilter === 'ip') {
      out = iocs.ips.join('\n');
    } else if (activeDefangFilter === 'domain') {
      out = iocs.domains.join('\n');
    } else if (activeDefangFilter === 'hash') {
      out = iocs.hashes.join('\n');
    } else if (activeDefangFilter === 'email') {
      out = iocs.emails.join('\n');
    }

    if (!out.trim()) {
      out = 'No indicators found for this filter.';
    }

    elDefangOutput.value = out;
  }

  document.querySelectorAll('.defang-pill-filter').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.defang-pill-filter').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeDefangFilter = pill.getAttribute('data-defang-filter') || 'all';
      renderDefangOutput();
    });
  });

  document.getElementById('btn-open-defang').addEventListener('click', () => openDefanger());
  document.getElementById('btn-close-defang').addEventListener('click', () => elModalDefang.classList.remove('active'));

  document.getElementById('btn-do-defang').addEventListener('click', () => {
    const raw = elDefangRawInput.value;
    if (!raw) return;
    elDefangOutput.value = defangString(raw);
    elDefangSummary.style.display = 'none';
    document.getElementById('defang-filter-bar').style.display = 'none';
    showToast('Defanged indicators for safe sharing');
  });

  document.getElementById('btn-do-refang').addEventListener('click', () => {
    const raw = elDefangRawInput.value;
    if (!raw) return;
    elDefangOutput.value = refangString(raw);
    elDefangSummary.style.display = 'none';
    document.getElementById('defang-filter-bar').style.display = 'none';
    showToast('Refanged indicators for live querying');
  });

  document.getElementById('btn-do-extract-iocs').addEventListener('click', () => {
    const raw = elDefangRawInput.value;
    if (!raw) {
      showToast('Paste raw incident text first');
      return;
    }
    const iocs = extractAllIOCs(raw);
    lastExtractedIOCs = iocs;
    extractedIocCache = [];

    iocs.ips.forEach(i => extractedIocCache.push({ val: i, type: 'ip' }));
    iocs.domains.forEach(d => extractedIocCache.push({ val: d, type: 'domain' }));
    iocs.hashes.forEach(h => extractedIocCache.push({ val: h, type: 'hash' }));
    iocs.emails.forEach(e => extractedIocCache.push({ val: e, type: 'email' }));

    activeDefangFilter = 'all';
    document.querySelectorAll('.defang-pill-filter').forEach(p => p.classList.remove('active'));
    document.querySelector('.defang-pill-filter[data-defang-filter="all"]')?.classList.add('active');
    document.getElementById('defang-filter-bar').style.display = 'flex';

    renderDefangOutput();
    elDefangSummary.style.display = 'block';
    elDefangSummary.innerHTML = `Extracted: <strong>${iocs.ips.length} IPs</strong>, <strong>${iocs.domains.length} Domains</strong>, <strong>${iocs.hashes.length} Hashes</strong>, <strong>${iocs.emails.length} Emails</strong>`;
    showToast(`Extracted ${extractedIocCache.length} IOCs`);
  });

  document.getElementById('btn-defang-copy-plain').addEventListener('click', () => {
    const iocs = lastExtractedIOCs;
    const flatList = [...iocs.ips, ...iocs.domains, ...iocs.hashes, ...iocs.emails];
    if (flatList.length) {
      navigator.clipboard.writeText(flatList.join('\n'));
      showToast(`Copied ${flatList.length} IOCs (clean newline list)`);
    } else {
      const out = elDefangOutput.value;
      if (out) {
        navigator.clipboard.writeText(out);
        showToast('Output copied to clipboard');
      }
    }
  });

  document.getElementById('btn-defang-copy-splunk').addEventListener('click', () => {
    const iocs = lastExtractedIOCs;
    const queries = [];
    if (iocs.ips.length) {
      queries.push(`(src_ip IN (${iocs.ips.map(i => `"${i}"`).join(', ')}) OR dest_ip IN (${iocs.ips.map(i => `"${i}"`).join(', ')}))`);
    }
    if (iocs.domains.length) {
      queries.push(`(query IN (${iocs.domains.map(d => `"${d}"`).join(', ')}) OR domain IN (${iocs.domains.map(d => `"${d}"`).join(', ')}))`);
    }
    if (iocs.hashes.length) {
      queries.push(`(file_hash IN (${iocs.hashes.map(h => `"${h}"`).join(', ')}) OR hash IN (${iocs.hashes.map(h => `"${h}"`).join(', ')}))`);
    }

    if (!queries.length) {
      showToast('Extract IOCs first to generate Splunk query');
      return;
    }

    const splunkQuery = queries.join(' OR\n');
    navigator.clipboard.writeText(splunkQuery);
    showToast('Copied Splunk / Sentinel Query to Clipboard!');
  });

  document.getElementById('btn-defang-clear').addEventListener('click', () => {
    elDefangRawInput.value = '';
    elDefangOutput.value = '';
    elDefangSummary.style.display = 'none';
    document.getElementById('defang-filter-bar').style.display = 'none';
    extractedIocCache = [];
    lastExtractedIOCs = { ips: [], domains: [], hashes: [], emails: [] };
  });

  document.getElementById('btn-defang-add-to-graph').addEventListener('click', () => {
    if (!extractedIocCache.length) {
      // Try extract from raw input if not already extracted
      const raw = elDefangRawInput.value;
      if (raw) {
        document.getElementById('btn-do-extract-iocs').click();
      }
    }

    if (!extractedIocCache.length) {
      showToast('No IOCs to add to graph');
      return;
    }

    extractedIocCache.forEach(ioc => {
      addNodeToGraph(ioc.val, ioc.type);
    });

    openInvestigationGraph();
    elModalDefang.classList.remove('active');
    showToast(`Added ${extractedIocCache.length} IOCs to Link Graph!`);
  });

  // =========================================================================
  // 4. VISUAL INVESTIGATION LINK GRAPH (CANVAS SIMULATION)
  // =========================================================================
  let graphAnimationId = null;
  let isGraphConnectMode = false;
  let connectSourceNode = null;
  let selectedGraphNode = null;
  let draggedNode = null;
  let graphOffset = { x: 0, y: 0 };
  let graphScale = 1.0;
  let isPanningCanvas = false;
  let panStart = { x: 0, y: 0 };

  const elNodeInspector = document.getElementById('graph-node-inspector');
  const elInspectorLabel = document.getElementById('inspector-node-label');
  const elInspectorType = document.getElementById('inspector-node-type');

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

  function setSelectedNode(node) {
    selectedGraphNode = node;
    if (node) {
      elNodeInspector.style.display = 'flex';
      elInspectorLabel.textContent = node.label;
      elInspectorType.textContent = node.type.toUpperCase();
      elInspectorType.style.color = node.color || 'var(--accent-cyan)';
    } else {
      elNodeInspector.style.display = 'none';
    }
  }

  function deleteSelectedNode() {
    if (!selectedGraphNode) return;
    const targetId = selectedGraphNode.id;
    investigationGraph.nodes = investigationGraph.nodes.filter(n => n.id !== targetId);
    investigationGraph.edges = investigationGraph.edges.filter(e => e.source !== targetId && e.target !== targetId);
    localStorage.setItem('bubbsy_investigation_graph', JSON.stringify(investigationGraph));
    showToast(`Deleted node: ${selectedGraphNode.label}`);
    setSelectedNode(null);
  }

  function startGraphSimulation() {
    if (graphAnimationId) cancelAnimationFrame(graphAnimationId);

    const ctx = elCanvas.getContext('2d');
    const nodes = investigationGraph.nodes;
    const edges = investigationGraph.edges;

    function renderLoop() {
      const k = 0.05;
      const rep = 800;
      const damping = 0.85;

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[j].x - nodes[i].x;
          const dy = nodes[j].y - nodes[i].y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          if (dist < 380) {
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

      nodes.forEach(n => {
        if (n !== draggedNode) {
          n.vx *= damping;
          n.vy *= damping;
          n.x += n.vx;
          n.y += n.vy;
        }
      });

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
          ctx.strokeStyle = 'rgba(0, 240, 255, 0.35)';
          ctx.lineWidth = 1.8;
          ctx.stroke();

          if (e.label) {
            const mx = (s.x + t.x) / 2;
            const my = (s.y + t.y) / 2;
            ctx.fillStyle = '#94a3b8';
            ctx.font = '10px monospace';
            ctx.fillText(e.label, mx, my - 4);
          }
        }
      });

      // Draw Nodes
      nodes.forEach(n => {
        const isSelected = selectedGraphNode && selectedGraphNode.id === n.id;

        // Selected halo
        if (isSelected) {
          ctx.beginPath();
          ctx.arc(n.x, n.y, n.radius + 8, 0, Math.PI * 2);
          ctx.strokeStyle = '#00f0ff';
          ctx.lineWidth = 2.5;
          ctx.setLineDash([4, 4]);
          ctx.stroke();
          ctx.setLineDash([]);
        }

        // Outer glow
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + 4, 0, Math.PI * 2);
        ctx.fillStyle = n.color ? `${n.color}22` : 'rgba(0, 240, 255, 0.15)';
        ctx.fill();

        // Node circle
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#0a101f';
        ctx.fill();
        ctx.lineWidth = isSelected ? 2.5 : 1.8;
        ctx.strokeStyle = isSelected ? '#ffffff' : (n.color || 'var(--accent-cyan)');
        ctx.stroke();

        // Node label
        ctx.fillStyle = isSelected ? '#00f0ff' : '#ffffff';
        ctx.font = isSelected ? 'bold 12px sans-serif' : 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(n.label, n.x, n.y + n.radius + 14);

        // Node type badge
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
      id: `node_${Date.now()}_${Math.floor(Math.random()*1000)}`,
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
          showToast(`Connected ${connectSourceNode.label} -> ${clicked.label}`);
          isGraphConnectMode = false;
          connectSourceNode = null;
        }
      } else {
        draggedNode = clicked;
        setSelectedNode(clicked);
      }
    } else {
      setSelectedNode(null);
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

  // Node Inspector Event Handlers
  document.getElementById('btn-inspector-pivot').addEventListener('click', () => {
    if (selectedGraphNode) openPivotMatrix(selectedGraphNode.label);
  });
  document.getElementById('btn-inspector-delete').addEventListener('click', deleteSelectedNode);
  document.getElementById('btn-inspector-close').addEventListener('click', () => setSelectedNode(null));

  // Case Template Loader
  document.getElementById('btn-graph-template').addEventListener('click', () => {
    investigationGraph = {
      nodes: [
        { id: 'n_org', label: 'Atlassian Australia', type: 'org', x: 260, y: 180, vx: 0, vy: 0, radius: 24, color: '#f59e0b' },
        { id: 'n_acn', label: 'ACN 004 044 937', type: 'aus', x: 420, y: 140, vx: 0, vy: 0, radius: 22, color: '#10b981' },
        { id: 'n_dom', label: 'atlassian.com', type: 'domain', x: 380, y: 300, vx: 0, vy: 0, radius: 22, color: '#00ff9d' },
        { id: 'n_ip', label: '104.192.141.1', type: 'ip', x: 540, y: 280, vx: 0, vy: 0, radius: 22, color: '#00f0ff' },
        { id: 'n_cve', label: 'CVE-2023-22515', type: 'cve', x: 240, y: 320, vx: 0, vy: 0, radius: 22, color: '#f43f5e' }
      ],
      edges: [
        { source: 'n_org', target: 'n_acn', label: 'registered_as' },
        { source: 'n_org', target: 'n_dom', label: 'operates' },
        { source: 'n_dom', target: 'n_ip', label: 'resolves_to' },
        { source: 'n_dom', target: 'n_cve', label: 'affected_by' }
      ]
    };
    localStorage.setItem('bubbsy_investigation_graph', JSON.stringify(investigationGraph));
    setSelectedNode(null);
    showToast('Loaded Australian Investigation Case Template!');
  });

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
    showToast(isGraphConnectMode ? 'Click source node then target node to connect' : 'Connection mode cancelled');
  });

  document.getElementById('btn-graph-clear').addEventListener('click', () => {
    if (confirm('Clear all nodes and edges in graph?')) {
      investigationGraph.nodes = [];
      investigationGraph.edges = [];
      localStorage.setItem('bubbsy_investigation_graph', JSON.stringify(investigationGraph));
      setSelectedNode(null);
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

  // Global Delete hotkey when Graph modal is active
  window.addEventListener('keydown', (e) => {
    if (elModalGraph.classList.contains('active') && selectedGraphNode) {
      if (e.key === 'Delete' || e.key === 'Backspace') {
        const isInput = document.activeElement && (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA');
        if (!isInput) {
          e.preventDefault();
          deleteSelectedNode();
        }
      }
    }
  });

  // =========================================================================
  // 5. INCIDENT SESSION & MARKDOWN EXPORT
  // =========================================================================
  function openSessionExport() {
    elModalExport.classList.add('active');
    const elStatGraph = document.getElementById('stat-graph-count');
    const elStatFav = document.getElementById('stat-fav-count');
    const elStatCve = document.getElementById('stat-cve-count');

    if (elStatGraph) elStatGraph.textContent = `GRAPH ENTITIES: ${investigationGraph.nodes.length}`;
    if (elStatFav) elStatFav.textContent = `PINNED TOOLS: ${userFavorites.length}`;
    if (elStatCve) elStatCve.textContent = `RADAR ADVISORIES: ${radarFeedData.length}`;
  }

  function buildDossierMarkdown() {
    const caseName = document.getElementById('export-case-name').value.trim() || 'Bubbsy Incident Report';
    const notes = document.getElementById('export-case-notes').value.trim() || 'No analyst notes recorded.';

    let md = `# ${caseName}\n\n`;
    md += `**Generated:** ${new Date().toISOString()}\n`;
    md += `**Platform:** Bubbsy Start Page | OSINT Command Hub 2.18.0\n\n`;
    md += `## Executive Summary & Analyst Notes\n\n${notes}\n\n`;
    md += `## Indicators of Compromise & Graph Entities\n\n`;
    md += `| Type | Indicator / Entity | Connected Edges |\n| :--- | :--- | :--- |\n`;

    investigationGraph.nodes.forEach(n => {
      const connections = investigationGraph.edges
        .filter(e => e.source === n.id || e.target === n.id)
        .map(e => {
          const other = investigationGraph.nodes.find(o => o.id === (e.source === n.id ? e.target : e.source));
          return `${e.label} -> ${other ? other.label : '?'}`;
        }).join(', ');

      md += `| **${n.type.toUpperCase()}** | \`${n.label}\` | ${connections || 'None'} |\n`;
    });

    md += `\n## Pinned Tools & Methodology References\n\n`;
    userFavorites.forEach(f => {
      md += `- [${f.title}](${f.url}) ${f.description ? '— ' + f.description : ''}\n`;
    });

    return { caseName, md };
  }

  document.getElementById('btn-export-markdown-file').addEventListener('click', () => {
    const { caseName, md } = buildDossierMarkdown();
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${caseName.toLowerCase().replace(/[^a-z0-9]/g, '_')}.md`;
    a.click();
    showToast('Downloaded incident dossier (.md)!');
  });

  document.getElementById('btn-export-copy-md').addEventListener('click', () => {
    const { md } = buildDossierMarkdown();
    navigator.clipboard.writeText(md);
    showToast('Copied Markdown Dossier to Clipboard!');
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
    let title = document.getElementById('bm-title').value.trim();
    const url = document.getElementById('bm-url').value.trim();
    const desc = document.getElementById('bm-desc').value.trim();
    const catId = parseInt(document.getElementById('bm-category').value, 10);
    const isAus = document.getElementById('bm-is-aus')?.checked;

    if (isAus && !title.startsWith('[AUS]')) {
      title = `[AUS] ${title}`;
    }

    const newLink = {
      id: Date.now(),
      title: title,
      url: url,
      description: desc,
      domain: extractDomain(url),
      favicon: `https://f.start.me/${extractDomain(url)}`
    };

    userBookmarks.push({ ...newLink, widgetId: catId, isAus: !!isAus });
    localStorage.setItem('bubbsy_user_bookmarks', JSON.stringify(userBookmarks));

    if (appData && appData.columns) {
      for (const col of appData.columns) {
        const w = col.widgets.find(item => item.id === catId);
        if (w) {
          if (isAus) {
            w.links.unshift(newLink);
          } else {
            w.links.push(newLink);
          }
          break;
        }
      }
    }

    document.getElementById('modal-custom-bookmark').classList.remove('active');
    document.getElementById('form-custom-bookmark').reset();
    renderDashboard();
    showToast(`Added bookmark: ${title}`);
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

  document.getElementById('btn-pivot-copy-urls').addEventListener('click', () => {
    const chips = elPivotMatrixActions.querySelectorAll('.pivot-btn-chip');
    if (!chips.length) {
      showToast('Enter a target indicator first');
      return;
    }
    const lines = [];
    chips.forEach(c => {
      const name = c.querySelector('span')?.textContent?.trim() || 'Pivot';
      const m = c.getAttribute('onclick')?.match(/window\.open\('([^']+)'/);
      if (m && m[1]) {
        lines.push(`- ${name}: ${m[1]}`);
      }
    });
    if (lines.length) {
      navigator.clipboard.writeText(lines.join('\n'));
      showToast(`Copied ${lines.length} pivot URLs to clipboard!`);
    } else {
      showToast('No active pivot links available');
    }
  });

  document.getElementById('btn-pivot-add-to-graph').addEventListener('click', () => {
    const val = elPivotInput.value.trim();
    if (val) {
      const type = detectIndicatorType(val);
      addNodeToGraph(val, type.toLowerCase());
      openInvestigationGraph();
      elModalPivot.classList.remove('active');
    }
  });

  // =========================================================================
  // 6. THREAT DORK & ATTACK SURFACE GENERATOR
  // =========================================================================
  const elModalDorks = document.getElementById('modal-dorks');
  const elDorkTargetInput = document.getElementById('dork-target-input');
  const elDorkPresetsContainer = document.getElementById('dork-presets-container');
  let currentDorksCache = [];

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
        name: 'Australian Gov & Sensitive Records',
        items: [
          { name: 'Confidential PDF Documents', query: `${t ? `site:${t}` : 'site:gov.au'} filetype:pdf ("confidential" OR "restricted" OR "not for public release")` },
          { name: 'Exposed Environment Files (.env)', query: `${t ? `site:${t}` : 'site:gov.au'} filetype:env OR filetype:yml "DB_PASSWORD"` },
          { name: 'Sensitive Spreadsheets (Salaries / PII)', query: `${t ? `site:${t}` : 'site:gov.au'} filetype:xlsx OR filetype:csv ("salary" OR "password" OR "tfn")` },
          { name: 'Open Directory File Indexes', query: `${t ? `site:${t}` : 'site:gov.au'} intitle:"index of" "backup" OR "dump"` }
        ]
      },
      {
        name: 'Cloud Buckets & Database Dumps',
        items: [
          { name: 'AWS S3 Exposed Storage', query: `site:s3.amazonaws.com "${t || 'backup'}"` },
          { name: 'SQL Database Dumps', query: `${sitePrefix}filetype:sql "INSERT INTO" ("admin" OR "password" OR "users")` },
          { name: 'Exposed Git Repositories', query: `${sitePrefix}intitle:"index of" ".git/config"` },
          { name: 'KeePass Password Vaults', query: `${sitePrefix}filetype:kdbx OR filetype:kdb` }
        ]
      },
      {
        name: 'Shodan & Port Attack Surface',
        items: [
          { name: 'Exposed RDP Port 3389', query: t ? `hostname:"${t}" port:3389` : 'port:3389 country:"AU"', isShodan: true },
          { name: 'Open SCADA / Industrial ICS', query: t ? `org:"${t}" port:502` : 'port:502 country:"AU"', isShodan: true },
          { name: 'Admin Dashboards (Grafana / Kibana)', query: t ? `hostname:"${t}" http.title:"Dashboard"` : 'http.title:"Dashboard" country:"AU"', isShodan: true }
        ]
      },
      {
        name: 'GitHub Secret Dorks',
        items: [
          { name: 'API Keys & Secrets in .env', query: `${t || 'org:australian-gov'} filename:.env "SECRET_KEY"`, isGithub: true },
          { name: 'Exposed RSA Private Keys', query: `${t || 'org:australian-gov'} filename:id_rsa`, isGithub: true },
          { name: 'AWS Credentials File', query: `${t || 'org:australian-gov'} path:.aws/credentials`, isGithub: true }
        ]
      }
    ];

    currentDorksCache = dorkGroups;

    elDorkPresetsContainer.innerHTML = dorkGroups.map(grp => `
      <div class="pivot-category-card">
        <div class="pivot-card-header">${escapeHtml(grp.name)}</div>
        <div class="pivot-btn-chips-container">
          ${grp.items.map(item => `
            <div class="pivot-btn-chip" style="flex-direction:column;align-items:flex-start;gap:3px;">
              <div style="display:flex;justify-content:space-between;width:100%;">
                <span style="font-weight:600;color:var(--text-primary);">${escapeHtml(item.name)}</span>
                <span style="display:flex;gap:6px;">
                  <button class="btn-icon" style="padding:0 4px;font-size:0.62rem;" onclick="navigator.clipboard.writeText('${escapeRegex(item.query)}'); showToast('Dork copied!');">Copy</button>
                  <button class="btn-icon" style="padding:0 4px;font-size:0.62rem;color:var(--accent-cyan);" onclick="executeDork('${encodeURIComponent(item.query)}', ${item.isShodan ? "'shodan'" : (item.isGithub ? "'github'" : "'google'")});">Run</button>
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

  document.querySelectorAll('.dork-preset-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      const target = pill.getAttribute('data-target');
      if (target) {
        elDorkTargetInput.value = target;
        renderDorkPresets(target);
        showToast(`Loaded preset target: ${target}`);
      }
    });
  });

  document.getElementById('btn-dork-copy-playbook').addEventListener('click', () => {
    const target = elDorkTargetInput.value.trim() || 'Global Target';
    let md = `# Threat Dorking Recon Playbook: ${target}\n`;
    md += `**Generated:** ${new Date().toISOString()}\n`;
    md += `**Platform:** Bubbsy OSINT Command Engine\n\n`;

    currentDorksCache.forEach(grp => {
      md += `## ${grp.name}\n\n`;
      grp.items.forEach(it => {
        md += `### ${it.name}\n\`\`\`\n${it.query}\n\`\`\`\n\n`;
      });
    });

    navigator.clipboard.writeText(md);
    showToast('Copied Threat Dork Playbook to Clipboard!');
  });

  document.getElementById('btn-dork-add-to-graph').addEventListener('click', () => {
    const target = elDorkTargetInput.value.trim() || 'Target Domain';
    addNodeToGraph(`Target: ${target}`, 'domain');
    openInvestigationGraph();
    elModalDorks.classList.remove('active');
  });

  // =========================================================================
  // 7. AUSTRALIAN CADASTRE & GEO-COORDINATE RECON
  // =========================================================================
  const elModalGeo = document.getElementById('modal-geo');
  const elGeoCoordInput = document.getElementById('geo-coord-input');
  const elGeoMapActions = document.getElementById('geo-map-actions');
  const elGeoTelemetry = document.getElementById('geo-resolved-telemetry');
  const elGeoTelemetryText = document.getElementById('geo-telemetry-text');
  let currentResolvedCoords = { lat: -33.8688, lon: 151.2093 };

  function openGeoRecon(defaultCoords = '') {
    elModalGeo.classList.add('active');
    if (defaultCoords) elGeoCoordInput.value = defaultCoords;
    handleGeoParse(elGeoCoordInput.value.trim());
    setTimeout(() => elGeoCoordInput.focus(), 50);
  }

  function handleGeoParse(input = '') {
    let lat = -33.8688;
    let lon = 151.2093;

    const match = input.match(/(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)/);
    if (match) {
      lat = parseFloat(match[1]);
      lon = parseFloat(match[2]);
    }
    currentResolvedCoords = { lat, lon };

    if (elGeoTelemetry && elGeoTelemetryText) {
      elGeoTelemetry.style.display = 'flex';
      elGeoTelemetryText.textContent = `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
    }

    const mapProviders = [
      {
        name: 'Australian Cadastre',
        items: [
          { name: 'NSW SIX Maps (Cadastral Boundaries)', url: `https://maps.six.nsw.gov.au/` },
          { name: 'VicPlan (Victoria Cadastre)', url: `https://mapshare.vic.gov.au/vicplan/` },
          { name: 'QLD Globe (Queensland Land)', url: `https://qldglobe.information.qld.gov.au/` },
          { name: 'National Map Australia', url: `https://nationalmap.gov.au/#share=s-coordinates` }
        ]
      },
      {
        name: 'Satellite & 3D Imagery',
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

  function decimalToDMS(lat, lon) {
    const latDir = lat >= 0 ? 'N' : 'S';
    const lonDir = lon >= 0 ? 'E' : 'W';
    
    const formatPart = (val, dir) => {
      const abs = Math.abs(val);
      const deg = Math.floor(abs);
      const minFloat = (abs - deg) * 60;
      const min = Math.floor(minFloat);
      const sec = ((minFloat - min) * 60).toFixed(1);
      return `${deg}°${min}'${sec}"${dir}`;
    };

    return `${formatPart(lat, latDir)} ${formatPart(lon, lonDir)}`;
  }

  document.getElementById('btn-open-geo').addEventListener('click', () => openGeoRecon());
  document.getElementById('btn-close-geo').addEventListener('click', () => elModalGeo.classList.remove('active'));
  document.getElementById('btn-geo-parse').addEventListener('click', () => handleGeoParse(elGeoCoordInput.value.trim()));
  document.getElementById('geo-coord-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleGeoParse(elGeoCoordInput.value.trim());
  });

  document.getElementById('btn-geo-copy-coords').addEventListener('click', () => {
    const text = `${currentResolvedCoords.lat}, ${currentResolvedCoords.lon}`;
    navigator.clipboard.writeText(text);
    showToast(`Decimal coordinates copied: ${text}`);
  });

  document.getElementById('btn-geo-copy-dms')?.addEventListener('click', () => {
    const dms = decimalToDMS(currentResolvedCoords.lat, currentResolvedCoords.lon);
    navigator.clipboard.writeText(dms);
    showToast(`DMS coordinates copied: ${dms}`);
  });

  document.getElementById('btn-geo-open-earth').addEventListener('click', () => {
    window.open(`https://earth.google.com/web/search/${currentResolvedCoords.lat},${currentResolvedCoords.lon}`, '_blank', 'noopener,noreferrer');
  });

  document.getElementById('btn-geo-add-to-graph').addEventListener('click', () => {
    const val = elGeoCoordInput.value.trim() || `${currentResolvedCoords.lat}, ${currentResolvedCoords.lon}`;
    addNodeToGraph(`Geo: ${val}`, 'aus');
    openInvestigationGraph();
    elModalGeo.classList.remove('active');
  });

  // Collapse / Expand All Dashboard Categories
  let allCardsCollapsed = false;
  document.getElementById('btn-toggle-all-cards')?.addEventListener('click', () => {
    allCardsCollapsed = !allCardsCollapsed;
    const cards = document.querySelectorAll('.widget-card');
    cards.forEach(card => {
      if (allCardsCollapsed) {
        card.classList.add('collapsed');
      } else {
        card.classList.remove('collapsed');
      }
    });
    const btn = document.getElementById('btn-toggle-all-cards');
    if (btn) btn.textContent = allCardsCollapsed ? 'Expand All' : 'Collapse All';
    showToast(allCardsCollapsed ? 'Collapsed all categories' : 'Expanded all categories');
  });

  // =========================================================================
  // 8. FIRST-TIME ONBOARDING TOUR CONTROLLER
  // =========================================================================
  const elModalTour = document.getElementById('modal-tour');
  const elModalShortcuts = document.getElementById('modal-shortcuts');
  const elTourSlideContainer = document.getElementById('tour-slide-container');
  const elTourDots = document.getElementById('tour-dots');
  const elBtnTourPrev = document.getElementById('btn-tour-prev');
  const elBtnTourNext = document.getElementById('btn-tour-next');
  const elBtnSkipTour = document.getElementById('btn-skip-tour');

  function openShortcutsModal() {
    elModalShortcuts.classList.add('active');
  }

  document.getElementById('btn-close-shortcuts')?.addEventListener('click', () => elModalShortcuts.classList.remove('active'));

  let currentTourSlide = 0;
  const tourSlides = [
    {
      icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>',
      title: 'Mission Briefing: Bubbsy Command Hub',
      desc: 'Welcome to your tactical OSINT & intelligence start page. Loaded with <strong>1,699+ verified tools</strong>, Australian corporate & legal registries, evergreen AI models, and sub-millisecond search.',
      box: 'Australian-First Hierarchy • Voidtools Everything • Clean AI Hub'
    },
    {
      icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
      title: 'Omnisearch & Quick Bang Operators',
      desc: 'Press <kbd class="hud-key">/</kbd> anywhere to focus the search bar. Use bang shortcuts to instantly route queries to specific intelligence providers:',
      box: '!es &lt;file&gt; • !abn &lt;entity&gt; • !trove &lt;archive&gt; • !gpt &lt;prompt&gt; • !shodan &lt;ip&gt;'
    },
    {
      icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>',
      title: 'Zero-Click Hover Hotkeys',
      desc: 'Keep your workspace clean without button clutter. Simply hover your mouse cursor over any tool:',
      box: 'Hover + C &rarr; Copy URL to Clipboard • Hover + F &rarr; Pin to Pinned Tools'
    },
    {
      icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"></rect><line x1="6" y1="8" x2="6.01" y2="8"></line><line x1="10" y1="8" x2="10.01" y2="8"></line><line x1="14" y1="8" x2="14.01" y2="8"></line><line x1="18" y1="8" x2="18.01" y2="8"></line></svg>',
      title: 'Global Command Palette (Ctrl+K)',
      desc: 'Press <kbd class="hud-key cyan">Ctrl+K</kbd> (or <kbd>Cmd+K</kbd>) anywhere to open the Spotlight launcher. Fuzzy search across all tools, local files, and HUD commands in milliseconds.',
      box: 'Arrow Keys ↑ ↓ to navigate • Enter to Launch • ESC to Dismiss'
    },
    {
      icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>',
      title: 'Clue Whiteboard & Threat Pivoting',
      desc: 'Enter any IP, Domain, Hash, CVE, or ABN into the <strong>Pivot Matrix</strong> for instant multi-engine lookups. Connect clues together on the <strong>Link Graph</strong> and export incident dossiers to Markdown.',
      box: 'Multi-Engine Pivots • Interactive Node Canvas • 1-Click Markdown Export'
    },
    {
      icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>',
      title: 'Public Web & Desktop Ready',
      desc: 'Bubbsy is 100% self-contained and ready for public web hosting (GitHub Pages / Vercel / Netlify). When run locally with <code>start_bubbsy.bat</code>, Voidtools Everything local disk indexing unlocks automatically.',
      box: 'Production Ready • 100% Offline Capable • Zero External Dependencies'
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

    const dots = elTourDots.querySelectorAll('.tour-dot');
    dots.forEach((d, idx) => {
      d.classList.toggle('active', idx === currentTourSlide);
    });

    elBtnTourPrev.style.display = currentTourSlide > 0 ? '' : 'none';
    elBtnTourNext.textContent = currentTourSlide === tourSlides.length - 1 ? 'Get Started' : 'Next →';
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
