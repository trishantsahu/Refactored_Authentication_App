/**
 * DRISHTI Clock — IST (Indian Standard Time, UTC+5:30)
 * Updates every second. Targets all elements with class `drishti-clock`.
 */
(function () {
  function getIST() {
    const now = new Date();
    const utc = now.getTime() + now.getTimezoneOffset() * 60000;
    const ist = new Date(utc + 5.5 * 3600000);
    const hh = String(ist.getHours()).padStart(2, '0');
    const mm = String(ist.getMinutes()).padStart(2, '0');
    const ss = String(ist.getSeconds()).padStart(2, '0');
    return `${hh}:${mm}:${ss} IST`;
  }

  function tick() {
    const time = getIST();
    document.querySelectorAll('.drishti-clock').forEach(el => {
      el.textContent = time;
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    tick();
    setInterval(tick, 1000);
  });
})();
