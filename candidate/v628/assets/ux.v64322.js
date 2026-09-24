(() => {
  'use strict';
  const english = (document.documentElement.lang || '').toLowerCase().startsWith('en');
  const label = english ? 'Swipe to see more' : 'Desliza para ver más';
  const selectors = [
    '.evidence-process-media--v6435',
    '.system-rail',
    '.method-cycle',
    '.week-flow',
    '.continuity-rail',
    '.brand-journey--editorial',
    '.app-story-stage',
    '.review-pair'
  ];
  document.addEventListener('DOMContentLoaded', () => {
    selectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(rail => {
        if (rail.nextElementSibling?.classList.contains('mobile-swipe-hint')) return;
        const hint = document.createElement('p');
        hint.className = 'mobile-swipe-hint';
        hint.textContent = label;
        hint.setAttribute('aria-hidden', 'true');
        rail.insertAdjacentElement('afterend', hint);
      });
    });
  });
})();
