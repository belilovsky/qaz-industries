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
}());
