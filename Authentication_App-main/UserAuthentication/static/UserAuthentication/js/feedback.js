/**
 * DRISHTI Feedback Widget
 * Floating pill → dropdown options → modal form.
 */
document.addEventListener('DOMContentLoaded', function () {
  const trigger   = document.getElementById('feedbackTrigger');
  const backdrop  = document.getElementById('feedbackBackdrop');
  const closeBtn  = document.getElementById('feedbackClose');
  const form      = document.getElementById('feedbackForm');
  const typeInput = document.getElementById('feedbackType');

  if (!trigger) return;

  // Toggle dropdown
  trigger.addEventListener('click', function (e) {
    if (!e.target.closest('.feedback-option')) {
      trigger.classList.toggle('open');
    }
  });

  // Close on outside click
  document.addEventListener('click', function (e) {
    if (!trigger.contains(e.target)) {
      trigger.classList.remove('open');
    }
  });

  // Open modal from option buttons
  document.querySelectorAll('.feedback-option').forEach(function (btn) {
    btn.addEventListener('click', function () {
      trigger.classList.remove('open');
      if (typeInput) typeInput.value = btn.dataset.type || 'general';
      const heading = document.getElementById('feedbackModalHeading');
      if (heading) heading.textContent = btn.dataset.label || 'Feedback';
      backdrop.classList.add('open');
    });
  });

  // Close modal
  function closeModal() { backdrop.classList.remove('open'); }
  if (closeBtn)  closeBtn.addEventListener('click', closeModal);
  backdrop.addEventListener('click', function (e) {
    if (e.target === backdrop) closeModal();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeModal();
  });

  // Submit via fetch
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const data = new FormData(form);
      fetch('/feedback/', { method: 'POST', body: data,
        headers: { 'X-CSRFToken': data.get('csrfmiddlewaretoken') }
      })
      .then(r => r.json())
      .then(function () {
        form.reset();
        closeModal();
        showToast('Feedback submitted. Thank you!', 'success');
      })
      .catch(function () {
        showToast('Could not send feedback. Please try again.', 'error');
      });
    });
  }

  function showToast(msg, type) {
    const t = document.createElement('div');
    t.className = `alert alert--${type === 'success' ? 'success' : 'danger'}`;
    t.style.cssText = 'position:fixed;bottom:5rem;right:1.5rem;z-index:9999;max-width:300px;font-size:.85rem;';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 3500);
  }
});
