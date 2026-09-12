/* IBERFIT WEB V6.21 · Consent-first, privacy-minimised measurement */
(() => {
  'use strict';
  const cfg = window.IBERFIT_ANALYTICS || {};
  const storageKey = 'iberfit_consent_v2';
  const lang = document.documentElement.lang === 'en' ? 'en' : 'es';
  const labels = lang === 'en' ? {
    title:'Your privacy, under your control',
    text:'Optional measurement helps us understand which pages are useful and which actions lead to contact. We never send message content or personal details.',
    all:'Accept all', audience:'Audience only', necessary:'Necessary only', preferences:'Preferences', save:'Save preferences',
    analytics:'Audience measurement', marketing:'Advertising measurement', close:'Close', optional:'Optional'
  } : {
    title:'Tu privacidad, bajo tu control',
    text:'La medición opcional nos ayuda a saber qué páginas resultan útiles y qué acciones terminan en contacto. Nunca enviamos el contenido de mensajes ni datos personales.',
    all:'Aceptar todo', audience:'Solo audiencia', necessary:'Solo necesarias', preferences:'Preferencias', save:'Guardar preferencias',
    analytics:'Medición de audiencia', marketing:'Medición publicitaria', close:'Cerrar', optional:'Opcional'
  };

  const parse = value => { try { return JSON.parse(value); } catch (_) { return null; } };
  const safeStorage = {
    get(key){ try { return window.localStorage.getItem(key); } catch (_) { return null; } },
    set(key,value){ try { window.localStorage.setItem(key,value); return true; } catch (_) { return false; } }
  };
  let consent = parse(safeStorage.get(storageKey));
  if (!consent || consent.version !== cfg.consentVersion) consent = null;
  let gaLoaded = false;
  let metaLoaded = false;
  let gaPageViewSent = false;
  let metaPageViewSent = false;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function(){ window.dataLayer.push(arguments); };
  window.gtag('consent', 'default', {
    analytics_storage:'denied', ad_storage:'denied', ad_user_data:'denied', ad_personalization:'denied', wait_for_update:500
  });

  const clean = value => typeof value === 'number' ? value : String(value ?? '').slice(0, 100);
  const context = () => ({
    page_path:location.pathname,
    page_language:lang,
    page_group:document.body?.dataset.page || 'general',
    viewport_group:innerWidth <= 720 ? 'mobile' : innerWidth <= 980 ? 'tablet' : 'desktop'
  });
  const canAnalytics = () => Boolean(consent?.analytics);
  const canMarketing = () => Boolean(consent?.marketing);

  const loadGA = () => {
    const id = String(cfg.ga4MeasurementId || '').trim();
    if (!id || gaLoaded) return;
    gaLoaded = true;
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`;
    document.head.appendChild(script);
    window.gtag('js', new Date());
    window.gtag('config', id, {
      send_page_view:false, anonymize_ip:true, allow_google_signals:false, allow_ad_personalization_signals:false
    });
  };
  const loadMeta = () => {
    const id = String(cfg.metaPixelId || '').trim();
    if (!id || metaLoaded) return;
    metaLoaded = true;
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    window.fbq('consent', 'grant');
    window.fbq('init', id);
  };
  const applyConsent = () => {
    window.gtag('consent', 'update', {
      analytics_storage:canAnalytics() ? 'granted' : 'denied',
      ad_storage:canMarketing() ? 'granted' : 'denied',
      ad_user_data:canMarketing() ? 'granted' : 'denied',
      ad_personalization:canMarketing() ? 'granted' : 'denied'
    });
    if (canAnalytics()) loadGA();
    if (canMarketing()) loadMeta();
    if (window.fbq) window.fbq('consent', canMarketing() ? 'grant' : 'revoke');
  };

  window.iberfitTrack = (eventName, params = {}) => {
    const payload = { ...context() };
    Object.entries(params).forEach(([key,value]) => {
      if (value !== undefined && value !== null) payload[key] = clean(value);
    });
    if (cfg.debug) console.info('[IBERFIT analytics]', eventName, payload);
    if (canAnalytics()) window.gtag('event', eventName, payload);
    if (canMarketing() && window.fbq && ['whatsapp_click','contact_email_click','format_guide_whatsapp_open'].includes(eventName)) {
      window.fbq('track', 'Lead', { content_name:eventName, page_group:payload.page_group });
    }
  };

  const referrerGroup = () => {
    if (!document.referrer) return 'direct';
    try { return new URL(document.referrer).hostname.slice(0, 100); } catch (_) { return 'unknown'; }
  };
  const sendPageView = () => {
    const payload = {
      ...context(),
      page_title:document.title,
      page_location:location.href,
      referrer_group:referrerGroup()
    };
    if (canAnalytics() && !gaPageViewSent) {
      gaPageViewSent = true;
      window.gtag('event', 'page_view', payload);
    }
    if (canMarketing() && window.fbq && !metaPageViewSent) {
      metaPageViewSent = true;
      window.fbq('track', 'PageView');
    }
  };
  const persist = (analytics, marketing) => {
    consent = {
      version:cfg.consentVersion,
      analytics:Boolean(analytics),
      marketing:Boolean(marketing),
      updatedAt:new Date().toISOString()
    };
    safeStorage.set(storageKey, JSON.stringify(consent));
    applyConsent();
    document.querySelector('.consent-banner')?.remove();
    document.querySelector('.consent-modal')?.remove();
    sendPageView();
    window.iberfitTrack('consent_updated', {
      analytics:consent.analytics ? 'granted' : 'denied',
      marketing:consent.marketing ? 'granted' : 'denied'
    });
  };

  const openSettings = () => {
    document.querySelector('.consent-modal')?.remove();
    const modal = document.createElement('div');
    modal.className = 'consent-modal';
    modal.setAttribute('role','dialog');
    modal.setAttribute('aria-modal','true');
    modal.setAttribute('aria-labelledby','consent-title');
    modal.innerHTML = `<div class="consent-dialog"><button class="consent-close" type="button" aria-label="${labels.close}">×</button><p class="kicker">IBERFIT</p><h2 id="consent-title">${labels.preferences}</h2><label class="consent-option"><span><strong>${labels.analytics}</strong><small>GA4 · ${labels.optional}</small></span><input type="checkbox" data-consent-analytics ${consent?.analytics ? 'checked' : ''}></label><label class="consent-option"><span><strong>${labels.marketing}</strong><small>Meta Pixel · ${labels.optional}</small></span><input type="checkbox" data-consent-marketing ${consent?.marketing ? 'checked' : ''}></label><button class="btn btn-primary" type="button" data-consent-save>${labels.save}</button></div>`;
    document.body.appendChild(modal);
    const close = () => modal.remove();
    modal.querySelector('.consent-close').addEventListener('click', close);
    modal.addEventListener('click', event => { if (event.target === modal) close(); });
    modal.addEventListener('keydown', event => { if (event.key === 'Escape') close(); });
    modal.querySelector('[data-consent-save]').addEventListener('click', () => persist(
      modal.querySelector('[data-consent-analytics]').checked,
      modal.querySelector('[data-consent-marketing]').checked
    ));
    modal.querySelector('.consent-close').focus();
  };
  const showBanner = () => {
    const banner = document.createElement('aside');
    banner.className = 'consent-banner';
    banner.setAttribute('aria-label', labels.title);
    banner.innerHTML = `<div><strong>${labels.title}</strong><p>${labels.text}</p></div><div class="consent-actions"><button class="btn btn-primary" type="button" data-consent-all>${labels.all}</button><button class="btn btn-secondary" type="button" data-consent-audience>${labels.audience}</button><button class="btn btn-ghost" type="button" data-consent-necessary>${labels.necessary}</button><button class="consent-link" type="button" data-consent-settings>${labels.preferences}</button></div>`;
    document.body.appendChild(banner);
    banner.querySelector('[data-consent-all]').addEventListener('click', () => persist(true,true));
    banner.querySelector('[data-consent-audience]').addEventListener('click', () => persist(true,false));
    banner.querySelector('[data-consent-necessary]').addEventListener('click', () => persist(false,false));
    banner.querySelector('[data-consent-settings]').addEventListener('click', openSettings);
  };

  applyConsent();
  document.addEventListener('click', event => {
    if (event.target.closest('[data-open-consent]')) { event.preventDefault(); openSettings(); }
  });

  document.addEventListener('DOMContentLoaded', () => {
    if (!consent) showBanner();
    sendPageView();
    const marks = [25,50,75,90];
    const seen = new Set();
    addEventListener('scroll', () => {
      const max = document.documentElement.scrollHeight - innerHeight;
      if (max <= 0) return;
      const percent = Math.round(scrollY / max * 100);
      marks.forEach(mark => {
        if (percent >= mark && !seen.has(mark)) {
          seen.add(mark);
          window.iberfitTrack('scroll_depth', { percent:mark });
        }
      });
    }, { passive:true });
    setTimeout(() => {
      if (document.visibilityState === 'visible') window.iberfitTrack('engaged_30_seconds');
    }, 30000);
    document.querySelectorAll('.lang-switch a').forEach(link => link.addEventListener('click', () => {
      window.iberfitTrack('language_switch', { target_language:link.textContent.trim().toLowerCase() });
    }));
    document.querySelectorAll('a[href^="mailto:"]').forEach(link => link.addEventListener('click', () => {
      window.iberfitTrack('contact_email_click');
    }));
  });
})();
