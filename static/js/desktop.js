/* Desktop window manager for GEEK TECHNOLOGIE */
(function(){
  const APPS = [
    { id:'dashboard', title:'Dashboard', icon:'📊', url:'/dashboard' },
    { id:'products', title:'Produits', icon:'📦', url:'/products' },
    { id:'clients', title:'Clients', icon:'👥', url:'/clients' },
    { id:'invoices', title:'Factures', icon:'🧾', url:'/invoices' },
    { id:'quotations', title:'Devis', icon:'📄', url:'/quotations' },
    { id:'debts', title:'Dettes', icon:'💳', url:'/debts' },
    { id:'suppliers', title:'Fournisseurs', icon:'🏭', url:'/suppliers' },
    { id:'supplier_invoices', title:'Factures Fournisseur', icon:'🧰', url:'/supplier-invoices' },
    { id:'reports', title:'Rapports', icon:'📈', url:'/reports' },
    { id:'bank', title:'Banque', icon:'🏦', url:'/bank-transactions' },
    { id:'scan', title:'Scanner', icon:'🧪', url:'/scan' },
    { id:'barcode', title:'Générateur Codes-Barres', icon:'🏷️', url:'/barcode-generator' },
    { id:'settings', title:'Paramètres', icon:'⚙️', url:'/settings' },
    { id:'daily_recap', title:'Récap Quotidien', icon:'🗓️', url:'/daily-recap' },
    { id:'daily_purchases', title:'Achats Quotidiens', icon:'🛒', url:'/daily-purchases' },
    { id:'migration', title:'Migration Données', icon:'🔁', url:'/migration-manager' },
    { id:'cache', title:'Cache', icon:'🧱', url:'/cache-manager' },
    { id:'guide', title:'Guide', icon:'📘', url:'/guide' }
  ];

  let USER_ROLE = 'user'; // admin | manager | cashier | user

  function allowedAppIdsFor(role){
    // Basic roles (cashier and user): strictly limited set
    if (role === 'cashier' || role === 'user') {
      return new Set(['invoices','quotations','products']);
    }
    // Manager: curated set of business apps (no cache/migration by default; keep settings if desired)
    if (role === 'manager') {
      return new Set([
        'dashboard','products','clients','invoices','quotations','debts',
        'suppliers','supplier_invoices','reports','bank','scan','barcode',
        'daily_recap','daily_purchases','guide','settings' // settings allowed for manager
      ]);
    }
    // Admin: all apps
    if (role === 'admin') {
      return new Set(APPS.map(a => a.id));
    }
    // Unknown roles fallback: behave like basic user
    return new Set(['invoices','quotations','products']);
  }

  const zStack = { top: 10 };
  const windows = new Map();
  const $ = sel => document.querySelector(sel);
  const $$ = sel => Array.from(document.querySelectorAll(sel));

  function renderLaunchpad(list){
    const grid = $('#lpGrid');
    const allowed = allowedAppIdsFor(USER_ROLE);
    grid.innerHTML = list.filter(app => allowed.has(app.id)).map(app => `
      <button class="app-icon" data-app="${app.id}">
        <div class="app-emoji">${app.icon}</div>
        <div class="app-label">${escapeHtml(app.title)}</div>
      </button>
    `).join('');
  }

  function anyWindowVisible(){
    for (const w of windows.values()) {
      if (!w.el.classList.contains('hide')) return true;
    }
    return false;
  }

  function updateLaunchpadVisibility(){
    const hasVisible = anyWindowVisible();
    toggleLaunchpad(!hasVisible);
  }

  function filterLaunchpad(q){
    const t = (q||'').toLowerCase();
    renderLaunchpad(APPS.filter(a => a.title.toLowerCase().includes(t)));
  }

  function escapeHtml(s){
    return (s||'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
  }

  function toggleLaunchpad(force){
    const el = $('#launchpad');
    const show = force === true || (force !== false && el.classList.contains('hidden'));
    el.classList.toggle('hidden', !show);
  }

  function bringToFront(win){ win.style.zIndex = String(++zStack.top); }

  function createWindow(app){
    // Reuse if already open
    if (windows.has(app.id)) {
      const w = windows.get(app.id);
      w.el.classList.remove('hide');
      bringToFront(w.el);
      updateLaunchpadVisibility();
      return w;
    }
    const el = document.createElement('div');
    el.className = 'win';
    el.style.left = `${24 + (windows.size*24)%200}px`;
    el.style.top = `${24 + (windows.size*16)%160}px`;
    // Dynamic default size based on viewport (bigger by default)
    const vw = window.innerWidth || document.documentElement.clientWidth || 1280;
    const vh = window.innerHeight || document.documentElement.clientHeight || 800;
    const defaultW = Math.min(1280, Math.max(980, Math.round(vw * 0.72)));
    const defaultH = Math.min(860, Math.max(640, Math.round(vh * 0.72)));
    el.style.width = defaultW + 'px';
    el.style.height = defaultH + 'px';
    el.innerHTML = `
      <div class="win-header">
        <div class="win-traffic">
          <span class="dot close" title="Fermer"></span>
          <span class="dot min" title="Masquer"></span>
          <span class="dot max" title="Plein écran"></span>
        </div>
        <div class="win-title">${escapeHtml(app.title)}</div>
        <div class="win-actions">
          <button class="btn btn-sm btn-outline-light tile-left">Gauche</button>
          <button class="btn btn-sm btn-outline-light tile-right">Droite</button>
          <button class="btn btn-sm btn-outline-light tile-full">Plein</button>
        </div>
      </div>
      <div class="win-body"><iframe src="${app.url}?embed=1" referrerpolicy="no-referrer"></iframe></div>
      <div class="win-resize" title="Redimensionner"></div>
    `;
    $('#windows').appendChild(el);
    const w = { id: app.id, el, app };
    windows.set(app.id, w);
    wireWindow(w);
    ensureDockIcon(app);
    bringToFront(el);
    updateLaunchpadVisibility();
    return w;
  }

  function wireWindow(w){
    const header = w.el.querySelector('.win-header');
    const closeBtn = w.el.querySelector('.dot.close');
    const minBtn = w.el.querySelector('.dot.min');
    const maxBtn = w.el.querySelector('.dot.max');
    const rHandle = w.el.querySelector('.win-resize');

    header.addEventListener('mousedown', startDrag.bind(null, w));
    w.el.addEventListener('mousedown', () => bringToFront(w.el));

    // Prevent drag when interacting with controls
    [closeBtn, minBtn, maxBtn].forEach(btn => btn.addEventListener('mousedown', (e)=>{ e.stopPropagation(); }));

    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      w.el.remove();
      windows.delete(w.id);
      setDockActive(w.id, false);
      removeDockIcon(w.id);
      updateDockVisibility();
      updateLaunchpadVisibility();
    });
    minBtn.addEventListener('click', (e) => { e.stopPropagation(); w.el.classList.add('hide'); setDockActive(w.id, true); updateLaunchpadVisibility(); });
    maxBtn.addEventListener('click', (e) => { e.stopPropagation(); tileWindow(w, 'full'); });

    const btnLeft = w.el.querySelector('.win-actions .tile-left');
    const btnRight = w.el.querySelector('.win-actions .tile-right');
    const btnFull = w.el.querySelector('.win-actions .tile-full');
    [btnLeft, btnRight, btnFull].forEach(btn => btn.addEventListener('mousedown', (e)=>{ e.stopPropagation(); }));
    btnLeft.addEventListener('click', (e) => { e.stopPropagation(); tileWindow(w, 'left'); updateLaunchpadVisibility(); });
    btnRight.addEventListener('click', (e) => { e.stopPropagation(); tileWindow(w, 'right'); updateLaunchpadVisibility(); });
    btnFull.addEventListener('click', (e) => { e.stopPropagation(); tileWindow(w, 'full'); updateLaunchpadVisibility(); });

    rHandle.addEventListener('mousedown', startResize.bind(null, w));
  }

  function startDrag(w, ev){
    if (ev.button !== 0) return;
    const rect = w.el.getBoundingClientRect();
    const offX = ev.clientX - rect.left;
    const offY = ev.clientY - rect.top;
    // If was tiled/full, exit tiling to free-move
    w.el.classList.remove('tile-left','tile-right','tile-full');
    updateDockVisibility();
    function move(e){
      const x = Math.max(0, Math.min(window.innerWidth - rect.width, e.clientX - offX));
      const y = Math.max(0, Math.min(window.innerHeight - rect.height - 80, e.clientY - offY));
      Object.assign(w.el.style, { left: x+"px", top: y+"px", right:'', bottom:'' });
    }
    function up(){
      document.removeEventListener('mousemove', move);
      document.removeEventListener('mouseup', up);
    }
    document.addEventListener('mousemove', move);
    document.addEventListener('mouseup', up);
  }

  function startResize(w, ev){
    ev.stopPropagation();
    const rect = w.el.getBoundingClientRect();
    const start = { x: ev.clientX, y: ev.clientY, w: rect.width, h: rect.height };
    function move(e){
      const nw = Math.max(420, start.w + (e.clientX - start.x));
      const nh = Math.max(300, start.h + (e.clientY - start.y));
      Object.assign(w.el.style, { width: nw+"px", height: nh+"px", right:'', bottom:'' });
    }
    function up(){
      document.removeEventListener('mousemove', move);
      document.removeEventListener('mouseup', up);
    }
    document.addEventListener('mousemove', move);
    document.addEventListener('mouseup', up);
  }

  function tileWindow(w, where){
    w.el.classList.remove('tile-left','tile-right','tile-full');
    // Clear inline geometry so CSS classes can control layout
    Object.assign(w.el.style, { left:'', right:'', top:'', bottom:'', width:'', height:'' });
    if (where === 'left') w.el.classList.add('tile-left');
    else if (where === 'right') w.el.classList.add('tile-right');
    else if (where === 'full') w.el.classList.add('tile-full');
    updateDockVisibility();
  }

  function ensureDockIcon(app){
    const dock = $('#dockApps');
    let btn = dock.querySelector(`[data-app="${app.id}"]`);
    if (!btn){
      btn = document.createElement('button');
      btn.className = 'dock-item';
      btn.dataset.app = app.id;
      btn.title = app.title;
      btn.innerHTML = `<span style="font-size:20px; line-height:1">${app.icon}</span>`;
      btn.addEventListener('click', () => {
        const existing = windows.get(app.id);
        if (existing && !existing.el.classList.contains('hide')) {
          existing.el.classList.add('hide');
          updateLaunchpadVisibility();
        } else if (existing) {
          existing.el.classList.remove('hide');
          bringToFront(existing.el);
          updateLaunchpadVisibility();
        } else {
          createWindow(app);
        }
      });
      dock.appendChild(btn);
    }
  }

  function setDockActive(id, isActive){
    const btn = document.querySelector(`#dockApps .dock-item[data-app="${id}"]`);
    if (btn) btn.style.outline = isActive ? '2px solid rgba(255,255,255,.6)' : '';
  }

  function removeDockIcon(id){
    const btn = document.querySelector(`#dockApps .dock-item[data-app="${id}"]`);
    if (btn && btn.parentElement) btn.parentElement.removeChild(btn);
  }


  function openAppById(id){
    const app = APPS.find(a => a.id === id);
    const allowed = allowedAppIdsFor(USER_ROLE);
    if (app && allowed.has(app.id)) { createWindow(app); toggleLaunchpad(false); }
  }

  async function init(){
    // Fetch role then render launchpad
    try {
      const resp = await fetch('/api/auth/verify', { credentials: 'include' });
      if (resp.ok) {
        const data = await resp.json();
        USER_ROLE = (data && data.role) ? String(data.role) : 'user';
        // Hydrate top-right user indicator
        try {
          const nameEl = document.querySelector('.top-right-actions .user-name');
          const roleEl = document.querySelector('.top-right-actions .user-role-badge');
          if (nameEl) nameEl.textContent = (data.full_name && data.full_name.trim()) ? data.full_name : (data.username || 'Utilisateur');
          if (roleEl) roleEl.textContent = data.role || 'user';
        } catch(e) {}
      }
    } catch(e) { USER_ROLE = 'user'; }
    renderLaunchpad(APPS);

    // Launchpad events
    $('#showLaunchpad').addEventListener('click', () => toggleLaunchpad());
    $('#lpGrid').addEventListener('click', (e) => {
      const el = e.target.closest('[data-app]');
      if (!el) return;
      openAppById(el.dataset.app);
    });
    $('#lpSearch').addEventListener('input', (e)=> filterLaunchpad(e.target.value));

    // Dock special actions
    $('#tileH').addEventListener('click', () => {
      // Two most recent windows side-by-side horizontally (left/right)
      const ws = Array.from(windows.values()).slice(-2);
      if (ws.length === 1) tileWindow(ws[0], 'full');
      if (ws.length === 2){ tileWindow(ws[0], 'left'); tileWindow(ws[1], 'right'); }
    });
    $('#tileV').addEventListener('click', () => {
      // Same action alias (for now behaves like side-by-side)
      const ws = Array.from(windows.values()).slice(-2);
      if (ws.length === 1) tileWindow(ws[0], 'full');
      if (ws.length === 2){ tileWindow(ws[0], 'left'); tileWindow(ws[1], 'right'); }
    });
    $('#showAll').addEventListener('click', () => {
      windows.forEach(w => w.el.classList.remove('hide'));
      toggleLaunchpad(false);
      updateLaunchpadVisibility();
      updateDockVisibility();
    });

    // Keyboard shortcuts
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') toggleLaunchpad(false);
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'space') { e.preventDefault(); toggleLaunchpad(); }
    });

    // Show Launchpad by default (no windows opened automatically)
    toggleLaunchpad(true);

    // Dock autohide handlers (robust)
    const dock = document.getElementById('dock');
    const hotzone = document.getElementById('hotzone');
    let overDock = false;
    let overHotzone = false;
    let hideTimer = null;

    function isAnyFullscreen(){
      for (const w of windows.values()) {
        if (!w.el.classList.contains('hide') && w.el.classList.contains('tile-full')) return true;
      }
      return false;
    }
    window.updateDockVisibility = updateDockVisibility;

    function scheduleHide(){
      if (hideTimer) clearTimeout(hideTimer);
      hideTimer = setTimeout(() => {
        if (isAnyFullscreen() && !overDock && !overHotzone) dock.classList.add('hidden');
      }, 160);
    }
    function showDock(){
      dock.classList.remove('hidden');
    }

    hotzone.addEventListener('mouseenter', () => { overHotzone = true; showDock(); });
    hotzone.addEventListener('mouseleave', () => { overHotzone = false; scheduleHide(); });
    dock.addEventListener('mouseenter', () => { overDock = true; showDock(); });
    dock.addEventListener('mouseleave', () => { overDock = false; scheduleHide(); });

    // Initialize state based on current layout
    updateDockVisibility();
    updateLaunchpadVisibility();
  }

  function updateDockVisibility(){
    const dock = document.getElementById('dock');
    const desktop = document.getElementById('desktop');
    let anyFull = false;
    for (const w of windows.values()) { if (!w.el.classList.contains('hide') && w.el.classList.contains('tile-full')) { anyFull = true; break; } }
    // If any fullscreen and not hovering dock/hotzone, hide; else show
    const shouldHide = (function(){
      try {
        const overDock = dock.matches(':hover');
        const overHot = document.getElementById('hotzone').matches(':hover');
        return anyFull && !(overDock || overHot);
      } catch { return anyFull; }
    })();
    dock.classList.toggle('hidden', shouldHide);
    if (desktop) desktop.classList.toggle('dock-hidden', anyFull);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
