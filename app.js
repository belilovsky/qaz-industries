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
  themeToggle?.setAttribute('aria-label', 'Сменить тему. Сейчас: ' + themeLabels[nextTheme]);
  if (persist) {
    try { localStorage.setItem('qaz-industries-theme', nextTheme); } catch (_) {}
  }
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
});

mobileNav?.addEventListener('click', (event) => {
  if (event.target.closest('a')) {
    menuButton.setAttribute('aria-expanded', 'false');
    mobileNav.hidden = true;
  }
});

const filterButtons = [...document.querySelectorAll('[data-filter]')];
const industryCards = [...document.querySelectorAll('[data-kind]')];

filterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const filter = button.dataset.filter;
    filterButtons.forEach((item) => {
      const active = item === button;
      item.classList.toggle('is-active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    industryCards.forEach((card) => {
      card.hidden = filter !== 'all' && card.dataset.kind !== filter;
    });
  });
});
