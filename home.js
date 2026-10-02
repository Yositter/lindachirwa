/* Linda Chirwa Attorneys: home page behaviour (loader, header on scroll, section dots, service tabs). */
(function() {
  'use strict';

  // ---------- Loader ----------
  // A short brand moment, never a wait for every image: the page is already parsed here.
  var loader = document.getElementById('loader');
  function hideLoader() { if (loader) loader.classList.add('hidden'); }
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) hideLoader();
  else setTimeout(hideLoader, 400);

  // ---------- Navbar scroll ----------
  var navbar = document.querySelector('.navbar');
  function handleNavScroll() {
    if (window.pageYOffset > 60) navbar.classList.add('scrolled');
    else navbar.classList.remove('scrolled');
  }

  // ---------- Dot nav ----------
  var dotNav = document.getElementById('dotNav');
  var dots = dotNav ? dotNav.querySelectorAll('.dot-nav-dot') : [];
  var sids = [];
  dots.forEach(function(d) { sids.push(d.getAttribute('data-section')); });
  function updateDots() {
    var ai = 0;
    sids.forEach(function(id, i) {
      var s = document.getElementById(id);
      if (s && s.getBoundingClientRect().top < window.innerHeight * 0.5) ai = i;
    });
    dots.forEach(function(d, i) { d.classList.toggle('active', i === ai); });
  }
  dots.forEach(function(d) {
    d.addEventListener('click', function() {
      var s = document.getElementById(d.getAttribute('data-section'));
      if (s) s.scrollIntoView({ behavior: 'smooth' });
    });
  });

  // ---------- Service tabs ----------
  var tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      tabBtns.forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      document.querySelectorAll('.tab-panel').forEach(function(p) { p.classList.remove('active'); });
      var panel = document.getElementById('tab-' + btn.getAttribute('data-tab'));
      if (panel) {
        panel.classList.add('active');
        // Re-trigger reveal animations for newly shown cards
        panel.querySelectorAll('.reveal').forEach(function(el) {
          el.classList.remove('visible');
          setTimeout(function() { el.classList.add('visible'); }, 40);
        });
      }
    });
  });

  // ---------- Scroll listener (throttled) ----------
  var ticking = false;
  window.addEventListener('scroll', function() {
    if (!ticking) {
      requestAnimationFrame(function() {
        handleNavScroll();
        updateDots();
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  handleNavScroll();
  updateDots();
})();
