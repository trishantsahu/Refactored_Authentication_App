/**
 * DRISHTI OTP Countdown
 * Reads data-generated-at / data-expiry-minutes from #otp-time,
 * updates #countdownDisplay, and marks #otpCountdown as expired.
 */
document.addEventListener('DOMContentLoaded', function () {
  var metaEl   = document.getElementById('otp-time');
  var display  = document.getElementById('countdownDisplay');
  var box      = document.getElementById('otpCountdown');
  if (!metaEl || !display) return;

  var generatedAt   = metaEl.getAttribute('data-generated-at');
  var expiryMinutes = parseInt(metaEl.getAttribute('data-expiry-minutes'), 10);
  if (!generatedAt || !expiryMinutes) return;

  var expiresAt = new Date(generatedAt).getTime() + expiryMinutes * 60 * 1000;

  function tick() {
    var remaining = expiresAt - Date.now();
    if (remaining <= 0) {
      display.textContent = 'EXPIRED';
      if (box) box.classList.add('otp-countdown--expired');
      /* Disable submit so the user knows they must restart */
      var btn = document.querySelector('button[type="submit"]:not([name="wizard_goto_step"])');
      if (btn) { btn.disabled = true; btn.textContent = 'OTP Expired — restart registration'; }
      return;
    }
    var m = Math.floor(remaining / 60000);
    var s = Math.floor((remaining % 60000) / 1000);
    display.textContent = m + ':' + String(s).padStart(2, '0');
    setTimeout(tick, 1000);
  }
  tick();
});
