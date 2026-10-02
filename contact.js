/* Linda Chirwa Attorneys: contact page enquiry form. */
(function() {
  'use strict';

  // ---------- Form ----------
  var form = document.getElementById('contactForm');
  var msgEl = document.getElementById('formMessage');
  var submitBtn = document.getElementById('submitBtn');
  var progressBar = document.getElementById('formProgress');

  if (form) {
    // Progress bar, tracks how many required fields are filled
    var requiredFields = form.querySelectorAll('[required]');
    function updateProgress() {
      var filled = 0;
      requiredFields.forEach(function(f) {
        if (f.type === 'checkbox') {
          if (f.checked) filled++;
        } else if (f.value.trim() !== '') {
          filled++;
        }
      });
      var pct = requiredFields.length ? (filled / requiredFields.length) * 100 : 0;
      progressBar.style.width = pct + '%';
    }
    form.addEventListener('input', updateProgress);
    form.addEventListener('change', updateProgress);
    updateProgress();

    form.addEventListener('submit', function(e) {
      e.preventDefault();

      msgEl.className = 'form-message';
      msgEl.style.display = 'none';
      msgEl.textContent = '';

      var name = form.querySelector('#name');
      var email = form.querySelector('#email');
      var phone = form.querySelector('#phone');
      var message = form.querySelector('#message');
      var service = form.querySelector('#service');
      var consent = form.querySelector('#consent');
      var errors = [];

      [name, email, phone, message, service].forEach(function(f) { f.classList.remove('error'); });

      if (!name.value.trim()) { errors.push('Full name is required.'); name.classList.add('error'); }
      if (!email.value.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
        errors.push('A valid email is required.'); email.classList.add('error');
      }
      if (!phone.value.trim()) { errors.push('Phone number is required.'); phone.classList.add('error'); }
      if (!service.value) { errors.push('Please select an area of law.'); service.classList.add('error'); }
      if (!message.value.trim()) { errors.push('Please describe your situation.'); message.classList.add('error'); }
      if (consent && !consent.checked) { errors.push('Please confirm your consent to be contacted.'); }

      if (errors.length > 0) {
        msgEl.className = 'form-message error';
        msgEl.textContent = errors.join(' ');
        msgEl.style.display = 'block';
        msgEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }

      submitBtn.classList.add('loading');
      submitBtn.disabled = true;

      fetch(form.action, { method: 'POST', body: new FormData(form) })
        .then(function(res) {
          return res.json().then(function(data) { return { ok: res.ok, data: data }; });
        })
        .then(function(result) {
          submitBtn.classList.remove('loading');
          submitBtn.disabled = false;

          if (result.data.success) {
            msgEl.className = 'form-message success';
            msgEl.textContent = result.data.message;
            msgEl.style.display = 'block';
            form.reset();
            updateProgress();
          } else {
            msgEl.className = 'form-message error';
            msgEl.textContent = result.data.message || 'Something went wrong. Please try again.';
            msgEl.style.display = 'block';
          }
          msgEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        })
        .catch(function() {
          submitBtn.classList.remove('loading');
          submitBtn.disabled = false;
          msgEl.className = 'form-message error';
          msgEl.textContent = 'Network error. Please check your connection, or contact us directly at admin@lindachirwaattorneys.co.za.';
          msgEl.style.display = 'block';
          msgEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    });
  }
})();
