/* IBERFIT WEB V6.23 · Navigation, conversion UX and privacy-safe behaviour */
document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  const isEn = (document.documentElement.lang || '').toLowerCase().startsWith('en');
  const track = (eventName, params = {}) => {
    try { if (typeof window.iberfitTrack === 'function') window.iberfitTrack(eventName, params); } catch (_) {}
  };
  const normalize = value => String(value || '')
    .toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s-]/g, '').trim().slice(0, 50);

  const zoneBucket = value => {
    const v = normalize(value);
    if (!v) return 'not_selected';
    const local = ['las condes','vitacura','providencia','lo barnechea','nunoa','la reina','penalolen'];
    if (local.some(zone => v.includes(zone))) return 'in_person_service_area';
    if (v.includes('fuera de chile') || v.includes('outside chile')) return 'international';
    return 'outside_primary_area';
  };

  /* Navigation */
  const toggle = document.querySelector('[data-menu-toggle]');
  const nav = document.querySelector('[data-navlinks]');
  const labels = isEn ? { menu:'Menu', close:'Close' } : { menu:'Menú', close:'Cerrar' };
  const closeNav = () => {
    if (!nav || !toggle) return;
    nav.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.textContent = labels.menu;
  };
  if (toggle && nav) {
    toggle.textContent = labels.menu;
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.textContent = open ? labels.close : labels.menu;
      track(open ? 'mobile_menu_open' : 'mobile_menu_close');
    });
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeNav));
    document.addEventListener('click', event => {
      if (nav.classList.contains('open') && !nav.contains(event.target) && !toggle.contains(event.target)) closeNav();
    });
    document.addEventListener('keydown', event => { if (event.key === 'Escape') closeNav(); });
  }

  const header = document.querySelector('.site-header');
  if (header) {
    const updateHeader = () => header.classList.toggle('scrolled', window.scrollY > 20);
    addEventListener('scroll', updateHeader, { passive:true });
    updateHeader();
  }

  /* Reveal animation with accessible fallback */
  const revealElements = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold:.1, rootMargin:'0px 0px -30px 0px' });
    revealElements.forEach(element => observer.observe(element));
  } else {
    revealElements.forEach(element => element.classList.add('visible'));
  }

  /* CTA and contact tracking. No message content is sent. */
  document.querySelectorAll('[data-track]').forEach(element => {
    element.addEventListener('click', () => track(element.dataset.track, {
      cta_position: element.dataset.ctaPosition || 'not_set',
      destination_type: (() => { const href = element.getAttribute('href') || ''; if (href.includes('wa.me')) return 'whatsapp'; if (/^https?:/i.test(href) && !href.includes(location.hostname)) return 'external'; return 'internal'; })()
    }));
  });
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href') || '';
    if (href.startsWith('#') && href.length > 1) {
      link.addEventListener('click', () => track('anchor_navigation', { target: normalize(href.slice(1)) }));
    }
    if (href.includes('wa.me')) {
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.addEventListener('click', () => track('whatsapp_click', {
        page_group: document.body.dataset.page || 'general',
        cta_position: link.dataset.ctaPosition || link.closest('section')?.id || 'content'
      }));
    }
  });

  /* Short format guide. Answers stay in-browser until the user opens WhatsApp. */
  const form = document.querySelector('[data-orientador-form]');
  if (form) {
    const steps = Array.from(form.querySelectorAll('[data-step]'));
    const dots = Array.from(document.querySelectorAll('[data-progress-dot]'));
    const result = form.querySelector('[data-orientador-result]');
    const whatsapp = form.querySelector('[data-orientador-whatsapp]');
    let current = 0;
    let started = false;
    let completed = false;

    const value = name => form.elements[name]?.value?.trim() || '';
    const safeAnalytics = () => ({
      selected_format: normalize(value('modalidad') || 'not_selected'),
      coverage_scope: zoneBucket(value('zona'))
    });
    const showStep = index => {
      current = Math.max(0, Math.min(index, steps.length - 1));
      steps.forEach((step, i) => step.classList.toggle('active', i === current));
      if (result) { result.hidden = true; result.classList.remove('active'); }
      dots.forEach((dot, i) => dot.classList.toggle('active', i <= current));
      steps[current]?.querySelector('select,button')?.focus({ preventScroll:true });
      track('format_guide_step_view', { step:current + 1 });
    };
    const buildMessage = () => {
      const fields = isEn ? [
        ['Main goal', value('objetivo')], ['Training background', value('experiencia')],
        ['Format considered', value('modalidad')], ['Location', value('zona')],
        ['General availability', value('disponibilidad')], ['Training environment', value('material')]
      ] : [
        ['Objetivo principal', value('objetivo')], ['Experiencia', value('experiencia')],
        ['Modalidad considerada', value('modalidad')], ['Ubicación', value('zona')],
        ['Disponibilidad general', value('disponibilidad')], ['Entorno de entrenamiento', value('material')]
      ];
      const intro = isEn
        ? 'Hello IBERFIT, I would like initial guidance about the IRI Assessment.'
        : 'Hola IBERFIT, quiero recibir orientación inicial sobre el Diagnóstico IRI.';
      return [intro, ...fields.filter(([,v]) => v).map(([k,v]) => `${k}: ${v}`)].join('\n');
    };

    form.addEventListener('click', event => {
      const next = event.target.closest('[data-next-step]');
      const previous = event.target.closest('[data-prev-step]');
      if (next) {
        if (!started) { started = true; track('format_guide_start'); }
        if (current === 0 && !value('objetivo')) {
          form.elements.objetivo?.focus();
          track('format_guide_validation', { field:'goal' });
          return;
        }
        track('format_guide_step_complete', { step:current + 1 });
        showStep(current + 1);
      }
      if (previous) showStep(current - 1);
    });
    form.addEventListener('submit', event => {
      event.preventDefault();
      completed = true;
      steps.forEach(step => step.classList.remove('active'));
      if (result) {
        result.hidden = false;
        result.classList.add('active');
        result.focus();
      }
      dots.forEach(dot => dot.classList.add('active'));
      if (whatsapp) whatsapp.href = `https://wa.me/56944040032?text=${encodeURIComponent(buildMessage())}`;
      track('format_guide_complete', safeAnalytics());
    });
    whatsapp?.addEventListener('click', () => track('format_guide_whatsapp_open', safeAnalytics()));
    const reportAbandon = () => {
      if (started && !completed) {
        track('format_guide_abandon', { step:current + 1 });
        started = false;
      }
    };
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') reportAbandon(); });
    addEventListener('pagehide', reportAbandon);

    /* Touch-first choice buttons. Values are not sent to analytics. */
    form.querySelectorAll('select').forEach(select => {
      const grid = document.createElement('div');
      grid.className = 'choice-grid';
      grid.setAttribute('role', 'group');
      const fieldLabel = form.querySelector(`label[for="${select.id}"]`);
      if (fieldLabel) grid.setAttribute('aria-label', fieldLabel.textContent.trim());
      Array.from(select.options).forEach(option => {
        if (!option.value) return;
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'choice-chip';
        button.textContent = option.textContent;
        button.dataset.value = option.value;
        button.addEventListener('click', () => {
          select.value = button.dataset.value;
          select.dispatchEvent(new Event('change', { bubbles:true }));
          grid.querySelectorAll('.choice-chip').forEach(item => item.classList.toggle('is-active', item === button));
          track('format_guide_choice', { field:normalize(select.name || select.id) });
        });
        grid.appendChild(button);
      });
      select.classList.add('is-enhanced');
      select.insertAdjacentElement('afterend', grid);
    });
  }

  /* Mobile quick dock */
  if (header && !document.querySelector('.device-dock')) {
    const hasGuide = Boolean(document.querySelector('#orientador'));
    const dockLabels = isEn
      ? { nav:'IBERFIT mobile navigation', home:'Home', iri:'IRI', guide:'Guide', contact:'Contact' }
      : { nav:'Navegación móvil IBERFIT', home:'Inicio', iri:'IRI', guide:'Orientador', contact:'Contacto' };
    const guideHref = hasGuide ? '#orientador' : (isEn ? '/en/contact/#orientador' : '/contacto/#orientador');
    const contactHref = isEn ? '/en/contact/' : '/contacto/';
    const dock = document.createElement('nav');
    dock.className = 'device-dock';
    dock.setAttribute('aria-label', dockLabels.nav);
    dock.innerHTML = `
      <a href="${isEn ? '/en/' : '/'}" data-dock="home"><strong aria-hidden="true">⌂</strong><span>${dockLabels.home}</span></a>
      <a href="${isEn ? '/en/iri-assessment/' : '/diagnostico-iri/'}" data-dock="iri"><strong>IRI</strong><span>${dockLabels.iri}</span></a>
      <a class="is-primary" href="${guideHref}" data-dock="guide"><img src="/assets/iberfit-isotipo-oficial.png" width="22" height="25" alt="" aria-hidden="true"><span>${dockLabels.guide}</span></a>
      <a href="${contactHref}" data-dock="contact"><strong aria-hidden="true">↗</strong><span>${dockLabels.contact}</span></a>`;
    document.body.appendChild(dock);
    dock.addEventListener('click', event => {
      const link = event.target.closest('a');
      if (link) track('mobile_dock_click', { destination:link.dataset.dock || 'unknown' });
    });
  }
});
