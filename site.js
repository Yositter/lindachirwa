(function() {
  'use strict';

  // ---------- Mobile nav ----------
  var toggle = document.getElementById('mobileToggle');
  var mobileNav = document.getElementById('mobileNav');
  if (toggle && mobileNav) {
    toggle.addEventListener('click', function() {
      var open = mobileNav.classList.contains('open');
      mobileNav.classList.toggle('open');
      toggle.classList.toggle('active');
      toggle.setAttribute('aria-expanded', !open);
      mobileNav.setAttribute('aria-hidden', open);
      document.body.style.overflow = open ? '' : 'hidden';
    });
    mobileNav.querySelectorAll('a').forEach(function(a) {
      a.addEventListener('click', function() {
        mobileNav.classList.remove('open');
        toggle.classList.remove('active');
        toggle.setAttribute('aria-expanded', 'false');
        mobileNav.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
      });
    });
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && mobileNav.classList.contains('open')) {
        mobileNav.classList.remove('open');
        toggle.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  // ---------- Reveal on scroll ----------
  var revealEls = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  if ('IntersectionObserver' in window) {
    var ro = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          ro.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function(el) { ro.observe(el); });
  } else {
    revealEls.forEach(function(el) { el.classList.add('visible'); });
  }

  // ---------- Counter animation (stat bands) ----------
  var counters = document.querySelectorAll('.counter');
  var statsEl = document.getElementById('stats');
  var counterDone = false;
  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
  if (statsEl && counters.length && 'IntersectionObserver' in window) {
    new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting && !counterDone) {
          counterDone = true;
          counters.forEach(function(c) {
            var target = parseFloat(c.getAttribute('data-target')) || 0;
            var decimals = (String(c.getAttribute('data-target')).indexOf('.') !== -1) ? 1 : 0;
            var start = null;
            var duration = 1600;
            function step(ts) {
              if (!start) start = ts;
              var p = Math.min((ts - start) / duration, 1);
              var v = target * easeOutCubic(p);
              c.textContent = decimals ? v.toFixed(decimals) : Math.round(v);
              if (p < 1) requestAnimationFrame(step);
              else c.textContent = decimals ? target.toFixed(decimals) : target;
            }
            requestAnimationFrame(step);
          });
        }
      });
    }, { threshold: 0.3 }).observe(statsEl);
  } else if (counters.length) {
    counters.forEach(function(c) { c.textContent = c.getAttribute('data-target'); });
  }

  // ---------- Open an accordion when linked to by #id ----------
  function openHashTarget() {
    var el = location.hash ? document.getElementById(location.hash.slice(1)) : null;
    if (el && el.tagName === 'DETAILS') {
      el.open = true;
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
  window.addEventListener('hashchange', openHashTarget);
  openHashTarget();
})();
