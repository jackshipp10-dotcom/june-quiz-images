// June product promo in the Botanical Plate style (15 s, 1280x720 logical). Content comes from window.SPEC (same shape as the felt engine).
(function () {
  const TAU = Math.PI * 2;
  const INK = '#3a2a1c', INK_SOFT = 'rgba(58,42,28,0.55)', RED = '#9a4426';
  const T = { sage: '#93ab76', leaf: '#6f8f4c', terra: '#cf7a52', ochre: '#ddb058', rose: '#d08a8a', sky: '#93b4c4' };
  const FX = {};
  const cache = (k, f) => FX[k] || (FX[k] = f());
  const IMG = {};
  window.loadImgs = () => Promise.all(Object.entries(window.IMGS).map(([k, src]) => new Promise((res) => { const im = new Image(); im.onload = () => { IMG[k] = im; res(); }; im.src = src; })));
  const clamp = H.clamp, ease = H.ease;
  const prog = (t, a, b) => clamp((t - a) / (b - a));

  // ---------- geometry ----------
  const quad = (a, c, b, n = 40) => Array.from({ length: n + 1 }, (_, i) => { const s = i / n, u = 1 - s; return [u * u * a[0] + 2 * u * s * c[0] + s * s * b[0], u * u * a[1] + 2 * u * s * c[1] + s * s * b[1]]; });
  const leafShape = (x, y, len, wid, ang, bend = 0.12, n = 26) => {
    const rib = [], L = [], R = [], ca = Math.cos(ang), sa = Math.sin(ang), nx = -sa, ny = ca;
    for (let i = 0; i <= n; i++) {
      const s = i / n, off = bend * len * Math.sin(Math.PI * s) * 0.6;
      const px = x + ca * s * len + nx * off, py = y + sa * s * len + ny * off;
      rib.push([px, py]);
      const hw = wid * Math.pow(Math.sin(Math.PI * Math.min(1, s * 1.04)), 0.7) * (1 - 0.3 * s);
      L.push([px + nx * hw, py + ny * hw]); R.push([px - nx * hw, py - ny * hw]);
    }
    return { outline: L.concat(R.slice().reverse()), rib, L, R };
  };
  const ellipsePts = (cx, cy, rx, ry, rot = 0, n = 48, wob = 0, seed = 1, a0 = 0) => { const r = H.rng(seed); const ph = r() * TAU; return Array.from({ length: n + 1 }, (_, i) => { const a = a0 + (i / n) * TAU, k = 1 + wob * Math.sin(a * 3 + ph) ; const x = Math.cos(a) * rx * k, y = Math.sin(a) * ry * k; return [cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot)]; }); };
  const pathOf = (pts, close = true) => { const p = new Path2D(); pts.forEach(([x, y], i) => (i ? p.lineTo(x, y) : p.moveTo(x, y))); if (close) p.closePath(); return p; };
  const bbox = (pts) => { let a = 1e9, b = 1e9, c = -1e9, d = -1e9; pts.forEach(([x, y]) => { a = Math.min(a, x); b = Math.min(b, y); c = Math.max(c, x); d = Math.max(d, y); }); return [a, b, c, d]; };

  // ---------- engraved pen line, revealed along its length, swelling in the middle ----------
  const pen = (ctx, pts, p, w = 1.6, col = INK) => {
    if (p <= 0) return;
    const n = Math.max(2, Math.floor((pts.length - 1) * p) + 1);
    ctx.save(); ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for (let i = 1; i < n; i++) { const s = i / (pts.length - 1); ctx.lineWidth = w * (0.35 + 0.85 * Math.sin(Math.PI * s)); ctx.beginPath(); ctx.moveTo(pts[i - 1][0], pts[i - 1][1]); ctx.lineTo(pts[i][0], pts[i][1]); ctx.stroke(); }
    ctx.restore();
  };
  // ---------- hatching clipped to a shape; only the shadow side (from `from` across the shape) ----------
  const hatch = (ctx, outline, p, ang = 0.8, sp = 4.2, lw = 0.9, from = 0.45, col = INK) => {
    if (p <= 0) return;
    const [x0, y0, x1, y1] = bbox(outline), cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, R = Math.hypot(x1 - x0, y1 - y0) / 2 + 4;
    const dx = Math.cos(ang), dy = Math.sin(ang), nx = -dy, ny = dx, N = Math.floor((2 * R) / sp);
    const i0 = Math.floor(N * from), shown = i0 + Math.floor((N - i0) * p);
    ctx.save(); ctx.clip(pathOf(outline)); ctx.strokeStyle = col; ctx.globalAlpha = 0.8;
    for (let i = i0; i < shown; i++) { const o = -R + i * sp, k = (i - i0) / Math.max(1, N - i0); ctx.lineWidth = lw * (0.5 + 0.8 * k); const px = cx + nx * o, py = cy + ny * o; ctx.beginPath(); ctx.moveTo(px - dx * R, py - dy * R); ctx.lineTo(px + dx * R, py + dy * R); ctx.stroke(); }
    ctx.restore();
  };
  // ---------- watercolour tint: mottled, pooled edge, granulation, slightly off register ----------
  const washSpr = (key, outline, col, seed = 3) => cache('w' + key, () => {
    const [x0, y0, x1, y1] = bbox(outline), pad = 14, W = Math.ceil(x1 - x0 + pad * 2), Hh = Math.ceil(y1 - y0 + pad * 2);
    const cv = H.layer(W, Hh), c = cv.getContext('2d'); c.translate(pad - x0, pad - y0);
    const p = pathOf(outline); c.fillStyle = col; c.globalAlpha = 0.5; c.fill(p);
    c.globalAlpha = 0.5; c.lineWidth = 2.6; c.strokeStyle = col; c.filter = 'blur(1.2px)'; c.stroke(p); c.filter = 'none';
    c.setTransform(1, 0, 0, 1, 0, 0);
    const im = c.getImageData(0, 0, W, Hh), d = im.data, nz = H.makeNoise(seed), r = H.rng(seed + 7);
    for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++) { const k = (y * W + x) * 4; if (!d[k + 3]) continue; const m = 0.62 + 0.5 * (nz.fbm2(x * 0.035, y * 0.035, 3) * 0.5 + 0.5) + (r() < 0.04 ? 0.25 : 0); d[k + 3] = Math.min(255, d[k + 3] * m); }
    c.putImageData(im, 0, 0);
    return { cv, x: x0 - pad, y: y0 - pad, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, R: Math.hypot(x1 - x0, y1 - y0) / 2 + pad };
  });
  const wash = (ctx, key, outline, col, p, seed = 3, off = [3, -2]) => {
    if (p <= 0) return;
    const s = washSpr(key, outline, col, seed), e = ease.out(p);
    ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = clamp(p * 1.8);
    if (e < 1) { const cl = ellipsePts(s.cx + off[0], s.cy + off[1], s.R * 1.15 * e, s.R * 1.15 * e, 0, 40, 0.12, seed); ctx.clip(pathOf(cl)); }
    ctx.drawImage(s.cv, s.x + off[0], s.y + off[1]); ctx.restore();
  };

  // ---------- figures: lists of timed pen / hatch / wash ops ----------
  const runOps = (ctx, ops, t) => ops.forEach((o) => {
    const p = prog(t, o.t0, o.t0 + o.d);
    if (o.k === 'wash') wash(ctx, o.key, o.pts, o.col, p, o.seed || 3);
    else if (o.k === 'hatch') hatch(ctx, o.pts, p, o.ang, o.sp, o.lw, o.from);
    else if (o.k === 'pen') pen(ctx, o.pts, p, o.w, o.col);
    else if (o.k === 'dot' && p > 0) { ctx.save(); ctx.globalAlpha = p; ctx.fillStyle = o.col || INK; ctx.beginPath(); ctx.arc(o.x, o.y, o.r, 0, TAU); ctx.fill(); ctx.restore(); }
  });
  const leafOps = (key, x, y, len, wid, ang, t0, tint = T.leaf, seed = 1) => {
    const lf = leafShape(x, y, len, wid, ang), ops = [];
    ops.push({ k: 'wash', key: key, pts: lf.outline, col: tint, t0: t0 + 0.35, d: 0.6, seed });
    ops.push({ k: 'pen', pts: lf.L, w: 1.5, t0, d: 0.35 }, { k: 'pen', pts: lf.R, w: 1.5, t0: t0 + 0.05, d: 0.35 }, { k: 'pen', pts: lf.rib, w: 1.0, t0: t0 + 0.1, d: 0.3 });
    for (let s = 0.2; s < 0.85; s += 0.15) { const i = Math.round(s * (lf.rib.length - 1)), j = Math.min(lf.L.length - 1, i + 3); ops.push({ k: 'pen', pts: quad(lf.rib[i], [(lf.rib[i][0] + lf.L[j][0]) / 2, (lf.rib[i][1] + lf.L[j][1]) / 2], lf.L[j], 6), w: 0.7, t0: t0 + 0.2 + s * 0.2, d: 0.15 }); }
    ops.push({ k: 'hatch', pts: lf.outline, ang: ang + 1.2, sp: 3.6, lw: 0.8, from: 0.55, t0: t0 + 0.3, d: 0.45 });
    return ops;
  };
  const sprigOps = (key, x, y, len, ang, t0, n = 4, tint = T.leaf, flip = 1, sc = 1) => {
    const tip = [x + Math.cos(ang) * len, y + Math.sin(ang) * len], mid = [x + Math.cos(ang) * len * 0.5 - Math.sin(ang) * len * 0.15 * flip, y + Math.sin(ang) * len * 0.5 + Math.cos(ang) * len * 0.15 * flip];
    const stem = quad([x, y], mid, tip, 30), ops = [{ k: 'pen', pts: stem, w: 1.7, t0, d: 0.4 }];
    for (let i = 0; i < n; i++) { const s = 0.25 + (i / n) * 0.7, q = stem[Math.round(s * 30)], side = i % 2 ? 1 : -1; ops.push(...leafOps(key + i, q[0], q[1], 46 * sc * (1.1 - s * 0.4), 15 * sc, ang + side * 0.85, t0 + 0.15 + i * 0.08, tint, i + 3)); }
    return ops;
  };
  const flowerOps = (key, x, y, r, t0, tint = T.rose) => {
    const ops = [];
    for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + (i / 5) * TAU, pt = ellipsePts(x + Math.cos(a) * r * 0.62, y + Math.sin(a) * r * 0.62, r * 0.55, r * 0.36, a, 30, 0.05, i + 2); ops.push({ k: 'wash', key: key + i, pts: pt, col: tint, t0: t0 + 0.25 + i * 0.04, d: 0.45, seed: i + 9 }, { k: 'pen', pts: pt, w: 1.2, t0: t0 + i * 0.05, d: 0.3 }, { k: 'hatch', pts: pt, ang: a + 1.4, sp: 3.4, lw: 0.6, from: 0.6, t0: t0 + 0.3, d: 0.3 }); }
    const c = ellipsePts(x, y, r * 0.22, r * 0.22, 0, 24, 0, 4); ops.push({ k: 'wash', key: key + 'c', pts: c, col: T.ochre, t0: t0 + 0.4, d: 0.3 }, { k: 'pen', pts: c, w: 1.1, t0: t0 + 0.3, d: 0.2 });
    for (let i = 0; i < 6; i++) { const a = (i / 6) * TAU; ops.push({ k: 'dot', x: x + Math.cos(a) * r * 0.1, y: y + Math.sin(a) * r * 0.1, r: 1.3, t0: t0 + 0.5, d: 0.1 }); }
    return ops;
  };
  // the pea plant on plate I
  const peaOps = (bx, by) => cache('pea', () => {
    const stem = quad([bx, by], [bx + 60, by - 250], [bx + 20, by - 500], 60), ops = [{ k: 'pen', pts: stem, w: 2.2, t0: 0.05, d: 0.6 }];
    [[0.22, -2.55, 0.25], [0.5, -2.45, 0.42], [0.78, -2.3, 0.6], [0.3, -0.5, 0.33]].forEach(([s, a, st], i) => { const q = stem[Math.round(s * 60)]; ops.push(...leafOps('pl' + i, q[0], q[1], 118 - s * 40, 40 - s * 10, a, st, i % 2 ? T.leaf : T.sage, i + 1)); });
    const top = stem[60], tend = Array.from({ length: 60 }, (_, i) => { const s = i / 59, a = -1.2 + s * 9, r = 34 * (1 - s * 0.85); return [top[0] + 28 + Math.cos(a) * r * 1.0 - 20 * (1 - s), top[1] - 18 + Math.sin(a) * r]; });
    ops.push({ k: 'pen', pts: quad(top, [top[0] + 10, top[1] - 10], tend[0], 8), w: 1.2, t0: 0.6, d: 0.15 }, { k: 'pen', pts: tend, w: 1.1, t0: 0.72, d: 0.6 });
    const q = stem[Math.round(0.6 * 60)], pod = leafShape(q[0] + 4, q[1] + 6, 165, 24, 0.62, -0.2);
    ops.push({ k: 'pen', pts: quad(q, [q[0] + 8, q[1] + 2], [q[0] + 4, q[1] + 6], 4), w: 1.4, t0: 0.6, d: 0.1 }, { k: 'wash', key: 'pod', pts: pod.outline, col: T.leaf, t0: 1.05, d: 0.6, seed: 12 }, { k: 'pen', pts: pod.L, w: 1.6, t0: 0.7, d: 0.4 }, { k: 'pen', pts: pod.R, w: 1.6, t0: 0.74, d: 0.4 }, { k: 'hatch', pts: pod.outline, ang: 2.3, sp: 3.4, lw: 0.8, from: 0.55, t0: 0.95, d: 0.45 });
    for (let i = 0; i < 5; i++) { const pp = pod.rib[5 + i * 4], pea = ellipsePts(pp[0], pp[1], 9, 9, 0, 20, 0, i); ops.push({ k: 'pen', pts: pea, w: 0.9, t0: 1.05 + i * 0.05, d: 0.15 }); }
    ops.push(...flowerOps('pf', stem[48][0] + 70, stem[48][1] - 20, 30, 0.85, T.rose));
    ops.push({ k: 'pen', pts: quad(stem[48], [stem[48][0] + 30, stem[48][1] - 30], [stem[48][0] + 58, stem[48][1] - 22], 10), w: 1.2, t0: 0.8, d: 0.15 });
    return ops;
  });

  // ---------- paper: foxed rag paper with a pressed plate mark per beat ----------
  const PW = 5120;
  const paper = (Hh) => cache('paper', () => {
    const cv = H.layer(PW, Hh), c = cv.getContext('2d'), im = c.createImageData(PW, Hh), d = im.data, nz = H.makeNoise(5), g = H.rng(4);
    for (let y = 0; y < Hh; y++) for (let x = 0; x < PW; x++) { const k = (y * PW + x) * 4, m = 0.955 + 0.045 * nz.fbm2(x * 0.004, y * 0.004, 4) + (g() - 0.5) * 0.03; d[k] = 240 * m; d[k + 1] = 230 * m; d[k + 2] = 207 * m; d[k + 3] = 255; }
    c.putImageData(im, 0, 0);
    const r = H.rng(11);
    c.strokeStyle = 'rgba(120,95,60,0.08)'; c.lineWidth = 0.7;
    for (let i = 0; i < 1400; i++) { const x = r() * PW, y = r() * Hh, a = r() * TAU, l = 4 + r() * 12; c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + Math.cos(a + 0.5) * l * 0.5, y + Math.sin(a + 0.5) * l * 0.5, x + Math.cos(a) * l, y + Math.sin(a) * l); c.stroke(); }
    for (let i = 0; i < 260; i++) { const edge = r() < 0.7, x = r() * PW, y = edge ? (r() < 0.5 ? r() * 60 : Hh - r() * 60) : r() * Hh, s = 1.5 + r() * (edge ? 9 : 4); const gr = c.createRadialGradient(x, y, 0, x, y, s); gr.addColorStop(0, `rgba(150,95,45,${0.1 + r() * 0.18})`); gr.addColorStop(1, 'rgba(150,95,45,0)'); c.fillStyle = gr; c.beginPath(); c.arc(x, y, s, 0, TAU); c.fill(); }
    ['I', 'II', 'III', 'IV'].forEach((n, i) => {
      const O = i * 1280, x = O + 34, y = 24, w = 1212, h = 672;
      c.fillStyle = 'rgba(255,252,240,0.22)'; c.fillRect(x, y, w, h);
      c.lineWidth = 2; c.strokeStyle = 'rgba(255,255,250,0.7)'; c.strokeRect(x - 1, y - 1, w, h);
      c.strokeStyle = 'rgba(110,80,45,0.28)'; c.strokeRect(x + 1.5, y + 1.5, w, h);
      const ig = c.createLinearGradient(0, y, 0, y + 14); ig.addColorStop(0, 'rgba(110,80,45,0.1)'); ig.addColorStop(1, 'rgba(110,80,45,0)'); c.fillStyle = ig; c.fillRect(x, y, w, 14);
      c.fillStyle = INK_SOFT; c.font = 'italic 400 17px "Lora"'; c.textAlign = 'right'; c.fillText('Pl. ' + n + '.', O + 1220, 54);
    });
    return cv;
  });

  // ---------- text ----------
  const font = (o) => `${o.it ? 'italic ' : ''}${o.wt || 400} ${o.px}px "Lora"`;
  const fitPx = (str, o, maxW) => { const m = H.layer(4, 4).getContext('2d'); let px = o.px; m.letterSpacing = (o.ls || 0) + 'px'; for (; px > 14; px -= 1) { m.font = font({ ...o, px }); if (m.measureText(str).width <= maxW) break; } return px; };
  // characters appear in sequence like ink taking to the paper
  const inkText = (ctx, str, x, y, o, t, t0, per = 0.035) => {
    if (t < t0) return;
    ctx.save(); ctx.font = font(o); ctx.letterSpacing = (o.ls || 0) + 'px'; ctx.fillStyle = o.col || INK; ctx.textBaseline = 'alphabetic';
    const W = ctx.measureText(str).width; let cx = o.al === 'left' ? x : o.al === 'right' ? x - W : x - W / 2;
    for (let i = 0; i < str.length; i++) { const a = clamp((t - t0 - i * per) / 0.22); const w = ctx.measureText(str.slice(0, i + 1)).width - ctx.measureText(str.slice(0, i)).width; if (a > 0) { ctx.globalAlpha = a * (o.a ?? 1); ctx.fillText(str[i], cx, y + (1 - ease.out(a)) * 4); } cx += w; }
    ctx.restore();
    return W;
  };
  const textW = (str, o) => { const m = H.layer(4, 4).getContext('2d'); m.font = font(o); m.letterSpacing = (o.ls || 0) + 'px'; return m.measureText(str).width; };
  const rule = (ctx, x0, x1, y, p, w = 1) => pen(ctx, [[x0, y], [x0 + (x1 - x0) * 0.5, y + 0.6], [x1, y]].flatMap((a, i, arr) => (i ? Array.from({ length: 12 }, (_, k) => [arr[i - 1][0] + (a[0] - arr[i - 1][0]) * (k + 1) / 12, arr[i - 1][1] + (a[1] - arr[i - 1][1]) * (k + 1) / 12]) : [a])), p, w);

  // a page tipped in: paper drop shadow, image, double ink rule
  const plate = (ctx, img, x, y, w, h, t, st, rot = 0) => {
    if (t < st) return;
    const u = prog(t, st, st + 0.5), e = ease.out(u), lift = 1 - e;
    ctx.save(); ctx.translate(x + w / 2, y + h / 2 - lift * 16); ctx.rotate(rot); ctx.globalAlpha = clamp(u * 2.2);
    ctx.shadowColor = `rgba(70,45,20,${0.28 - lift * 0.1})`; ctx.shadowBlur = 8 + lift * 20; ctx.shadowOffsetX = 3 + lift * 8; ctx.shadowOffsetY = 5 + lift * 14;
    ctx.fillStyle = '#f8f2e2'; ctx.fillRect(-w / 2, -h / 2, w, h); ctx.shadowColor = 'transparent';
    ctx.drawImage(img, -w / 2 + 12, -h / 2 + 12, w - 24, h - 24);
    ctx.restore();
    ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.rotate(rot); ctx.translate(-x - w / 2, -y - h / 2);
    const fp = prog(t, st + 0.25, st + 0.8), box = (i, lw) => { const pts = [[x - i, y - i], [x + w + i, y - i], [x + w + i, y + h + i], [x - i, y + h + i], [x - i, y - i]]; const dense = pts.slice(1).flatMap((b, k) => Array.from({ length: 20 }, (_, j) => [pts[k][0] + (b[0] - pts[k][0]) * (j + 1) / 20, pts[k][1] + (b[1] - pts[k][1]) * (j + 1) / 20])); pen(ctx, [pts[0], ...dense], fp, lw); };
    box(6, 1.5); box(11, 0.7);
    ctx.restore();
  };
  // engraved roundel with a roman numeral, hatched on its shadow side
  const roundel = (ctx, x, y, r, num, t, st) => {
    if (t < st) return;
    const o1 = ellipsePts(x, y, r, r, 0, 60, 0, 1, -1.6), o2 = ellipsePts(x, y, r - 6, r - 6, 0, 60, 0, 1, -1.6), p = prog(t, st, st + 0.4);
    ctx.save(); ctx.globalAlpha = clamp(p * 3); ctx.fillStyle = 'rgba(250,244,228,0.9)'; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); ctx.restore();
    wash(ctx, 'rd' + num, o2, T.sage, prog(t, st + 0.3, st + 0.8), num.length + 4);
    pen(ctx, o1, p, 1.8); pen(ctx, o2, prog(t, st + 0.1, st + 0.5), 0.9);
    hatch(ctx, o2, prog(t, st + 0.3, st + 0.7), 0.9, 3.4, 0.7, 0.62);
    inkText(ctx, num, x, y + r * 0.32, { px: Math.round(r * 0.85), wt: 600 }, t, st + 0.25, 0.05);
  };
  // lettered annotation with a fine dotted leader line, as on a natural history plate
  const leader = (ctx, from, to, p) => { if (p <= 0) return; ctx.save(); ctx.strokeStyle = INK; ctx.lineWidth = 0.9; ctx.setLineDash([2, 4]); ctx.beginPath(); ctx.moveTo(from[0], from[1]); ctx.lineTo(from[0] + (to[0] - from[0]) * p, from[1] + (to[1] - from[1]) * p); ctx.stroke(); ctx.restore(); if (p > 0.95) { ctx.save(); ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(from[0], from[1], 2.2, 0, TAU); ctx.fill(); ctx.restore(); } };

  const EXPLAIN = (ctx, W, H_, t) => {
    const S = window.SPEC;
    const seg = (a, b) => ease.inOut(prog(t, a, b));
    const cam = 1280 * seg(2.0, 2.6) + 1280 * seg(5.6, 6.2) + 1280 * seg(9.0, 9.6);
    ctx.drawImage(paper(H_), -cam, 0);
    ctx.save(); ctx.translate(-cam, 0);

    // PLATE I (0 to 2 s): the pea plant engraves itself and is tinted; the hook is printed beside it
    if (t < 2.7) {
      runOps(ctx, peaOps(250, 620), t);
      inkText(ctx, 'Fig. 1.  Pisum sativum, the garden pea', 250, 664, { px: 15, it: true, col: INK_SOFT }, t, 1.3, 0.012);
      const [h1, h2] = S.hook, cx = 790;
      const px1 = fitPx(h1, { px: 66, wt: 500 }, 720), px2 = fitPx(h2, { px: 80, wt: 700, it: true }, 720);
      inkText(ctx, 'FROM THE NOTEBOOKS OF JUNE', cx, 206, { px: 17, ls: 5, col: RED }, t, 0.1, 0.012);
      rule(ctx, cx - 150, cx + 150, 228, prog(t, 0.2, 0.6), 1.1);
      inkText(ctx, h1, cx, 330, { px: px1, wt: 500 }, t, 0.25, 0.035);
      wash(ctx, 'hookwash', ellipsePts(cx, 404, Math.min(380, textW(h2, { px: px2, wt: 700, it: true }) / 2 + 40), 46, -0.02, 50, 0.08, 6), T.ochre, prog(t, 1.0, 1.7), 6);
      inkText(ctx, h2, cx, 430, { px: px2, wt: 700, it: true }, t, 0.7, 0.04);
      rule(ctx, cx - 110, cx + 110, 492, prog(t, 1.4, 1.8), 0.9);
    }

    // PLATE II (2.3 to 5.5 s): three real pages tipped in as figures with italic captions, then the heading
    if (t > 1.9 && t < 6.6) {
      const O = 1280;
      S.pages.forEach((pg, i) => {
        const st = 2.4 + i * 0.35, x = O + pg.x, rot = [-0.012, 0.006, 0.012][i];
        plate(ctx, IMG[pg.img], x, pg.y, pg.w, pg.h, t, st, rot);
        inkText(ctx, `Fig. ${i + 2}.`, x + pg.w / 2, pg.y + pg.h + 44, { px: 15, it: true, col: INK_SOFT }, t, st + 0.35, 0.02);
        inkText(ctx, pg.tag, x + pg.w / 2, pg.y + pg.h + 74, { px: fitPx(pg.tag, { px: 27, it: true, wt: 500 }, pg.w + 40), it: true, wt: 500 }, t, st + 0.45, 0.025);
      });
      const hy = S.pages[0].y < 160 ? 96 : 118, hw = textW(S.heading.toUpperCase(), { px: 26, ls: 6, wt: 500 });
      inkText(ctx, S.heading.toUpperCase(), O + 640, hy, { px: 26, ls: 6, wt: 500 }, t, 4.4, 0.02);
      rule(ctx, O + 640 - hw / 2 - 90, O + 640 - hw / 2 - 20, hy - 9, prog(t, 4.7, 5.0), 1);
      rule(ctx, O + 640 + hw / 2 + 20, O + 640 + hw / 2 + 90, hy - 9, prog(t, 4.7, 5.0), 1);
    }

    // PLATE III (5.9 to 9.0 s): the hero page on a soft wash, lettered annotations, a sprig and a flower
    if (t > 5.5 && t < 10.0) {
      const O = 2560, hr = S.hero, hx = O + hr.x, hy = hr.y;
      wash(ctx, 'herowash', ellipsePts(hx + hr.w / 2, hy + hr.h / 2, hr.w * 0.72, hr.h * 0.58, 0.05, 60, 0.05, 8), T.sage, prog(t, 6.0, 6.9), 8, [0, 0]);
      plate(ctx, IMG[hr.img], hx, hy, hr.w, hr.h, t, 6.2, 0.01);
      inkText(ctx, 'Fig. 5.  ' + S.title, hx + hr.w / 2, Math.min(700, hy + hr.h + 40), { px: 15, it: true, col: INK_SOFT }, t, 6.6, 0.012);
      S.facts.forEach((f, i) => {
        const n = S.facts.length, fy = hy + hr.h / 2 + 14 + (i - (n - 1) / 2) * 120, fx = O + hr.fx + 30, st = 6.9 + i * 0.5;
        leader(ctx, [hx + hr.w - 40, hy + hr.h * (0.38 + i * 0.24)], [fx - 14, fy - 12], prog(t, st, st + 0.3));
        inkText(ctx, 'abc'[i] + '.', fx, fy, { px: 28, it: true, al: 'left', col: RED }, t, st + 0.2);
        inkText(ctx, f, fx + 34, fy, { px: fitPx(f, { px: 42, wt: 500 }, 1200 - hr.fx - 70), wt: 500, al: 'left' }, t, st + 0.25, 0.02);
      });
      runOps(ctx, cache('sp3', () => sprigOps('s3', O + 1190, 670, 190, -2.5, 7.9, 5, T.leaf, 1, 0.9)), t);
      runOps(ctx, cache('fl3', () => flowerOps('f3', hx + hr.w - 10, hy + 6, 34, 8.4, T.rose)), t);
    }

    // PLATE IV (9.4 to 12.9 s): three numbered roundels joined by a growing vine, then the emphasis line on a wash
    if (t > 9.0) {
      const O = 3840, y = 255, xs = [O + 260, O + 640, O + 1020];
      const vine = cache('vine', () => Array.from({ length: 121 }, (_, i) => { const s = i / 120, x = O + 90 + s * 1100; return [x, y + Math.sin(s * TAU * 1.5) * 26]; }));
      pen(ctx, vine, prog(t, 9.6, 11.6), 1.8);
      runOps(ctx, cache('vleaves', () => [0.08, 0.22, 0.42, 0.58, 0.78, 0.92].flatMap((s, i) => { const q = vine[Math.round(s * 120)]; return leafOps('v' + i, q[0], q[1], 40, 14, (i % 2 ? 0.9 : -0.9) - 0.6, 9.6 + s * 2.0, i % 2 ? T.leaf : T.sage, i + 20); })), t);
      const SP = Math.min(...S.steps.map((s) => fitPx(s, { px: 38, it: true, wt: 500 }, 340)));
      S.steps.forEach((s, i) => { const st = 9.75 + i * 0.7; roundel(ctx, xs[i], y, 44, ['I', 'II', 'III'][i], t, st); inkText(ctx, s, xs[i], y + 100, { px: SP, it: true, wt: 500 }, t, st + 0.3, 0.025); });
      const hot = t > 12.2, bounce = hot ? 1 + 0.08 * Math.sin(prog(t, 12.2, 12.6) * Math.PI) : 1;
      const ePx = fitPx(S.emphasis, { px: S.emphPx || 72, wt: 700 }, 980), ew = textW(S.emphasis, { px: ePx, wt: 700 });
      wash(ctx, 'emw', ellipsePts(O + 640, 512, ew / 2 + 60, 56, 0.01, 60, 0.07, 14), T.ochre, prog(t, 11.9, 12.4), 14);
      ctx.save(); ctx.translate(O + 640, 512); ctx.scale(bounce, bounce); ctx.translate(-(O + 640), -512);
      inkText(ctx, S.emphasis, O + 640, 536, { px: ePx, wt: 700, col: hot ? RED : INK }, t, 11.8, 0.02);
      ctx.restore();
      if (hot) runOps(ctx, cache('fl4', () => flowerOps('f4', O + 640 + ew / 2 + 74, 462, 36, 12.2, T.rose)), t);
    }
    ctx.restore();

    // running head
    inkText(ctx, 'PLOT TO PLATE WITH JUNE', 64, 56, { px: 15, ls: 4, al: 'left', col: INK_SOFT }, t, 2.25, 0.01);

    // END (13 to 15 s): a printed label pasted over the last plate
    if (t >= 12.9) {
      const u = prog(t, 12.95, 13.4), e = ease.out(u);
      ctx.save(); ctx.globalAlpha = clamp(u * 2) * 0.35; ctx.fillStyle = 'rgb(232,220,195)'; ctx.fillRect(0, 0, W, H_); ctx.restore();
      ctx.save(); ctx.globalAlpha = clamp(u * 2.5); ctx.translate(640, 360 - (1 - e) * 18);
      ctx.shadowColor = 'rgba(70,45,20,0.3)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 12;
      ctx.fillStyle = '#f6efdc'; ctx.beginPath(); ctx.ellipse(0, 0, 520, 210, 0, 0, TAU); ctx.fill(); ctx.restore();
      if (t > 13.0) {
        pen(ctx, ellipsePts(640, 360, 500, 192, 0, 120, 0, 1, -1.57), prog(t, 13.0, 13.6), 1.8);
        pen(ctx, ellipsePts(640, 360, 488, 181, 0, 120, 0, 1, -1.57), prog(t, 13.1, 13.7), 0.8);
        runOps(ctx, cache('endL', () => sprigOps('eL', 330, 470, 150, -2.6, 13.3, 4, T.leaf, 1, 0.8)), t);
        runOps(ctx, cache('endR', () => sprigOps('eR', 950, 470, 150, -0.54, 13.3, 4, T.sage, -1, 0.8)), t);
        inkText(ctx, 'PLOT TO PLATE WITH JUNE', 640, 270, { px: 16, ls: 5, col: RED }, t, 13.05, 0.01);
        const tPx = fitPx(S.title, { px: S.titlePx || 54, wt: 700 }, 800);
        inkText(ctx, S.title, 640, 360, { px: tPx, wt: 700 }, t, 13.1, 0.02);
        rule(ctx, 540, 740, 392, prog(t, 13.4, 13.7), 1);
        inkText(ctx, S.subtitle.replace(/\s+·\s+/g, '  ·  '), 640, 440, { px: fitPx(S.subtitle, { px: 28, it: true }, 760), it: true, col: INK }, t, 13.45, 0.015);
      }
    }
    H.vignette(ctx, W, H_, 0.32, '80,55,25');
    H.grain(ctx, W, H_, 0.02, 6 + Math.floor(t * 12));
  };
  window.DURATION = 15;
  window.explainer = EXPLAIN;

  // vertical (9:16) caption overlay: a printed label on top, "Link in bio" below
  window.overlay = (ctx) => {
    const S = window.SPEC, lab = (str, y, o) => {
      ctx.save(); ctx.font = font(o); ctx.letterSpacing = (o.ls || 0) + 'px'; const w = ctx.measureText(str).width + 90, h = o.px * 1.9;
      ctx.shadowColor = 'rgba(60,40,20,0.45)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 8; ctx.fillStyle = '#f6efdc'; ctx.fillRect(540 - w / 2, y - h / 2, w, h); ctx.shadowColor = 'transparent';
      ctx.strokeStyle = INK; ctx.lineWidth = 2; ctx.strokeRect(540 - w / 2 + 9, y - h / 2 + 9, w - 18, h - 18); ctx.lineWidth = 0.8; ctx.strokeRect(540 - w / 2 + 15, y - h / 2 + 15, w - 30, h - 30);
      ctx.fillStyle = o.col || INK; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(str, 540, y + 3); ctx.restore();
    };
    lab(S.title, 330, { px: fitPx(S.title, { px: S.vTitlePx || 52, wt: 700 }, 880), wt: 700 });
    lab('Link in bio', 1700, { px: 50, it: true, wt: 600, col: RED });
  };
})();
