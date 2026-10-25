/* Negotiate the default-language entry; explicit localized links stay shareable. */
(() => {
  const root = document.documentElement;
  const locales = {'en-US':'', 'zh-CN':'zh-cn/', 'zh-HK':'zh-hk/'};
  const key = 'academic-homepage-language';
  const valid = value => Object.prototype.hasOwnProperty.call(locales, value);
  const requested = new URLSearchParams(location.search).get('lang');
  let preferred = null;
  try {
    const saved = localStorage.getItem(key);
    if (valid(saved)) preferred = saved;
  } catch (_) { /* Explicit language links still work without browser storage. */ }

  if (valid(requested)) {
    preferred = requested;
    try { localStorage.setItem(key, preferred); } catch (_) { /* Optional persistence. */ }
  }

  function deviceLocale() {
    const tag = (navigator.languages?.[0] || navigator.language || 'en').toLowerCase();
    if (!/^zh(?:-|$)/.test(tag)) return 'en-US';
    const parts = tag.split('-');
    if (parts.includes('hant')) return 'zh-HK';
    if (parts.includes('hans')) return 'zh-CN';
    return parts.some(part => ['hk', 'mo', 'tw'].includes(part)) ? 'zh-HK' : 'zh-CN';
  }

  // Only the default English entry is negotiated automatically. Explicit
  // Chinese URLs retain their language; manual switches always override it.
  const target = preferred || deviceLocale();
  if ((root.lang === 'en-US' || valid(requested)) && target !== root.lang) {
    const base = new URL(root.dataset.base, location.href);
    const destination = new URL(locales[target] + root.dataset.page, base);
    destination.search = location.search;
    destination.hash = location.hash;
    location.replace(destination.href);
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.languages a[hreflang]').forEach(anchor => {
      anchor.addEventListener('click', () => {
        const locale = anchor.getAttribute('hreflang');
        if (!valid(locale)) return;
        try { localStorage.setItem(key, locale); } catch (_) { /* URL preserves this choice. */ }
      });
    });
  });
})();
