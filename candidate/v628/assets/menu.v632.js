(() => {
  'use strict';
  const init = () => {
    const toggle = document.querySelector('[data-menu-toggle]');
    const nav = document.querySelector('[data-navlinks]');
    const header = document.querySelector('.site-header');
    if (!toggle || !nav || !header) return;
    const compact = matchMedia('(max-width:1380px)');
    const english = document.documentElement.lang.startsWith('en');
    const backdrop = document.createElement('div');
    backdrop.className = 'nav-panel-backdrop';
    backdrop.setAttribute('aria-hidden', 'true');
    document.body.appendChild(backdrop);
    nav.id ||= 'iberfit-nav-panel';
    toggle.setAttribute('aria-controls', nav.id);
    let wasOpen = false;
    let background = [];
    const sync = () => {
      const open = compact.matches && nav.classList.contains('open');
      document.documentElement.style.setProperty('--nav-panel-top', `${Math.round(Math.max(0, header.getBoundingClientRect().bottom) + 8)}px`);
      nav.setAttribute('aria-hidden', String(compact.matches && !open));
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? (english ? 'Close menu' : 'Cerrar menú') : (english ? 'Menu' : 'Menú'));
      document.body.classList.toggle('nav-panel-open', open);
      backdrop.classList.toggle('is-visible', open);
      if (open && !wasOpen) {
        background = Array.from(document.querySelectorAll('main,.site-footer,.device-dock,.wa-float,.site-header .brand,.site-header .nav-cta,.site-header .lang-switch,.consent-banner')).map(el => [el, el.inert]);
        background.forEach(([el]) => { el.inert = true; });
        nav.querySelector('a[href]')?.focus({ preventScroll: true });
      } else if (!open && wasOpen) {
        background.forEach(([el, inert]) => { el.inert = inert; });
        background = [];
        // Preserve native anchor focus when following a same-page destination.
        if (compact.matches && (nav.contains(document.activeElement) || document.activeElement === document.body)) toggle.focus({ preventScroll: true });
      }
      wasOpen = open;
    };
    const close = () => { if (nav.classList.contains('open')) toggle.click(); };
    backdrop.addEventListener('click', close);
    document.addEventListener('keydown', event => {
      if (!compact.matches || !nav.classList.contains('open') || event.key !== 'Tab') return;
      const items = [toggle, ...nav.querySelectorAll('a[href],button:not([disabled])')].filter(el => el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden' && !el.closest('[inert]'));
      const first = items[0], last = items[items.length - 1];
      if (event.shiftKey && (document.activeElement === first || !items.includes(document.activeElement))) {
        event.preventDefault(); last?.focus();
      } else if (!event.shiftKey && (document.activeElement === last || !items.includes(document.activeElement))) {
        event.preventDefault(); first?.focus();
      }
    });
    new MutationObserver(sync).observe(nav, { attributes: true, attributeFilter: ['class'] });
    const resize = () => { if (!compact.matches) close(); sync(); };
    compact.addEventListener('change', resize);
    addEventListener('resize', resize, { passive: true });
    sync();
  };
  document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', init, { once: true }) : init();
})();
