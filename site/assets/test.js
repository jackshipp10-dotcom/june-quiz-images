/* The Gardener Level Test. Plain JS, no libraries. Data comes from #gt-data. */
(function () {
  'use strict';
  var D = JSON.parse(document.getElementById('gt-data').textContent);
  var Q = D.questions, LV = D.levels, FORM = D.form;
  var root = document.getElementById('gt');
  var RM = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  var muted = store.get('gt-muted') === '1';
  var i = 0, answers = [], ac = null, revealTimer = [];

  /* ---------- sound ---------- */
  function audio() {
    if (!ac) { var C = window.AudioContext || window.webkitAudioContext; if (C) { try { ac = new C(); } catch (e) {} } }
    if (ac && ac.state === 'suspended') ac.resume();
    return ac;
  }
  function tone(f1, f2, start, dur, type, peak) {
    if (muted || !ac) return;
    var t = ac.currentTime + start, o = ac.createOscillator(), g = ac.createGain();
    o.type = type || 'sine';
    o.frequency.setValueAtTime(f1, t);
    if (f2) o.frequency.exponentialRampToValueAtTime(f2, t + dur);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(peak || 0.12, t + 0.012);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(ac.destination); o.start(t); o.stop(t + dur + 0.02);
  }
  var sfx = {
    tap: function () { tone(880, 0, 0, 0.05, 'sine', 0.05); },
    right: function () { tone(1046.5, 0, 0, 0.14, 'sine', 0.12); tone(1318.5, 0, 0.09, 0.26, 'sine', 0.12); },
    wrong: function () { tone(220, 196, 0, 0.28, 'triangle', 0.13); },
    next: function () { tone(660, 990, 0, 0.09, 'sine', 0.04); },
    results: function () { [523.25, 659.25, 783.99, 1046.5].forEach(function (f, n) { tone(f, 0, n * 0.11, 0.3, 'sine', 0.11); }); }
  };
  function buzz(p) { if (!muted && navigator.vibrate) { try { navigator.vibrate(p); } catch (e) {} } }

  /* ---------- helpers ---------- */
  function h(tag, attrs, html) {
    var el = document.createElement(tag);
    for (var k in attrs || {}) { if (k === 'class') el.className = attrs[k]; else el.setAttribute(k, attrs[k]); }
    if (html != null) el.innerHTML = html;
    return el;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function level(score) { for (var n = 0; n < LV.length; n++) if (score >= LV[n].min && score <= LV[n].max) return n; return 0; }
  function score() { return answers.reduce(function (a, b) { return a + b; }, 0); }
  var TICK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var CROSS = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/></svg>';
  var SPK_ON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/><path d="M16.5 8.5a5 5 0 010 7M19 6a8.5 8.5 0 010 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  var SPK_OFF = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/><path d="M17 9l5 6M22 9l-5 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';

  var first = true;
  function swap(el) {
    root.innerHTML = '';
    root.appendChild(el);
    el.classList.add('gt-in');
    if (first) { first = false; return; }
    window.scrollTo({ top: Math.max(0, root.getBoundingClientRect().top + window.pageYOffset - 70), behavior: RM ? 'auto' : 'smooth' });
  }

  function muteBtn() {
    var b = h('button', { type: 'button', class: 'gt-mute', 'aria-pressed': muted ? 'true' : 'false', 'aria-label': 'Sound' }, muted ? SPK_OFF : SPK_ON);
    b.addEventListener('click', function () {
      muted = !muted; store.set('gt-muted', muted ? '1' : '0');
      b.innerHTML = muted ? SPK_OFF : SPK_ON; b.setAttribute('aria-pressed', muted ? 'true' : 'false');
      if (!muted) { audio(); sfx.tap(); }
    });
    return b;
  }

  /* ---------- intro ---------- */
  function intro() {
    var best = parseInt(store.get('gt-best'), 10);
    var el = h('div', { class: 'gt-card gt-intro' });
    el.innerHTML =
      '<p class="gt-kicker">15 questions &middot; about 3 minutes</p>' +
      '<h2>How good a gardener are you, really?</h2>' +
      '<p>It starts easy and gets harder. Photos, myths and a couple of curveballs. Can you get all 15?</p>' +
      '<ol class="gt-ladder">' + LV.map(function (l, n) { return '<li><span class="gt-lv-ico" data-lv="' + n + '"></span><b>' + esc(l.name) + '</b><span>' + l.min + ' to ' + l.max + '</span></li>'; }).join('') + '</ol>' +
      (best >= 0 ? '<p class="gt-best">Your best so far: <b>' + best + '/15</b>. Beat it.</p>' : '');
    var go = h('button', { type: 'button', class: 'btn gt-go' }, 'Start the test');
    go.addEventListener('click', function () { audio(); sfx.next(); i = 0; answers = []; question(); });
    el.appendChild(go);
    el.querySelectorAll('.gt-lv-ico').forEach(function (s) { s.innerHTML = badgeSvg(+s.dataset.lv); });
    swap(el);
  }

  /* ---------- question ---------- */
  function dots() {
    var d = h('ol', { class: 'gt-dots', 'aria-hidden': 'true' });
    for (var n = 0; n < Q.length; n++) {
      var c = n < answers.length ? (answers[n] ? 'ok' : 'no') : (n === i ? 'now' : '');
      d.appendChild(h('li', { class: c }));
    }
    return d;
  }

  function optInner(o, fmt) {
    var media = o.svg ? '<span class="gt-media gt-svg">' + D.svgs[o.svg] + '</span>'
      : o.img ? '<span class="gt-media"><img src="/img/test/' + o.img + '" alt="" width="360" height="360" decoding="async"></span>' : '';
    var icon = fmt === 'mf' ? (o.label === 'Myth' ? '<span class="gt-ico" aria-hidden="true">?</span>' : '<span class="gt-ico" aria-hidden="true">!</span>')
      : fmt === 'ff' ? (o.label === 'Friend' ? '<span class="gt-ico" aria-hidden="true">&#9829;</span>' : '<span class="gt-ico" aria-hidden="true">&#9888;</span>') : '';
    return media + '<span class="gt-label">' + icon + esc(o.label) + '</span><span class="gt-mark" aria-hidden="true"></span>';
  }

  function question() {
    var q = Q[i];
    var layout = (q.fmt === 'tt') ? 'gt-two' : (q.fmt === 'grid' || q.fmt === 'odd') ? 'gt-grid' : (q.fmt === 'mc') ? 'gt-list' : 'gt-pair';
    var el = h('div', { class: 'gt-card gt-q gt-f-' + q.fmt });
    var top = h('div', { class: 'gt-top' });
    top.appendChild(h('p', { class: 'gt-count' }, 'Question ' + (i + 1) + ' of ' + Q.length));
    top.appendChild(muteBtn());
    el.appendChild(top);
    el.appendChild(dots());
    var tag = { tt: 'This or that', ff: 'Friend or foe', mf: 'Myth or fact', grid: 'Pick one', odd: 'Odd one out', mc: 'Pick one' }[q.fmt];
    el.appendChild(h('p', { class: 'gt-tag' }, tag));
    el.appendChild(h('h2', { class: 'gt-qtext', id: 'gt-qt' }, esc(q.q)));
    if (q.img) el.appendChild(h('figure', { class: 'gt-photo' }, '<img src="/img/test/' + q.img + '" alt="' + esc(q.alt || '') + '" width="720" height="720">'));
    var opts = h('div', { class: 'gt-opts ' + layout, role: 'group', 'aria-labelledby': 'gt-qt' });
    q.options.forEach(function (o, n) {
      var b = h('button', { type: 'button', class: 'gt-opt' + (o.svg || o.img ? ' gt-tile' : '') }, optInner(o, q.fmt));
      b.addEventListener('click', function () { choose(n, opts, el); });
      opts.appendChild(b);
    });
    el.appendChild(opts);
    el.appendChild(h('div', { class: 'gt-fb', 'aria-live': 'polite' }));
    swap(el);
    // warm the next question's images
    var nx = Q[i + 1];
    if (nx) [nx.img].concat(nx.options.map(function (o) { return o.img; })).forEach(function (s) { if (s) { var im = new Image(); im.src = '/img/test/' + s; } });
  }

  function choose(n, opts, el) {
    var q = Q[i], ok = n === q.answer, btns = opts.querySelectorAll('.gt-opt');
    if (opts.dataset.done) return;
    opts.dataset.done = '1';
    answers.push(ok ? 1 : 0);
    btns.forEach(function (b, k) { b.disabled = true; b.setAttribute('aria-disabled', 'true'); if (k !== n && k !== q.answer) b.classList.add('gt-dim'); });
    var picked = btns[n], right = btns[q.answer];
    picked.classList.add('gt-picked');
    if (ok) {
      sfx.right(); buzz(15);
      picked.classList.add('gt-ok'); picked.querySelector('.gt-mark').innerHTML = TICK;
    } else {
      sfx.wrong(); buzz([30, 40, 30]);
      picked.classList.add('gt-no'); picked.querySelector('.gt-mark').innerHTML = CROSS;
      setTimeout(function () { right.classList.add('gt-ok', 'gt-reveal'); right.querySelector('.gt-mark').innerHTML = TICK; }, RM ? 0 : 350);
    }
    // update this question's dot
    var d = el.querySelectorAll('.gt-dots li')[i]; if (d) { d.className = ok ? 'ok' : 'no'; }
    var fb = el.querySelector('.gt-fb');
    var praise = ['Spot on.', 'Nailed it.', 'Correct.', 'Lovely.', 'Right first time.'];
    var miss = ['Not quite.', 'So close.', 'Not this time.', 'Easily done.'];
    var head = ok ? praise[i % praise.length] : miss[i % miss.length];
    var last = i === Q.length - 1;
    setTimeout(function () {
      fb.innerHTML = '<div class="gt-fbin ' + (ok ? 'ok' : 'no') + '"><p class="gt-verdict">' + (ok ? TICK : CROSS) + '<b>' + head + '</b></p>' +
        '<p>' + esc(q.why) + '</p>' + (i % 3 === 1 || !ok ? '<p class="gt-more">June’s full tip for this one is in your breakdown at the end.</p>' : '') + '</div>';
      var nb = h('button', { type: 'button', class: 'btn gt-next' }, last ? 'See my level' : 'Next question');
      nb.addEventListener('click', function () { sfx.next(); i++; if (last) results(); else question(); });
      fb.appendChild(nb);
      nb.focus({ preventScroll: true });
      if (fb.getBoundingClientRect().bottom > window.innerHeight) fb.scrollIntoView({ behavior: RM ? 'auto' : 'smooth', block: 'end' });
    }, ok ? 220 : (RM ? 100 : 520));
  }

  /* ---------- badge art: a plant that grows with the level ---------- */
  function badgeSvg(lv) {
    var leaves = [
      '<path d="M50 70 V52" stroke="#3F6B3A" stroke-width="3.5" stroke-linecap="round"/><path d="M50 56 C40 46 32 50 30 54 C38 60 46 60 50 56Z M50 56 C60 46 68 50 70 54 C62 60 54 60 50 56Z" fill="#7FA36E" stroke="#1D2E21" stroke-width="1.6"/>',
      '<path d="M50 70 V40" stroke="#3F6B3A" stroke-width="3.5" stroke-linecap="round"/><path d="M50 58 C40 50 30 54 28 58 C36 64 46 63 50 58Z M50 50 C60 40 70 44 72 48 C64 55 55 54 50 50Z M50 42 C44 32 36 33 34 36 C38 44 46 45 50 42Z" fill="#7FA36E" stroke="#1D2E21" stroke-width="1.6"/>',
      '<path d="M50 70 V30" stroke="#3F6B3A" stroke-width="3.5" stroke-linecap="round"/><path d="M50 60 C38 52 28 56 26 60 C34 67 46 66 50 60Z M50 52 C62 42 72 46 74 50 C66 58 56 57 50 52Z M50 42 C40 32 32 34 30 38 C36 46 45 47 50 42Z M50 34 C58 24 66 26 67 30 C62 37 55 38 50 34Z" fill="#5E8C4F" stroke="#1D2E21" stroke-width="1.6"/>',
      '<path d="M50 70 V28" stroke="#3F6B3A" stroke-width="3.5" stroke-linecap="round"/><path d="M50 60 C38 52 28 56 26 60 C34 67 46 66 50 60Z M50 50 C62 40 72 44 74 48 C66 56 56 55 50 50Z M50 40 C40 30 32 32 30 36 C36 44 45 45 50 40Z" fill="#5E8C4F" stroke="#1D2E21" stroke-width="1.6"/><circle cx="62" cy="34" r="7" fill="#C2452F" stroke="#1D2E21" stroke-width="1.6"/><circle cx="38" cy="50" r="6" fill="#C2452F" stroke="#1D2E21" stroke-width="1.6"/><circle cx="50" cy="24" r="6" fill="#F3B526" stroke="#1D2E21" stroke-width="1.6"/>'
    ][lv];
    return '<svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="46" fill="#F4EFDF" stroke="#1D2E21" stroke-width="2.5"/><path d="M22 72 Q50 66 78 72 L74 80 Q50 76 26 80Z" fill="#8A6646" stroke="#1D2E21" stroke-width="1.6"/>' + leaves + '</svg>';
  }

  /* ---------- results ---------- */
  function results() {
    var s = score(), lv = level(s), L = LV[lv];
    var best = parseInt(store.get('gt-best'), 10), newBest = !(best >= s);
    if (newBest) store.set('gt-best', String(s));
    var squares = answers.map(function (a) { return a ? '🟩' : '🟥'; }).join('');
    var el = h('div', { class: 'gt-card gt-res' + (RM ? '' : ' gt-anim') });
    el.innerHTML =
      '<div class="gt-seeds" aria-hidden="true"></div>' +
      '<p class="gt-kicker">Your gardener level</p>' +
      '<div class="gt-badge" aria-hidden="true">' + badgeSvg(lv) + '</div>' +
      '<h2 class="gt-level">' + esc(L.name) + '</h2>' +
      '<p class="gt-score"><span class="gt-num">0</span>/15' + (newBest && best >= 0 ? ' <span class="gt-pb">New best</span>' : '') + '</p>' +
      '<p class="gt-sq" aria-label="' + s + ' right out of 15">' + answers.map(function (a) { return '<i class="' + (a ? 'ok' : 'no') + '"></i>'; }).join('') + '</p>' +
      '<p class="gt-line">' + esc(L.line) + '</p>' +
      '<div class="gt-after">' +
      '<form class="gt-form" novalidate>' +
      '<h3>Get your full breakdown</h3>' +
      '<p>Every answer explained, plus June’s tip for each one, sent straight to your inbox.</p>' +
      '<label class="sr" for="gt-email">Email address</label>' +
      '<input id="gt-email" name="email" type="email" autocomplete="email" inputmode="email" autocapitalize="off" spellcheck="false" placeholder="Your email" required>' +
      '<label class="gt-check"><input type="checkbox" name="news" value="yes"> <span>Yes, send me June’s emails too: tips, recipes and the odd offer.</span></label>' +
      '<button class="btn btn-block" type="submit">Send my breakdown</button>' +
      '<p class="gt-err" role="alert" hidden></p>' +
      '<p class="gt-small">Unsubscribe any time. <a href="/privacy/">Privacy</a></p>' +
      '</form>' +
      '<div class="gt-share"><button type="button" class="btn-outline gt-sharebtn">Challenge a friend</button><button type="button" class="btn-outline gt-again">Try again</button></div>' +
      '</div>';
    swap(el);
    sfx.results(); buzz(20);

    // count up, stamp, seeds, then the rest. Tap anywhere to skip.
    var num = el.querySelector('.gt-num');
    function finish() { revealTimer.forEach(clearTimeout); revealTimer = []; num.textContent = s; el.classList.add('gt-done'); }
    if (RM) finish();
    else {
      var steps = Math.max(s, 1), dur = 1100;
      for (var k = 1; k <= s; k++) (function (k) { revealTimer.push(setTimeout(function () { num.textContent = k; if (k % 2 === 0) tone(700 + k * 30, 0, 0, 0.04, 'sine', 0.035); }, (dur / steps) * k)); })(k);
      revealTimer.push(setTimeout(function () { el.classList.add('gt-stamp'); }, 1250));
      revealTimer.push(setTimeout(function () { seeds(el.querySelector('.gt-seeds')); }, 1500));
      revealTimer.push(setTimeout(finish, 2600));
      el.addEventListener('click', function skip(ev) { if (!el.classList.contains('gt-done') && !ev.target.closest('input,button,a,label')) finish(); });
    }

    // share
    el.querySelector('.gt-sharebtn').addEventListener('click', function (ev) {
      var text = 'I got ' + s + '/15 on June’s Gardener Level Test: ' + L.name + '.\n' + squares + '\nThink you can beat me?';
      var url = location.origin + '/test/?utm_source=share&utm_medium=social&utm_campaign=gardener_test';
      var b = ev.currentTarget;
      if (navigator.share) navigator.share({ title: 'The Gardener Level Test', text: text, url: url }).catch(function () {});
      else if (navigator.clipboard) navigator.clipboard.writeText(text + '\n' + url).then(function () { b.textContent = 'Copied. Paste it anywhere'; });
    });
    el.querySelector('.gt-again').addEventListener('click', function () { sfx.next(); i = 0; answers = []; question(); });

    // email
    var f = el.querySelector('.gt-form');
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var em = f.email.value.trim(), err = f.querySelector('.gt-err'), btn = f.querySelector('button[type=submit]');
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em)) { err.textContent = 'That email doesn’t look quite right.'; err.hidden = false; f.email.focus(); return; }
      err.hidden = true; btn.disabled = true; btn.textContent = 'Sending…';
      var fd = new FormData();
      fd.append('fields[email]', em);
      fd.append('fields[test_score]', String(s));
      fd.append('fields[test_level]', L.name);
      fd.append('fields[test_answers]', answers.join(''));
      fd.append('fields[test_newsletter]', f.news.checked ? 'yes' : 'no');
      fd.append('ml-submit', '1');
      fd.append('anticsrf', 'true');
      function done() {
        f.innerHTML = '<div class="gt-sent">' + TICK + '<div><h3>On its way</h3><p>Check your inbox in a minute or two (and your promotions or spam folder, just in case).</p></div></div>';
        sfx.right();
        if (window.zaraz) { try { zaraz.track('gardener_test_signup'); } catch (e) {} }
      }
      fetch(FORM, { method: 'POST', body: fd })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (j && j.success) done();
          else { btn.disabled = false; btn.textContent = 'Send my breakdown'; err.textContent = 'Something went wrong. Please check your email and try again.'; err.hidden = false; }
        })
        .catch(function () {
          // CORS or network hiccup: try once more without reading the reply
          fetch(FORM, { method: 'POST', body: fd, mode: 'no-cors' }).then(done).catch(function () {
            btn.disabled = false; btn.textContent = 'Send my breakdown'; err.textContent = 'Couldn’t connect. Please try again.'; err.hidden = false;
          });
        });
    });
  }

  function seeds(box) {
    if (!box) return;
    var cols = ['#F3B526', '#7FA36E', '#C2452F', '#F4EFDF', '#B48B62'];
    for (var n = 0; n < 18; n++) {
      var sd = h('i', { class: 'gt-seed' });
      sd.style.left = (Math.random() * 100) + '%';
      sd.style.background = cols[n % cols.length];
      sd.style.animationDelay = (Math.random() * 0.6) + 's';
      sd.style.animationDuration = (1.6 + Math.random() * 1.2) + 's';
      sd.style.setProperty('--r', (Math.random() * 360) + 'deg');
      box.appendChild(sd);
    }
    setTimeout(function () { box.innerHTML = ''; }, 3600);
  }

  intro();
})();
