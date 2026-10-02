/* Linda Chirwa Attorneys: whistleblower report form. */
(function() {
  'use strict';

  var form = document.getElementById('wbForm');
  var msgEl = document.getElementById('wbFormMessage');
  var submitBtn = document.getElementById('wbSubmitBtn');
  if (!form) return;

  form.addEventListener('submit', function(e) {
    e.preventDefault();

    msgEl.className = 'form-message';
    msgEl.style.display = 'none';
    msgEl.textContent = '';

    var org = form.querySelector('#wb_org');
    var cat = form.querySelector('#wb_category');
    var desc = form.querySelector('#wb_description');
    var consent = form.querySelector('#wb_consent');
    var errors = [];

    [org, cat, desc].forEach(function(f) { f.classList.remove('error'); });

    if (!org.value.trim()) { errors.push('Please name the organisation involved.'); org.classList.add('error'); }
    if (!cat.value) { errors.push('Please select the type of conduct.'); cat.classList.add('error'); }
    if (!desc.value.trim()) { errors.push('Please describe what happened.'); desc.classList.add('error'); }
    if (consent && !consent.checked) { errors.push('Please confirm your declaration.'); }

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
        msgEl.textContent = 'Network error. If your report is urgent, please email whistleblower@lindachirwaattorneys.co.za directly.';
        msgEl.style.display = 'block';
        msgEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
  });
})();
