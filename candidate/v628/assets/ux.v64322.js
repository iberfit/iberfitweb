(() => {
  'use strict';
  const english = (document.documentElement.lang || '').toLowerCase().startsWith('en');
  const label = english ? 'Scroll to see more' : 'Desplaza para ver más';
  const definitions = [
    ['.evidence-process-media--v6435', 'Training process', 'Proceso de entrenamiento'],
    ['.system-rail', 'Training system', 'Sistema de entrenamiento'],
    ['.method-cycle', 'Training method cycle', 'Ciclo del método'],
    ['.method-proof-stage', 'Method in practice', 'Método en la práctica'],
    ['.week-flow', 'Training week', 'Semana de entrenamiento'],
    ['.continuity-rail', 'Training continuity', 'Continuidad del entrenamiento'],
    ['.brand-journey--editorial', 'IBERFIT journey', 'Trayectoria de IBERFIT'],
    ['.app-story-stage', 'IBERFIT app views', 'Vistas de la app IBERFIT'],
    ['.review-pair', 'Client experiences', 'Experiencias de clientes'],
    ['.premium-rail', 'Related content', 'Contenido relacionado']
  ];
  const init = () => {
    const rails = new Map();
    for (const [selector, en, es] of definitions) {
      document.querySelectorAll(selector).forEach(rail => {
        if (rails.has(rail)) return;
        let hint = rail.nextElementSibling;
        if (!hint?.classList.contains('mobile-swipe-hint')) {
          hint = document.createElement('p');
          hint.className = 'mobile-swipe-hint';
          rail.insertAdjacentElement('afterend', hint);
        }
        hint.textContent = label;
        hint.setAttribute('aria-hidden', 'true');
        const initial = {
          tabindex: rail.getAttribute('tabindex'),
          role: rail.getAttribute('role'),
          label: rail.getAttribute('aria-label')
        };
        rails.set(rail, {hint, initial, name: english ? en : es});
        rail.addEventListener('keydown', event => {
          if (event.target !== rail || rail.dataset.a11yScroll !== 'true' ||
              event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
          const step = Math.max(1, rail.clientWidth * .8);
          const max = rail.scrollWidth - rail.clientWidth;
          const next = {ArrowLeft: rail.scrollLeft-step, ArrowRight: rail.scrollLeft+step, Home: 0, End: max}[event.key];
          if (next === undefined) return;
          event.preventDefault();
          rail.scrollTo({left: Math.max(0, Math.min(max, next)), behavior: 'instant'});
        });
      });
    }
    const restore = (rail, attribute, original) => {
      if (original === null) rail.removeAttribute(attribute);
      else rail.setAttribute(attribute, original);
    };
    const update = () => {
      for (const [rail, {hint, initial, name}] of rails) {
        const scrollable = /^(auto|scroll)$/.test(getComputedStyle(rail).overflowX) &&
          rail.clientWidth > 0 && rail.scrollWidth - rail.clientWidth > 2;
        hint.hidden = !scrollable;
        if (scrollable && rail.dataset.a11yScroll !== 'true') {
          rail.dataset.a11yScroll = 'true';
          rail.tabIndex = 0;
          if (!rail.hasAttribute('role')) rail.setAttribute('role','region');
          if (!rail.hasAttribute('aria-label') && !rail.hasAttribute('aria-labelledby')) rail.setAttribute('aria-label',name);
        } else if (!scrollable && rail.dataset.a11yScroll === 'true') {
          delete rail.dataset.a11yScroll;
          restore(rail,'tabindex',initial.tabindex);
          restore(rail,'role',initial.role);
          restore(rail,'aria-label',initial.label);
        }
      }
    };
    let frame = 0;
    const schedule = () => {
      if (frame) return;
      frame = requestAnimationFrame(() => { frame=0; update(); });
    };
    update();
    window.addEventListener('resize',schedule,{passive:true});
    window.addEventListener('pageshow',schedule);
    document.fonts?.ready.then(schedule);
    if ('ResizeObserver' in window) {
      const observer = new ResizeObserver(schedule);
      for (const rail of rails.keys()) {
        observer.observe(rail);
        for (const child of rail.children) observer.observe(child);
      }
    }
  };
  if (document.readyState !== 'complete') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
