/**
 * DRISHTI Theme System
 * Persists user preference in localStorage.
 * Applies `data-theme="dark"` on <html> for CSS variable switching.
 */
(function () {
  const KEY = 'drishti_theme';

  function getPreferred() {
    const stored = localStorage.getItem(KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(KEY, theme);
    // Update all toggle buttons
    document.querySelectorAll('.theme-toggle').forEach(btn => {
      const icon = btn.querySelector('.theme-toggle__icon');
      const label = btn.querySelector('.theme-toggle__label');
      if (icon)  icon.textContent = theme === 'dark' ? '☀' : '🌙';
      if (label) label.textContent = theme === 'dark' ? 'Light' : 'Dark';
      btn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    });
  }

  function toggle() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    apply(current === 'dark' ? 'light' : 'dark');
  }

  // Apply immediately (before paint) to prevent flash
  apply(getPreferred());

  document.addEventListener('DOMContentLoaded', function () {
    apply(getPreferred());
    document.querySelectorAll('.theme-toggle').forEach(btn => {
      btn.addEventListener('click', toggle);
    });
  });
})();
