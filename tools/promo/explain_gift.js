  // ===================== June's Grow Your Own Gift Set: 15 s, silent first (Etsy) =====================
  const IMG = {};
  window.loadImgs = () => Promise.all(Object.entries(window.IMGS).map(([k, src]) => new Promise((res) => { const im = new Image(); im.onload = () => { IMG[k] = im; res(); }; im.src = src; })));
  // a real product page sewn onto a felt backing: cream felt border, the printed page inset, running stitch round it
  const pageSpr = (key, img, w, h, felt = '#f3ecdc', thread = '#c8443a') => feltSpr('pg' + key, [[0, 0], [w, 0], [w, h], [0, h]], felt, w, h, (c) => {
    const ins = 16;
    c.save(); c.shadowColor = 'rgba(40,20,10,0.35)'; c.shadowBlur = 4; c.shadowOffsetX = 1.5; c.shadowOffsetY = 2.5;
    c.drawImage(img, ins, ins, w - ins * 2, h - ins * 2); c.restore();
    frun(c, [[7, 7], [w - 7, 7], [w - 7, h - 7], [7, h - 7], [7, 7]], thread, 9, 5, 2.2);
  });
  // felt gift parcel: box + lid, satin ribbon cross, felt bow
  const parcelSpr = () => feltSpr('parcel', [[0, 60], [300, 60], [300, 300], [0, 300]], '#2f6b4f', 300, 300, (c) => {
    c.save(); c.shadowColor = 'rgba(40,20,10,0.4)'; c.shadowBlur = 6; c.shadowOffsetX = 2; c.shadowOffsetY = 4;
    c.fillStyle = '#3a7d5c'; c.fillRect(-10, 50, 320, 62); c.restore();
    fsatin(c, 150, 52, 150, 300, '#d9564a', 30);
    fsatin(c, -8, 80, 308, 80, '#d9564a', 26);
    const loop = (sx) => { const pts = Array.from({ length: 40 }, (_, i) => { const a = (i / 40) * Math.PI * 2; return [150 + sx * (40 + Math.cos(a) * 38), 30 + Math.sin(a) * 26]; }); c.save(); c.shadowColor = 'rgba(40,20,10,0.4)'; c.shadowBlur = 5; c.shadowOffsetY = 3; c.beginPath(); pts.forEach(([x, y], i) => (i ? c.lineTo(x, y) : c.moveTo(x, y))); c.closePath(); c.fillStyle = '#e06456'; c.fill(); c.restore(); frun(c, pts, '#a33b30', 6, 4, 1.6); };
    loop(-1); loop(1);
    c.fillStyle = '#c8443a'; c.beginPath(); c.arc(150, 32, 16, 0, TAU); c.fill();
    frun(c, [[12, 124], [288, 124], [288, 288], [12, 288], [12, 124]], '#f4ead2', 9, 5, 2);
  });

  const EXPLAIN = (ctx, W, H_, t) => {
    const seg = (a, b) => H.ease.inOut(H.clamp((t - a) / (b - a)));
    const prog = (a, b) => H.clamp((t - a) / (b - a));
    const put = (spr, x, y, st, o = {}) => {
      if (!spr || t < st) return;
      const u = H.clamp((t - st) / 0.45), lift = 1 - H.ease.out(u), sq = u > 0.45 && u < 1 ? Math.sin(((u - 0.45) / 0.55) * Math.PI) * 0.04 : 0;
      const cx = x + spr.w / 2, cy = y + spr.h / 2;
      ctx.save();
      ctx.shadowColor = `rgba(40,20,10,${0.45 - lift * 0.2})`; ctx.shadowBlur = (o.sb ?? 10) + lift * 26; ctx.shadowOffsetX = (o.sx ?? 4) + lift * 18; ctx.shadowOffsetY = (o.sy ?? 6) + lift * 26;
      ctx.globalAlpha = H.clamp(u * 5);
      ctx.translate(cx, cy - lift * 30); if (o.rot) ctx.rotate(o.rot); ctx.scale((1 + lift * 0.14 + sq) * (o.s || 1), (1 + lift * 0.14 - sq) * (o.s || 1)); ctx.translate(-cx, -cy);
      ctx.drawImage(spr, x - spr.pad, y - spr.pad); ctx.restore();
    };
    const ringSew = (cx, cy, rx, ry, a, b, seed, col = '#c8443a') => {
      const ring = circPts(cx, cy, rx, ry, 140, 0.02, seed), rp = prog(a, b);
      for (let i = 0; i < ring.length * rp; i += 2) { const [x, y] = ring[i], dx = x - cx, dy = y - cy, d = Math.hypot(dx, dy) || 1; fthread(ctx, x - (dx / d) * 12, y - (dy / d) * 12, x, y, col, 2.6); if (i > 1) fthread(ctx, ring[i - 2][0], ring[i - 2][1], x, y, col, 2.6); }
    };
    // ---- camera pans along the quilt ----
    const cam = 1280 * seg(2.0, 2.6) + 1280 * seg(5.6, 6.2) + 1280 * seg(9.0, 9.6);
    // ---- quilt (baked once, 2560 wide, tiled): unchanged from the reference ----
    if (!FX.quilt) {
      const QW = 2560, P = 160, C = H.layer(QW, H_), c = C.getContext('2d'), img = c.createImageData(QW, H_), d = img.data;
      const nz = H.makeNoise(21), r = H.rng(314), cols = QW / P, rows = Math.ceil(H_ / P) + 1, pick = [];
      for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) { let k; do { k = r.int(0, PRINTS.length - 1); } while ((i > 0 && pick[j * cols + i - 1] === k) || (j > 0 && pick[(j - 1) * cols + i] === k)); pick.push(k); }
      const grain = H.rng(9), lnz = H.makeNoise(77);
      for (let y = 0; y < H_; y++) {
        const yy = y + 30, j = Math.floor(yy / P), v = yy - j * P;
        if (y % 8 === 0) {
          FX.lg0 = FX.lg1 || null; FX.lg1 = []; const y8 = y + 8;
          for (let x = 0; x <= QW; x += 8) { const a = (x / QW) * TAU; FX.lg1.push(0.85 + 0.15 * lnz.fbm3(Math.cos(a) * 0.9, Math.sin(a) * 0.9, y8 * 0.0035, 3)); }
          if (!FX.lg0) { FX.lg0 = []; for (let x = 0; x <= QW; x += 8) { const a = (x / QW) * TAU; FX.lg0.push(0.85 + 0.15 * lnz.fbm3(Math.cos(a) * 0.9, Math.sin(a) * 0.9, y * 0.0035, 3)); } }
        }
        const yt = (y % 8) / 8, lrow = FX.lg0.map((v, q) => v + (FX.lg1[q] - v) * yt);
        for (let x = 0; x < QW; x++) {
          const i = Math.floor(x / P), u = x - i * P, pr = PRINTS[pick[j * cols + i]];
          const col = H.mix(printCol(pr, Math.max(0, u + nz.n2(x * 0.02, y * 0.02) * 1.2), Math.max(0, v + nz.n2(x * 0.02 + 9, y * 0.02) * 1.2)), [214, 200, 178], 0.3);
          const wx = x % 3, wy = y % 3, over = (Math.floor(x / 3) + Math.floor(y / 3)) & 1;
          const wv = 1 + (over ? (wx === 1 ? 0.05 : -0.02) : (wy === 1 ? 0.05 : -0.02)) - (wx === 0 && wy === 0 ? 0.06 : 0) + (grain() - 0.5) * 0.06;
          const e = Math.min(u, P - u, v, P - v), puff = 0.93 - 0.36 * Math.exp(-e / 14) + (0.08 * (P / 2 - u + (P / 2 - v))) / P, seam = Math.exp(-(e * e) / 2.5) * 0.45;
          const lq = x >> 3, lf = lrow[lq] + ((lrow[lq + 1] ?? lrow[0]) - lrow[lq]) * ((x & 7) / 8);
          const s = wv * puff * (1 - seam) * lf, k = (y * QW + x) * 4;
          d[k] = col[0] * s; d[k + 1] = col[1] * s; d[k + 2] = col[2] * s; d[k + 3] = 255;
        }
      }
      c.putImageData(img, 0, 0);
      for (let gx = 9; gx < QW; gx += P) frun(c, [[gx, -10], [gx, H_ + 10]], '#f4ead6', 10, 7, 2.4);
      for (let gy = -21; gy < H_ + P; gy += P) frun(c, [[-10, gy], [QW + 10, gy]], '#f4ead6', 10, 7, 2.4);
      FX.quilt = C;
    }
    const qx = -(cam % 2560);
    ctx.drawImage(FX.quilt, qx, 0); ctx.drawImage(FX.quilt, qx + 2560, 0);

    ctx.save(); ctx.translate(-cam, 0); // ======== world ========

    // ---- BEAT 1 (0 to 2 s): hook, felt letters dropped on a backing oval ----
    {
      const cols = ['#d9564a', '#2f5f9a', '#e8b04a', '#3f8c86', '#c8443a'];
      const line = (str, px, y, st, off) => {
        const m = H.layer(4, 4).getContext('2d'); m.font = `700 ${px}px "Fredoka"`;
        let x = 640 - (m.measureText(str).width + str.length * 6) / 2, i = 0;
        for (const ch of str) { const w = m.measureText(ch).width; if (ch !== ' ') put(feltText('L' + ch + px + (i + off) % 5, ch, px, cols[(i + off) % 5]), x, y, st + i * 0.06, { rot: (H.rng(i + off)() - 0.5) * 0.12 }); x += w + 6; i++; }
      };
      put(feltSpr('b1back', circPts(370, 160, 370, 160, 120, 0.03, 1), '#f3ecdc', 740, 320), 270, 140, 0.0, { sb: 16 });
      line('A gift for', 100, 176, 0.15, 0);
      line('a gardener', 108, 300, 0.7, 2);
      const bp = prog(0.4, 1.8), ring = circPts(640, 300, 380, 170, 160, 0.03, 1);
      for (let i = 0; i < ring.length * bp; i += 2) { const [x, y] = ring[i], dx = x - 640, dy = y - 300, d = Math.hypot(dx / 380, dy / 170) || 1, ux = dx / 380 / d, uy = dy / 170 / d, n = Math.hypot(ux, uy); fthread(ctx, x - (ux / n) * 14, y - (uy / n) * 14, x + (ux / n) * 2, y + (uy / n) * 2, '#c8443a', 2.6); if (i > 1) fthread(ctx, ring[i - 2][0], ring[i - 2][1], x, y, '#c8443a', 2.6); }
    }

    // ---- BEAT 2 (2.3 to 5.6 s): the three printables sewn on, with tags and stitched plus signs ----
    if (t > 1.9 && t < 6.6) {
      const O = 1280;
      put(pageSpr('year', IMG.year, 250, 350), O + 70, 150, 2.4, { rot: -0.03, sb: 14 });
      put(pageSpr('chart', IMG.chart, 400, 286), O + 420, 180, 2.75, { rot: 0.015, sb: 14 });
      put(pageSpr('seed', IMG.seed, 250, 350), O + 950, 150, 3.1, { rot: 0.03, sb: 14 });
      put(tagSpr('Year Planner', 30), O + 80, 520, 2.75, { rot: -0.04 });
      put(tagSpr('Sowing Chart', 30, '#3f8c86'), O + 515, 500, 3.1, { rot: 0.03 });
      put(tagSpr('Seed Tin Kit', 30, '#c8443a'), O + 960, 520, 3.45, { rot: 0.04 });
      // stitched plus signs between them
      [[O + 365, 300], [O + 870, 300]].forEach(([x, y], i) => { const a = 3.8 + i * 0.35; fsatin(ctx, x - 24 * prog(a, a + 0.15), y, x + 24 * prog(a, a + 0.15), y, '#2f5f9a', 12); fsatin(ctx, x, y - 24 * prog(a + 0.15, a + 0.3), x, y + 24 * prog(a + 0.15, a + 0.3), '#2f5f9a', 12); });
      put(feltText('three', '3 printables', 64, '#2f5f9a', undefined, { back: '#f4ecdc' }), O + 420, 34, 4.5, { sb: 14, rot: -0.02 });
    }

    // ---- BEAT 3 (5.9 to 9.0 s): they go into a felt parcel, then the gift card drops on ----
    if (t > 5.5 && t < 10.0) {
      const O = 2560;
      farrow(ctx, fcurve(O + 20, 330, O + 120, 250, O + 250, 330), '#c8443a', prog(6.0, 6.5));
      put(parcelSpr(), O + 280, 220, 6.2, { sb: 20, sx: 8, sy: 12 });
      put(tagSpr('all in one gift set', 30, '#2f6b4f'), O + 285, 560, 6.6, { rot: -0.03 });
      put(pageSpr('card', IMG.card, 250, 350, '#f3ecdc', '#2f6b4f'), O + 720, 150, 7.2, { rot: 0.04, sb: 16 });
      put(tagSpr('printable gift card', 32, '#c8443a'), O + 700, 585, 7.55, { rot: 0.03 });
      ringSew(O + 845, 325, 190, 230, 7.9, 8.5, 9);
      // a little felt heart pinned to the card corner (emphasis)
      if (t > 8.45) put(feltSpr('heart', Array.from({ length: 60 }, (_, i) => { const a = (i / 60) * TAU, x = 16 * Math.sin(a) ** 3, y = -(13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a)); return [50 + x * 2.6, 46 + y * 2.6]; }), '#d9564a', 100, 92), O + 935, 120, 8.45, { rot: 0.2 });
    }

    // ---- BEAT 4 (9.4 to 12.9 s): buy today, print tonight, give tomorrow, sewn along one thread ----
    if (t > 9.0) {
      const O = 3840, y = 250;
      const steps = [['Buy today', '#2f5f9a', 9.75], ['Print tonight', '#3f8c86', 10.45], ['Give tomorrow', '#c8443a', 11.15]];
      const xs = [O + 40, O + 440, O + 870];
      frun(ctx, [[O + 30, y + 130], [O + 1250, y + 130]], '#3d3548', 14, 7, 3.4, prog(9.6, 11.6));
      steps.forEach(([s, col, st], i) => {
        put(tagSpr(s, 46, col), xs[i], y, st, { rot: [-0.03, 0.02, -0.02][i], sb: 14 });
        if (i < 2) farrow(ctx, [[xs[i] + 330, y + 60], [xs[i + 1] - 20, y + 60]], '#c8443a', prog(st + 0.3, st + 0.65));
      });
      const hot = t > 12.2, bounce = hot ? 1 + 0.16 * Math.sin(prog(12.2, 12.55) * Math.PI) : 1;
      ctx.save(); ctx.translate(O + 640, 470); ctx.scale(bounce, bounce); ctx.translate(-(O + 640), -470);
      const np = feltText('npost' + hot, 'Nothing to post', 84, hot ? '#d9564a' : '#2f5f9a', undefined, { back: '#f4ecdc' });
      put(np, O + 640 - np.w / 2, 420, 11.8, { sb: 18, sx: 6, sy: 10 });
      ctx.restore();
      if (hot) put(feltSpr('star', Array.from({ length: 10 }, (_, i) => { const a = -Math.PI / 2 + (i / 10) * TAU, r = i % 2 ? 26 : 60; return [62 + Math.cos(a) * r, 62 + Math.sin(a) * r]; }), '#e8b04a', 124, 124, (c) => frun(c, Array.from({ length: 11 }, (_, i) => { const a = -Math.PI / 2 + (i / 10) * TAU, r = i % 2 ? 16 : 40; return [62 + Math.cos(a) * r, 62 + Math.sin(a) * r]; }), '#c8443a', 5, 4, 1.8)), O + 1080, 360, 12.2, { rot: 0.1 });
    }
    ctx.restore(); // ======== end world ========

    // header tag (screen space) and takeaway
    put(tagSpr('Plot to Plate with June', 30), 24, 16, 2.25, { rot: -0.02 });
    if (t >= 13.0) {
      const dim = H.clamp((t - 13.0) / 0.4) * 0.35; ctx.fillStyle = `rgba(40,25,15,${dim})`; ctx.fillRect(0, 0, W, H_);
      put(feltSpr('endback', circPts(600, 200, 600, 200, 140, 0.03, 5), '#f3ecdc', 1200, 400), 40, 160, 12.95, { sb: 18 });
      const tg = tagSpr("June's Grow Your Own Gift Set", 50, '#2f6b4f');
      put(tg, 640 - tg.w / 2, 270, 13.1, { sb: 16, rot: -0.01 });
      const t2 = tagSpr('Set for UK gardens  ·  instant download', 32, '#c8443a');
      put(t2, 640 - t2.w / 2, 395, 13.45, { sb: 12, rot: 0.01 });
    }
    // studio light + grain (unchanged from the reference)
    ctx.save(); ctx.globalCompositeOperation = 'soft-light';
    const lg = ctx.createRadialGradient(380 + t * 10, 190, 60, 600, 360, 900); lg.addColorStop(0, 'rgba(255,245,220,0.6)'); lg.addColorStop(1, 'rgba(30,20,10,0.62)');
    ctx.fillStyle = lg; ctx.fillRect(0, 0, W, H_); ctx.restore();
    H.vignette(ctx, W, H_, 0.55, '35,20,10');
    H.grain(ctx, W, H_, 0.025, 6 + Math.floor(t * 12));
  };
  window.DURATION = 15;
  window.explainer = EXPLAIN;
}
