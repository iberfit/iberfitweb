
(() => {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const isEnglish = (document.documentElement.lang || '').toLowerCase().startsWith('en');
  const track = (name, payload = {}) => {
    try {
      if (typeof window.iberfitTrack === 'function') window.iberfitTrack(name, payload);
    } catch (_) {}
  };

  const initReviews = () => {
    const cards = document.querySelector('.review-cards');
    if (!cards || cards.dataset.v629Ready === '1') return;
    const slides = Array.from(cards.querySelectorAll('.client-review'));
    if (slides.length < 2) return;
    if (slides.length === 2) {
      cards.dataset.v629Ready = '1';
      cards.classList.add('review-pair');
      cards.setAttribute('role', 'region');
      cards.setAttribute('aria-label', isEnglish ? 'Real IBERFIT client experiences' : 'Experiencias reales de clientes IBERFIT');
      slides.forEach((slide, index) => {
        slide.classList.remove('reveal');
        slide.classList.add('visible');
        slide.setAttribute('role', 'group');
        slide.setAttribute('aria-label', isEnglish ? `${index + 1} of ${slides.length}` : `${index + 1} de ${slides.length}`);
      });
      return;
    }

    cards.dataset.v629Ready = '1';
    const showcase = cards.closest('.review-showcase');
    if (showcase) showcase.classList.add('is-carousel-ready');

    cards.classList.add('review-carousel');
    cards.setAttribute('role', 'region');
    cards.setAttribute('aria-roledescription', isEnglish ? 'carousel' : 'carrusel');
    cards.setAttribute('aria-label', isEnglish ? 'Real IBERFIT client experiences' : 'Experiencias reales de clientes IBERFIT');

    const shell = document.createElement('div');
    shell.className = 'review-carousel-shell';
    cards.parentNode.insertBefore(shell, cards);
    const stage = document.createElement('div');
    stage.className = 'review-carousel-stage';
    shell.appendChild(stage);
    stage.appendChild(cards);

    let current = 0;
    let timer = 0;
    let manuallyPaused = false;
    let pointerStart = null;
    let hovered = false;
    let focused = false;
    const delay = 6000;

    slides.forEach((slide, index) => {
      // El carrusel controla por completo visibilidad/opacidad. Retirar las
      // clases de reveal evita que dos sistemas de transición compitan entre sí.
      slide.classList.remove('reveal', 'visible');
      slide.classList.add('review-slide');
      slide.dataset.reviewIndex = String(index);
      slide.setAttribute('role', 'group');
      slide.setAttribute('aria-roledescription', isEnglish ? 'review' : 'reseña');
      slide.setAttribute('aria-label', isEnglish ? `${index + 1} of ${slides.length}` : `${index + 1} de ${slides.length}`);
    });

    const controls = document.createElement('div');
    controls.className = 'review-carousel-controls';
    controls.innerHTML = `
      <div class="review-carousel-nav">
        <button class="review-carousel-btn" type="button" data-review-prev aria-label="${isEnglish ? 'Previous review' : 'Reseña anterior'}">←</button>
        <button class="review-carousel-btn" type="button" data-review-pause aria-label="${isEnglish ? 'Pause automatic rotation' : 'Pausar cambio automático'}">Ⅱ</button>
        <button class="review-carousel-btn" type="button" data-review-next aria-label="${isEnglish ? 'Next review' : 'Reseña siguiente'}">→</button>
      </div>
      <div class="review-carousel-dots" role="group" aria-label="${isEnglish ? 'Choose review' : 'Elegir reseña'}"></div>
      <div class="review-carousel-status" aria-hidden="true"></div>
    `;
    shell.appendChild(controls);

    const dots = controls.querySelector('.review-carousel-dots');
    const status = controls.querySelector('.review-carousel-status');
    const pauseButton = controls.querySelector('[data-review-pause]');

    slides.forEach((_, index) => {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'review-carousel-dot';
      dot.setAttribute('aria-pressed', 'false');
      dot.setAttribute('aria-label', isEnglish ? `Show review ${index + 1}` : `Mostrar reseña ${index + 1}`);
      dot.addEventListener('click', () => {
        show(index, 'dot');
        restart();
      });
      dots.appendChild(dot);
    });

    const dotItems = Array.from(dots.children);
    const show = (next, source = 'auto') => {
      const normalized = (next + slides.length) % slides.length;
      slides.forEach((slide, index) => {
        const active = index === normalized;
        slide.classList.toggle('is-active', active);
        slide.setAttribute('aria-hidden', String(!active));
        if ('inert' in slide) slide.inert = !active;
      });
      dotItems.forEach((dot, index) => {
        const active = index === normalized;
        dot.classList.toggle('is-active', active);
        dot.setAttribute('aria-pressed', String(active));
        dot.tabIndex = 0;
      });
      current = normalized;
      status.textContent = `${current + 1} / ${slides.length}`;
      if (source !== 'init' && source !== 'auto') track('review_carousel_change', { source, review: current + 1 });
    };

    const stop = () => {
      if (timer) window.clearInterval(timer);
      timer = 0;
    };
    const start = () => {
      stop();
      if (manuallyPaused || prefersReducedMotion.matches || document.hidden || hovered || focused) return;
      timer = window.setInterval(() => show(current + 1, 'auto'), delay);
    };
    const restart = () => {
      stop();
      start();
    };

    controls.querySelector('[data-review-prev]').addEventListener('click', () => {
      show(current - 1, 'previous');
      restart();
    });
    controls.querySelector('[data-review-next]').addEventListener('click', () => {
      show(current + 1, 'next');
      restart();
    });
    pauseButton.addEventListener('click', () => {
      manuallyPaused = !manuallyPaused;
      pauseButton.textContent = manuallyPaused ? '▶' : 'Ⅱ';
      pauseButton.setAttribute('aria-label', manuallyPaused
        ? (isEnglish ? 'Resume automatic rotation' : 'Reanudar cambio automático')
        : (isEnglish ? 'Pause automatic rotation' : 'Pausar cambio automático'));
      track('review_carousel_toggle', { state: manuallyPaused ? 'paused' : 'playing' });
      start();
    });

    shell.addEventListener('mouseenter', () => { hovered = true; stop(); });
    shell.addEventListener('mouseleave', () => { hovered = false; start(); });
    shell.addEventListener('focusin', () => { focused = true; stop(); });
    shell.addEventListener('focusout', (event) => {
      focused = shell.contains(event.relatedTarget);
      if (!focused) start();
    });
    stage.addEventListener('pointercancel', () => { pointerStart = null; });
    stage.addEventListener('pointerdown', (event) => {
      pointerStart = { x: event.clientX, y: event.clientY };
    }, { passive: true });
    stage.addEventListener('pointerup', (event) => {
      if (!pointerStart) return;
      const dx = event.clientX - pointerStart.x;
      const dy = event.clientY - pointerStart.y;
      pointerStart = null;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) {
        show(current + (dx < 0 ? 1 : -1), 'swipe');
        restart();
      }
    }, { passive: true });

    document.addEventListener('visibilitychange', () => document.hidden ? stop() : start());
    const motionChange = () => {
      pauseButton.disabled = prefersReducedMotion.matches;
      pauseButton.textContent = prefersReducedMotion.matches || manuallyPaused ? '▶' : 'Ⅱ';
      pauseButton.setAttribute('aria-label', prefersReducedMotion.matches
        ? (isEnglish ? 'Automatic rotation disabled: reduced motion' : 'Cambio automático desactivado: movimiento reducido')
        : (manuallyPaused ? (isEnglish ? 'Resume automatic rotation' : 'Reanudar cambio automático') : (isEnglish ? 'Pause automatic rotation' : 'Pausar cambio automático')));
      start();
    };
    prefersReducedMotion.addEventListener?.('change', motionChange);

    const sourceRow = document.querySelector('.review-source-row');
    if (sourceRow) {
      sourceRow.classList.add('review-source-row--internal');
      sourceRow.innerHTML = isEnglish ? `
        <p>Verified public reviews. We show them here so you can read the experiences without leaving IBERFIT.</p>
        <span class="review-verified-badge">Verified reviews</span>
      ` : `
        <p>Reseñas públicas verificadas. Las mostramos aquí para que puedas leer las experiencias sin salir de IBERFIT.</p>
        <span class="review-verified-badge">Reseñas verificadas</span>
      `;
    }

    show(0, 'init');
    motionChange();
  };

  const initLocalPages = () => {
    if (!['local','local_en'].includes(document.body.dataset.page || '')) return;
    const heroText = document.querySelector('.hero .hero-text');
    if (!heroText || heroText.querySelector('.local-place-badge')) return;

    const eyebrow = heroText.querySelector('.eyebrow');
    const raw = eyebrow?.textContent?.trim() || '';
    const match = isEnglish ? raw.match(/IBERFIT\s+in\s+(.+)/i) : raw.match(/IBERFIT\s+en\s+(.+)/i);
    const fallbackPattern = isEnglish ? /\bin\s+([^,.]+?)(?:\s+without|\s+with|\.|$)/i : /(?:en|de)\s+([^,.]+?)(?:\s+sin|\s+con|$)/i;
    const place = match?.[1]?.trim() || document.querySelector('h1')?.textContent?.match(fallbackPattern)?.[1]?.trim() || (isEnglish ? 'your area' : 'tu comuna');

    const badge = document.createElement('div');
    badge.className = 'local-place-badge';
    badge.innerHTML = `
      <span class="local-place-pin" aria-hidden="true">⌖</span>
      <span class="local-place-copy"><small>${isEnglish ? 'Local coverage' : 'Cobertura local'}</small><strong>${place}</strong></span>
    `;
    eyebrow?.insertAdjacentElement('afterend', badge);

    const meta = heroText.querySelector('.hero-meta');
    if (meta && !heroText.querySelector('.local-service-strip')) {
      const strip = document.createElement('div');
      strip.className = 'local-service-strip';
      strip.setAttribute('aria-label', isEnglish ? `Training options in ${place}` : `Opciones de entrenamiento en ${place}`);
      strip.innerHTML = isEnglish ? `
        <div class="local-service-chip"><b>01</b><span><strong>Home training</strong><br>We coordinate area and schedule with you.</span></div>
        <div class="local-service-chip"><b>02</b><span><strong>Condominium gym</strong><br>When the space supports quality training.</span></div>
        <div class="local-service-chip"><b>03</b><span><strong>Park or green space</strong><br>When the environment and conditions are suitable.</span></div>
        <div class="local-service-chip"><b>04</b><span><strong>Hybrid</strong><br>When it improves continuity.</span></div>
      ` : `
        <div class="local-service-chip"><b>01</b><span><strong>Domicilio</strong><br>Coordinamos sector y horario contigo.</span></div>
        <div class="local-service-chip"><b>02</b><span><strong>Gimnasio de edificio</strong><br>Si el espacio permite trabajar bien.</span></div>
        <div class="local-service-chip"><b>03</b><span><strong>Parque o zona verde</strong><br>Cuando el entorno y las condiciones permiten entrenar bien.</span></div>
        <div class="local-service-chip"><b>04</b><span><strong>Híbrido</strong><br>Cuando mejora la continuidad.</span></div>
      `;
      meta.insertAdjacentElement('afterend', strip);
    }

    document.body.classList.add('local-experience-v629');
  };

  document.addEventListener('DOMContentLoaded', () => {
    initReviews();
    initLocalPages();
  });
})();
