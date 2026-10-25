/* Apply the saved theme before rendering; all pages share the preference. */
(() => {
  const root = document.documentElement;
  const key = 'academic-homepage-theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preferred = null;
  try {
    const saved = localStorage.getItem(key);
    if (saved === 'light' || saved === 'dark') preferred = saved;
  } catch (_) { /* Browsing modes that block storage can still toggle themes. */ }

  function apply(theme) {
    root.dataset.theme = theme;
    const button = document.querySelector('[data-theme-toggle]');
    if (!button) return;
    const dark = theme === 'dark';
    const label = dark ? button.dataset.lightLabel : button.dataset.darkLabel;
    button.setAttribute('aria-label', label);
    button.setAttribute('title', label);
    button.setAttribute('aria-pressed', String(dark));
    button.hidden = false;
  }

  function currentTheme() {
    return preferred || (system.matches ? 'dark' : 'light');
  }
  apply(currentTheme());
  document.addEventListener('DOMContentLoaded', () => {
    apply(currentTheme());
    document.querySelector('[data-theme-toggle]').addEventListener('click', () => {
      preferred = root.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(key, preferred); } catch (_) { /* Optional persistence. */ }
      apply(preferred);
    });
  });
  system.addEventListener('change', () => {
    if (!preferred) apply(currentTheme());
  });
  window.addEventListener('storage', (event) => {
    if (event.key !== key && event.key !== null) return;
    preferred = event.newValue === 'light' || event.newValue === 'dark' ? event.newValue : null;
    apply(currentTheme());
  });
})();
