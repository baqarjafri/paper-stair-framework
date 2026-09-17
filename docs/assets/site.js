/* STAIR paper page interactions. The page is complete without this file; it adds hover, click, the in-place player and the slide viewer. */
(function () {
  'use strict';
  var D = window.STAIR_DATA || null;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var DIMS = ['COV', 'ACC', 'EDU', 'TMP', 'INT'];
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var level = function (id) { return D ? D.levels.filter(function (l) { return l.id === id; })[0] : null; };

  /* 1. Nav: mobile menu and current section */
  var menuBtn = $('#menu-btn'), navList = $('#nav-list');
  if (menuBtn && navList) {
    menuBtn.addEventListener('click', function () { var open = navList.classList.toggle('open'); menuBtn.setAttribute('aria-expanded', String(open)); });
    navList.addEventListener('click', function (e) { if (e.target.tagName === 'A') { navList.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false'); } });
  }
  var navLinks = $$('#nav-list a[href^="#"]');
  var sections = navLinks.map(function (a) { return $(a.getAttribute('href')); }).filter(Boolean);
  if ('IntersectionObserver' in window && sections.length) {
    var navIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (!e.isIntersecting) return; navLinks.forEach(function (a) { a.classList.toggle('current', a.getAttribute('href') === '#' + e.target.id); }); });
    }, { rootMargin: '-40% 0px -55% 0px' });
    sections.forEach(function (s) { navIO.observe(s); });
  }

  /* 2. Video: swap the facade for the player, in place */
  var facade = $('#video-facade');
  var loadVideo = function () {
    if (!facade || facade.getAttribute('data-loaded')) return;
    facade.setAttribute('data-loaded', '1');
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/IOQ33vkTfSk?autoplay=1&rel=0';
    f.title = 'STAIR Framework talk, AITHE 2026 (YouTube player)';
    f.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture; fullscreen');
    f.setAttribute('allowfullscreen', '');
    facade.parentNode.replaceChild(f, facade);
    f.focus();
  };
  if (facade) facade.addEventListener('click', loadVideo);
  $$('a[data-play]').forEach(function (a) { a.addEventListener('click', function () { setTimeout(loadVideo, 350); }); });

  /* 3. Finding 1: tooltip and pinned dimension breakdown */
  var chart = $('#c1'), wrap = chart ? chart.parentNode : null, tip = $('#c1tip'), panel = $('#c1panel'), pinned = null;
  var dimsHtml = function (l) {
    return DIMS.map(function (k) { var v = l.dims[k]; return '<div class="dim"><b>' + k + '</b><span class="v' + (v === 0 ? ' z' : '') + '">' + v + '</span><span class="tr"><i style="width:' + v + '%"></i></span><small>' + esc(D.dims[k]) + '</small></div>'; }).join('');
  };
  var showPanel = function (l) {
    panel.innerHTML = '<h4>' + esc(l.id + ' ' + l.long) + ' <span>' + l.score + '% = mean of ' + DIMS.map(function (k) { return l.dims[k]; }).join(', ') + '</span></h4><div class="dims">' + dimsHtml(l) + '</div>';
    panel.hidden = false;
  };
  if (chart && tip && panel && D) {
    $$('.bar', chart).forEach(function (g) {
      var l = level(g.getAttribute('data-level'));
      var show = function () {
        var r = g.getBoundingClientRect(), c = wrap.getBoundingClientRect();
        tip.innerHTML = '<b>' + esc(l.id + ' ' + l.long + ' \u00b7 ' + l.score + '% \u00b7 ' + l.band) + '</b>' + esc(l.requirement) + '<dl>' + DIMS.map(function (k) { return '<div><dt>' + k + '</dt><dd>' + l.dims[k] + '</dd></div>'; }).join('') + '</dl>';
        tip.style.left = Math.min(Math.max(r.left - c.left + r.width / 2, 130), c.width - 130) + 'px';
        tip.style.top = Math.max(r.top - c.top + 24, 40) + 'px';
        tip.hidden = false;
        if (!pinned) showPanel(l);
      };
      var hide = function () { tip.hidden = true; };
      g.addEventListener('mouseenter', show); g.addEventListener('focus', show);
      g.addEventListener('mouseleave', hide); g.addEventListener('blur', hide);
      var toggle = function () {
        pinned = (pinned === l.id) ? null : l.id;
        $$('.bar', chart).forEach(function (b) { b.classList.toggle('dim', pinned !== null && b.getAttribute('data-level') !== pinned); });
        showPanel(l);
      };
      g.addEventListener('click', toggle);
      g.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } else if (e.key === 'Escape') hide(); });
    });
    showPanel(level('L3'));
  }

  /* 4. Finding 2: row select fills the detail panel */
  var rows = $('#rows'), detail = $('#detail');
  var showSub = function (sid) {
    var s = D.subs[sid]; if (!s) return; var l = level(s.level);
    $$('.row', rows).forEach(function (r) { r.setAttribute('aria-pressed', String(r.getAttribute('data-sub') === sid)); });
    detail.innerHTML = '<p class="k">' + esc(l.id + ' ' + l.long) + ' \u00b7 check ' + esc(sid.split('_')[0]) + '</p><h4>' + esc(s.name) + '</h4><span class="score s' + s.score + '">' + s.score + ' of 4 \u00b7 ' + esc(s.label) + ' \u00b7 counts as ' + s.pct + '</span><p class="k">What was checked</p><p>' + esc(s.definition) + '</p><p class="k">What was found in Moodle</p><p>' + esc(s.evidence) + '</p><p class="k">Rubric anchor</p><p>' + esc(D.rubric[String(s.score)]) + '</p><p class="k">Grounded in</p><p>' + esc(s.grounding.map(function (g) { return D.grounding[g]; }).join('; ')) + '</p>';
  };
  if (rows && detail && D) {
    rows.addEventListener('click', function (e) { var b = e.target.closest('.row'); if (b) showSub(b.getAttribute('data-sub')); });
  }

  /* 5. Finding 4: ladder steps */
  var ladder = $('#ladder');
  if (ladder) {
    ladder.addEventListener('click', function (e) {
      var btn = e.target.closest('.step'); if (!btn) return;
      var wrapEl = btn.parentNode, open = btn.getAttribute('aria-expanded') === 'true';
      $$('.step-wrap', ladder).forEach(function (w) { w.classList.remove('on'); var b = $('.step', w), d = $('.stepdetail', w); b.setAttribute('aria-expanded', 'false'); d.hidden = true; });
      if (!open) { wrapEl.classList.add('on'); btn.setAttribute('aria-expanded', 'true'); $('.stepdetail', wrapEl).hidden = false; }
    });
  }

  /* 6. Slide viewer */
  var viewer = $('#slides-viewer'), img = $('#slide-img'), count = $('#slide-count');
  if (viewer && img && count) {
    var N = 20;
    var TITLES = ['Title: STAIR, a five-level framework for evaluating LMS readiness for agentic AI teaching agents', 'Picture a second-year, call him Tom (illustrative)', 'A colleague that acts, on a platform built for content', 'Two questions, one ruler for any LMS', 'STAIR: five levels, a strict dependency chain', 'Derivation: three literatures converge on five levels', 'L1 and L2: perceive and remember', 'L3 to L5: reason, coordinate, reach', 'Research design: design science, structured source-code analysis', 'The scoring instrument: 28 sub-dimensions, 0 to 4 rubric, evidence tiers', 'We scored Moodle: 55 and 53', 'The 28-point cliff: readiness doesn\'t decay, it collapses', 'Two sealed rooms: AI and analytics share no code', 'The 28 dimensions scored, and why L3 is 25', 'Beyond Moodle: Canvas and Blackboard', 'One doorway: a small plugin, no core change', 'Three questions for your LMS', 'What this does and does not claim', 'Why it couldn\'t help him: nothing connected seeing to saying', 'We don\'t need smarter AI. We need LMSs ready to host it. Contact'];
    var cur = 1;
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };
    var src = function (n) { return 'assets/slides/slide_' + pad(n) + '.png'; };
    var go = function (n, updateHash) {
      cur = ((n - 1 + N) % N) + 1;
      img.src = src(cur); img.alt = 'Slide ' + cur + ' of ' + N + ': ' + TITLES[cur - 1];
      count.textContent = cur + ' / ' + N + ' \u00b7 ' + TITLES[cur - 1];
      $$('.thumb').forEach(function (t) { t.classList.toggle('on', Number(t.getAttribute('data-slide')) === cur); });
      [cur + 1, cur - 1].forEach(function (m) { if (m >= 1 && m <= N) { var pre = new Image(); pre.src = src(m); } });
      if (updateHash !== false && history.replaceState) history.replaceState(null, '', '#slide-' + cur);
    };
    var toggleFull = function () {
      if (document.fullscreenElement) document.exitFullscreen();
      else if (viewer.requestFullscreen) viewer.requestFullscreen();
      else viewer.classList.toggle('is-full');
    };
    $('#slide-prev').addEventListener('click', function () { go(cur - 1); });
    $('#slide-next').addEventListener('click', function () { go(cur + 1); });
    $('#slide-full').addEventListener('click', toggleFull);
    $$('.thumb').forEach(function (t) { t.addEventListener('click', function () { go(Number(t.getAttribute('data-slide'))); viewer.focus(); }); });
    viewer.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(cur + 1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); go(cur - 1); }
      else if (e.key === 'f' || e.key === 'F') toggleFull();
      else if (e.key === 'Escape' && viewer.classList.contains('is-full')) viewer.classList.remove('is-full');
    });
    var x0 = null;
    viewer.addEventListener('pointerdown', function (e) { x0 = e.clientX; });
    viewer.addEventListener('pointerup', function (e) { if (x0 === null) return; var dx = e.clientX - x0; x0 = null; if (Math.abs(dx) > 40) go(dx < 0 ? cur + 1 : cur - 1); });
    var m = /^#slide-(\d+)$/.exec(location.hash);
    if (m) { go(Number(m[1]), false); viewer.scrollIntoView(); } else go(1, false);
  }

  /* 7. BibTeX copy */
  var copyBtn = $('#copy-bib'), bib = $('#bibtex');
  if (copyBtn && bib) {
    copyBtn.addEventListener('click', function () {
      var text = bib.textContent.trim();
      var done = function (label) { copyBtn.textContent = label; setTimeout(function () { copyBtn.textContent = 'Copy BibTeX'; }, 2000); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { done('Copied'); }, function () { done('Select and copy manually'); });
      else { var range = document.createRange(); range.selectNodeContents(bib); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range); done('Selected, press Ctrl+C'); }
    });
  }
})();
