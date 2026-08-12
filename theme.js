(() => {
  const themes = ['institutional', 'editorial', 'data-analytics', 'map', 'dark', 'print', 'golden-paper'];
  let theme = 'institutional';
  try {
    const stored = localStorage.getItem('qaz-industries-theme');
    if (themes.includes(stored)) theme = stored;
  } catch (_) {}
  document.documentElement.dataset.avTheme = theme;
})();
