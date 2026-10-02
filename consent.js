/* Linda Chirwa Attorneys: cookie consent.
 *
 * What it does
 *  - Shows a banner on the first visit with equal "Reject non-essential" and "Accept all" buttons.
 *  - Stores the choice in one first-party cookie, "cookie_consent" (12 months).
 *  - Blocks third-party embeds (Google Maps, Facebook video) until the visitor allows them.
 *    Mark an embed up like this and this script does the rest:
 *      <iframe data-consent-src="https://..." data-consent-title="Google Maps"
 *              data-consent-open="https://link-to-open-it-directly" title="..."></iframe>
 *  - Loads Google Analytics only after consent, and only if a measurement ID is set below.
 *  - Any element with a data-cookie-settings attribute reopens the preferences panel.
 *
 * Setup: set GA_ID to your GA4 measurement ID (for example 'G-ABC123XYZ9') to switch analytics on.
 * Leave it empty and the analytics option is hidden and nothing is loaded.
 */
(function () {
  'use strict';

  var GA_ID = '';
  var COOKIE = 'cookie_consent';
  var VERSION = 1;
  var MAX_AGE_DAYS = 365;

  var state = read();
  var banner = null;
  var panel = null;
  var lastFocus = null;

  // ---------- Cookie storage ----------
  function read() {
    try {
      var m = document.cookie.match(new RegExp('(?:^|; )' + COOKIE + '=([^;]*)'));
      if (!m) return null;
      var v = JSON.parse(decodeURIComponent(m[1]));
      return v && v.v === VERSION ? v : null;
    } catch (e) { return null; }
  }
  function write(choice) {
    state = { v: VERSION, ts: new Date().toISOString().slice(0, 10), embeds: !!choice.embeds, analytics: !!(GA_ID && choice.analytics) };
    var secure = location.protocol === 'https:' ? '; Secure' : '';
    document.cookie = COOKIE + '=' + encodeURIComponent(JSON.stringify(state)) +
      '; Max-Age=' + (MAX_AGE_DAYS * 86400) + '; Path=/; SameSite=Lax' + secure;
  }
  function clearAnalyticsCookies() {
    var host = location.hostname.split('.');
    var domains = ['', location.hostname];
    for (var i = 1; i < host.length - 1; i++) domains.push('.' + host.slice(i).join('.'));
    document.cookie.split('; ').forEach(function (c) {
      var n = c.split('=')[0];
      if (n === '_ga' || n === '_gid' || n.indexOf('_ga_') === 0) {
        domains.forEach(function (d) {
          document.cookie = n + '=; Max-Age=0; Path=/' + (d ? '; Domain=' + d : '');
        });
      }
    });
  }

  // ---------- Third-party content ----------
  function embeds() { return document.querySelectorAll('iframe[data-consent-src]'); }

  function applyEmbeds() {
    embeds().forEach(function (f) {
      var host = f.parentNode;
      var ph = host.querySelector(':scope > .cc-placeholder');
      if (state && state.embeds) {
        if (ph) ph.remove();
        if (!f.getAttribute('src')) f.setAttribute('src', f.getAttribute('data-consent-src'));
        f.style.visibility = '';
      } else {
        f.removeAttribute('src');
        f.style.visibility = 'hidden';
        if (!ph) host.appendChild(buildPlaceholder(f));
      }
    });
  }

  function buildPlaceholder(f) {
    var host = f.parentNode;
    host.classList.add('cc-host');
    var title = f.getAttribute('data-consent-title') || 'Third-party content';
    var open = f.getAttribute('data-consent-open');
    var ph = el('div', 'cc-placeholder');
    ph.appendChild(el('strong', '', title));
    ph.appendChild(el('p', '', 'This content is provided by ' + title + ', which may set its own cookies. It loads only if you allow third-party content.'));
    var row = el('div', 'cc-placeholder-actions');
    var allow = el('button', 'cc-btn cc-btn-primary', 'Allow and load');
    allow.type = 'button';
    allow.addEventListener('click', function () {
      write({ embeds: true, analytics: state ? state.analytics : false });
      applyEmbeds();
      announce();
    });
    row.appendChild(allow);
    if (open) {
      var a = el('a', 'cc-link', 'Open it directly');
      a.href = open; a.target = '_blank'; a.rel = 'noopener';
      row.appendChild(a);
    }
    ph.appendChild(row);
    return ph;
  }

  // ---------- Analytics ----------
  function applyAnalytics() {
    if (!GA_ID) return;
    if (state && state.analytics) {
      window['ga-disable-' + GA_ID] = false;
      if (!document.getElementById('cc-ga')) {
        var s = document.createElement('script');
        s.id = 'cc-ga'; s.async = true;
        s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_ID);
        document.head.appendChild(s);
        window.dataLayer = window.dataLayer || [];
        window.gtag = function () { window.dataLayer.push(arguments); };
        window.gtag('js', new Date());
        window.gtag('config', GA_ID, { anonymize_ip: true });
      }
    } else {
      window['ga-disable-' + GA_ID] = true;
      clearAnalyticsCookies();
    }
  }

  function announce() {
    document.dispatchEvent(new CustomEvent('lc:consent', { detail: state }));
  }

  // ---------- Small DOM helpers ----------
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }
  function button(label, cls, fn) {
    var b = el('button', 'cc-btn ' + cls, label);
    b.type = 'button';
    b.addEventListener('click', fn);
    return b;
  }

  // ---------- Banner ----------
  function showBanner() {
    if (banner) return;
    banner = el('div', 'cc-banner');
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-modal', 'false');
    banner.setAttribute('aria-labelledby', 'cc-title');
    banner.setAttribute('aria-describedby', 'cc-desc');

    var h = el('h2', 'cc-title', 'Cookies on this site'); h.id = 'cc-title';
    var p = el('p', 'cc-text'); p.id = 'cc-desc';
    p.appendChild(document.createTextNode(
      'We use one cookie to remember this choice. ' +
      (GA_ID ? 'With your permission we also measure how the site is used. ' : '') +
      'Maps and videos on some pages come from Google and Facebook, which may set their own cookies, so we load them only if you allow it. '));
    var a = el('a', '', 'Cookie Policy'); a.href = 'cookies.html';
    p.appendChild(a); p.appendChild(document.createTextNode('.'));

    var actions = el('div', 'cc-actions');
    actions.appendChild(button('Reject non-essential', 'cc-btn-secondary', function () { save({ embeds: false, analytics: false }); }));
    actions.appendChild(button('Manage', 'cc-btn-ghost', function () { openPanel(); }));
    actions.appendChild(button('Accept all', 'cc-btn-primary', function () { save({ embeds: true, analytics: true }); }));

    banner.appendChild(h); banner.appendChild(p); banner.appendChild(actions);
    document.body.appendChild(banner);
    requestAnimationFrame(function () { banner.classList.add('cc-in'); });
  }
  function hideBanner() {
    if (!banner) return;
    banner.classList.remove('cc-in');
    var b = banner; banner = null;
    setTimeout(function () { b.remove(); }, 300);
  }

  // ---------- Preferences panel ----------
  function row(id, title, desc, checked, locked) {
    var r = el('div', 'cc-row');
    var text = el('div', 'cc-row-text');
    var l = el('label', 'cc-row-title', title); l.setAttribute('for', id);
    text.appendChild(l); text.appendChild(el('p', '', desc));
    var sw = el('input', 'cc-switch'); sw.type = 'checkbox'; sw.id = id; sw.checked = checked; sw.disabled = !!locked;
    r.appendChild(text); r.appendChild(sw);
    return r;
  }

  function openPanel() {
    if (panel) return;
    lastFocus = document.activeElement;
    var overlay = el('div', 'cc-overlay');
    var dlg = el('div', 'cc-panel');
    dlg.setAttribute('role', 'dialog'); dlg.setAttribute('aria-modal', 'true'); dlg.setAttribute('aria-labelledby', 'cc-ptitle');

    var h = el('h2', 'cc-title', 'Cookie preferences'); h.id = 'cc-ptitle';
    dlg.appendChild(h);
    dlg.appendChild(el('p', 'cc-text', 'Choose which cookies you allow. You can change this at any time from the Cookie Settings link in the footer.'));

    dlg.appendChild(row('cc-necessary', 'Strictly necessary',
      'Remembers this choice (cookie_consent, 12 months). The site cannot work without it, so it is always on.', true, true));
    dlg.appendChild(row('cc-embeds', 'Third-party content',
      'Google Maps on the contact page and Facebook videos on the resources page. These providers may set their own cookies.',
      !!(state && state.embeds), false));
    if (GA_ID) {
      dlg.appendChild(row('cc-analytics', 'Analytics',
        'Google Analytics shows us which pages are used so we can improve the site. IP addresses are anonymised.',
        !!(state && state.analytics), false));
    }

    var actions = el('div', 'cc-actions');
    actions.appendChild(button('Reject non-essential', 'cc-btn-secondary', function () { save({ embeds: false, analytics: false }); }));
    actions.appendChild(button('Save choices', 'cc-btn-ghost', function () {
      save({ embeds: dlg.querySelector('#cc-embeds').checked, analytics: GA_ID ? dlg.querySelector('#cc-analytics').checked : false });
    }));
    actions.appendChild(button('Accept all', 'cc-btn-primary', function () { save({ embeds: true, analytics: true }); }));
    dlg.appendChild(actions);

    var close = el('button', 'cc-close'); close.type = 'button'; close.setAttribute('aria-label', 'Close preferences');
    close.innerHTML = '&times;';
    close.addEventListener('click', closePanel);
    dlg.appendChild(close);

    overlay.appendChild(dlg);
    overlay.addEventListener('mousedown', function (e) { if (e.target === overlay) closePanel(); });
    document.body.appendChild(overlay);
    document.body.classList.add('cc-lock');
    panel = overlay;
    requestAnimationFrame(function () { overlay.classList.add('cc-in'); });
    dlg.querySelector('#cc-embeds').focus();
  }

  function closePanel() {
    if (!panel) return;
    var p = panel; panel = null;
    p.classList.remove('cc-in');
    document.body.classList.remove('cc-lock');
    setTimeout(function () { p.remove(); }, 250);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener('keydown', function (e) {
    if (!panel) return;
    if (e.key === 'Escape') { closePanel(); return; }
    if (e.key === 'Tab') {
      var f = panel.querySelectorAll('button, input:not(:disabled), a[href]');
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  // ---------- Saving ----------
  function save(choice) {
    var hadEmbeds = !!(state && state.embeds);
    var hadAnalytics = !!(state && state.analytics);
    write(choice);
    hideBanner();
    closePanel();
    applyEmbeds();
    applyAnalytics();
    announce();
    // Content already loaded cannot be unloaded cleanly, so refresh when something was switched off.
    if ((hadEmbeds && !state.embeds) || (hadAnalytics && !state.analytics)) location.reload();
  }

  // ---------- Reopen from anywhere ----------
  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('[data-cookie-settings]') : null;
    if (t) { e.preventDefault(); openPanel(); }
  });

  // ---------- Init ----------
  function init() {
    applyEmbeds();
    applyAnalytics();
    if (!state) showBanner();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
