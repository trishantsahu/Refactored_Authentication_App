document.addEventListener('DOMContentLoaded', function () {
  const otpTimeEl = document.getElementById('otp-time');
  if (!otpTimeEl) return;

  const generatedAt = otpTimeEl.getAttribute('data-generated-at');
  const expiryMinutes = parseInt(otpTimeEl.getAttribute('data-expiry-minutes'), 10);
  if (!generatedAt || !expiryMinutes) return;

  const otpExpiryTime = new Date(generatedAt).getTime() + expiryMinutes * 60 * 1000;

  function updateCountdown() {
    const now = new Date().getTime();
    const timeLeft = otpExpiryTime - now;
    const countdownEl = document.getElementById('countdown');

    if (timeLeft <= 0) {
      countdownEl.innerText = 'EXPIRED';
      const submitBtn = document.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;
    } else {
      const minutes = Math.floor(timeLeft / (1000 * 60));
      const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
      countdownEl.innerText = `${minutes}m ${seconds}s`;
      setTimeout(updateCountdown, 1000);
    }
  }

  updateCountdown();
});
