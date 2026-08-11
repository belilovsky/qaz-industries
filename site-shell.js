(function () {
  'use strict';

  const menuButton = document.querySelector('.menu-button');
  const mobileNav = document.querySelector('#mobile-nav');
  const themeToggle = document.querySelector('[data-theme-toggle]');
  const themes = ['institutional', 'golden-paper'];
  const themeLabels = { institutional: 'Институц.', 'golden-paper': 'Бумага' };

  function setTheme(theme, persist = true) {
    const nextTheme = themes.includes(theme) ? theme : 'institutional';
    document.documentElement.dataset.avTheme = nextTheme;
    document.querySelectorAll('[data-theme-label]').forEach((label) => {
      label.textContent = themeLabels[nextTheme];
    });
    themeToggle?.setAttribute('aria-label', `Сменить тему. Сейчас: ${themeLabels[nextTheme]}`);
    if (persist) {
      try { localStorage.setItem('qaz-industries-theme', nextTheme); } catch (_) {}
    }
  }

  function closeMobileNav({ restoreFocus = false } = {}) {
    if (!menuButton || !mobileNav) return;
    menuButton.setAttribute('aria-expanded', 'false');
    mobileNav.hidden = true;
    if (restoreFocus) menuButton.focus();
  }

  setTheme(document.documentElement.dataset.avTheme, false);
  themeToggle?.addEventListener('click', () => {
    const current = document.documentElement.dataset.avTheme;
    setTheme(themes[(themes.indexOf(current) + 1) % themes.length]);
  });

  menuButton?.addEventListener('click', () => {
    const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!isOpen));
    mobileNav.hidden = isOpen;
    if (!isOpen) mobileNav.querySelector('a')?.focus();
  });

  mobileNav?.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMobileNav();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
      closeMobileNav({ restoreFocus: true });
    }
  });

  const desktopQuery = window.matchMedia?.('(min-width: 841px)');
  desktopQuery?.addEventListener?.('change', (event) => {
    if (event.matches) closeMobileNav();
  });

  async function refreshAvdsCoverageBadge() {
    const badges = document.querySelectorAll('[data-avds-coverage-badge]');
    if (!badges.length) return;
    try {
      const response = await fetch('data/avds-coverage.v1.json', {
        cache: 'no-store',
      });
      if (!response.ok) throw new Error(`AVDS coverage HTTP ${response.status}`);
      const receipt = await response.json();
      const version = String(receipt?.avds?.version || '');
      const percent = Number(receipt?.coverage_percent);
      if (!/^4\.\d+\.\d+$/.test(version) || !Number.isInteger(percent) || percent < 0 || percent > 100) {
        throw new Error('Invalid AVDS coverage contract');
      }
      const label = `AVDS ${version}-${percent}`;
      badges.forEach((badge) => {
        badge.textContent = label;
        badge.setAttribute('aria-label', `Покрытие AVDS ${version}: ${percent} процентов`);
        badge.dataset.avdsCoverageState = 'fresh';
      });
    } catch (_) {
      badges.forEach((badge) => { badge.dataset.avdsCoverageState = 'fallback'; });
    }
  }

  refreshAvdsCoverageBadge();
}());
