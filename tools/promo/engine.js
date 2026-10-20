  // ===================== Generic June product promo in Felt & Patchwork (15 s). Content comes from window.SPEC =====================
  const IMG = {};
  window.loadImgs = () => Promise.all(Object.entries(window.IMGS).map(([k, src]) => new Promise((res) => { const im = new Image(); im.onload = () => { IMG[k] = im; res(); }; im.src = src; })));
  const pageSpr = (key, img, w, h, felt = '#f3ecdc', thread = '#c8443a') => feltSpr('pg' + key + w, [[0, 0], [w, 0], [w, h], [0, h]], felt, w, h, (c) => {
    const ins = 16;
    c.save(); c.shadowColor = 'rgba(40,20,10,0.35)'; c.shadowBlur = 4; c.shadowOffsetX = 1.5; c.shadowOffsetY = 2.5;
    c.drawImage(img, ins, ins, w - ins * 2, h - ins * 2); c.restore();
    frun(c, [[7, 7], [w - 7, 7], [w - 7, h - 7], [7, h - 7], [7, 7]], thread, 9, 5, 2.2);
  });
  const starSpr = () => feltSpr('star', Array.from({ length: 10 }, (_, i) => { const a = -Math.PI / 2 + (i / 10) * TAU, r = i % 2 ? 26 : 60; return [62 + Math.cos(a) * r, 62 + Math.sin(a) * r]; }), '#e8b04a', 124, 124, (c) => frun(c, Array.from({ length: 11 }, (_, i) => { const a = -Math.PI / 2 + (i / 10) * TAU, r = i % 2 ? 16 : 40; return [62 + Math.cos(a) * r, 62 + Math.sin(a) * r]; }), '#c8443a', 5, 4, 1.8));
  const heartSpr = () => feltSpr('heart', Array.from({ length: 60 }, (_, i) => { const a = (i / 60) * TAU, x = 16 * Math.sin(a) ** 3, y = -(13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a)); return [50 + x * 2.6, 46 + y * 2.6]; }), '#d9564a', 100, 92);

  const EXPLAIN = (ctx, W, H_, t) => {
    const S = window.SPEC;
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
    const cam = 1280 * seg(2.0, 2.6) + 1280 * seg(5.6, 6.2) + 1280 * seg(9.0, 9.6);
    if (!FX.quilt) {
      const QW = 2560, P = 160, C = H.layer(QW, H_), c = C.getContext('2d'), img = c.createImageData(QW, H_), d = img.data;
      const nz = H.makeNoise(21), r = H.rng(S.quiltSeed || 314), cols = QW / P, rows = Math.ceil(H_ / P) + 1, pick = [];
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

    ctx.save(); ctx.translate(-cam, 0);

    // BEAT 1 (0 to 2 s): hook in felt letters on a cream oval, blanket stitch sewn round
    {
      const cols = ['#d9564a', '#2f5f9a', '#e8b04a', '#3f8c86', '#c8443a'];
      const line = (str, px, y, st, off) => {
        const m = H.layer(4, 4).getContext('2d'); m.font = `700 ${px}px "Fredoka"`;
        let x = 640 - (m.measureText(str).width + str.length * 6) / 2, i = 0;
        for (const ch of str) { const w = m.measureText(ch).width; if (ch !== ' ') put(feltText('L' + ch + px + (i + off) % 5, ch, px, cols[(i + off) % 5]), x, y, st + i * 0.05, { rot: (H.rng(i + off)() - 0.5) * 0.12 }); x += w + 6; i++; }
      };
      const [h1, h2] = S.hook, px = S.hookPx || 100;
      put(feltSpr('b1back', circPts(420, 170, 420, 170, 120, 0.03, 1), '#f3ecdc', 840, 340), 220, 130, 0.0, { sb: 16 });
      line(h1, px, 176, 0.15, 0);
      line(h2, px, 300, 0.7, 2);
      const bp = prog(0.4, 1.8), ring = circPts(640, 300, 430, 180, 160, 0.03, 1);
      for (let i = 0; i < ring.length * bp; i += 2) { const [x, y] = ring[i], dx = x - 640, dy = y - 300, d = Math.hypot(dx / 430, dy / 180) || 1, ux = dx / 430 / d, uy = dy / 180 / d, n = Math.hypot(ux, uy); fthread(ctx, x - (ux / n) * 14, y - (uy / n) * 14, x + (ux / n) * 2, y + (uy / n) * 2, '#c8443a', 2.6); if (i > 1) fthread(ctx, ring[i - 2][0], ring[i - 2][1], x, y, '#c8443a', 2.6); }
    }

    // BEAT 2 (2.3 to 5.5 s): three real pages sewn on with woven tags, then a felt heading
    if (t > 1.9 && t < 6.6) {
      const O = 1280;
      S.pages.forEach((pg, i) => {
        const st = 2.4 + i * 0.35;
        put(pageSpr(pg.img, IMG[pg.img], pg.w, pg.h), O + pg.x, pg.y, st, { rot: [-0.03, 0.015, 0.03][i], sb: 14 });
        const tg = tagSpr(pg.tag, 30, ['#2f5f9a', '#3f8c86', '#c8443a'][i]);
        put(tg, O + pg.x + pg.w / 2 - tg.w / 2, pg.y + pg.h + 22, st + 0.35, { rot: [-0.04, 0.03, 0.04][i] });
      });
      const hd = feltText('head', S.heading, 64, '#2f5f9a', undefined, { back: '#f4ecdc' });
      put(hd, O + 640 - hd.w / 2, 34, 4.4, { sb: 14, rot: -0.02 });
    }

    // BEAT 3 (5.9 to 9.0 s): the hero close up, ringed in thread, with two fact tags
    if (t > 5.5 && t < 10.0) {
      const O = 2560, hr = S.hero, hx0 = O + hr.x, hy0 = hr.y;
      farrow(ctx, fcurve(O + 20, 330, O + 80, 260, hx0 - 20, 330), '#c8443a', prog(6.0, 6.45));
      put(pageSpr('hero' + hr.img, IMG[hr.img], hr.w, hr.h, '#f3ecdc', '#2f6b4f'), hx0, hy0, 6.2, { rot: 0.02, sb: 18, sx: 8, sy: 12 });
      ringSew(hx0 + hr.w / 2, hy0 + hr.h / 2, hr.w * 0.62, hr.h * 0.62, 7.9, 8.5, 9);
      S.facts.forEach((f, i) => { const tg = tagSpr(f, 36, ['#2f6b4f', '#c8443a'][i]); put(tg, O + hr.fx, hr.fy + i * 110, 6.9 + i * 0.5, { rot: [-0.03, 0.03][i], sb: 12 }); });
      if (t > 8.45) put(heartSpr(), hx0 + hr.w - 70, hy0 - 40, 8.45, { rot: 0.2 });
    }

    // BEAT 4 (9.4 to 12.9 s): three steps along one thread, then the emphasis line
    if (t > 9.0) {
      const O = 3840, y = 250;
      const steps = S.steps.map((s, i) => [s, ['#2f5f9a', '#3f8c86', '#c8443a'][i], 9.75 + i * 0.7]);
      const m = H.layer(4, 4).getContext('2d'); m.font = '700 46px "Fredoka"';
      const raw = steps.reduce((a, [s]) => a + m.measureText(s).width + 46 * 1.4 + 20, 0), SP = Math.max(34, Math.min(46, Math.floor(46 * 1020 / raw)));
      m.font = `700 ${SP}px "Fredoka"`;
      const ws = steps.map(([s]) => m.measureText(s).width + SP * 1.4 + 20), gap = (1180 - ws.reduce((a, b) => a + b, 0)) / 2;
      const xs = [O + 50, O + 50 + ws[0] + gap, O + 50 + ws[0] + ws[1] + gap * 2];
      frun(ctx, [[O + 30, y + 130], [O + 1250, y + 130]], '#3d3548', 14, 7, 3.4, prog(9.6, 11.6));
      steps.forEach(([s, col, st], i) => {
        put(tagSpr(s, SP, col), xs[i], y, st, { rot: [-0.03, 0.02, -0.02][i], sb: 14 });
        if (i < 2) farrow(ctx, [[xs[i] + ws[i] + 4, y + 50], [xs[i + 1] - 14, y + 50]], '#c8443a', prog(st + 0.3, st + 0.65));
      });
      const hot = t > 12.2, bounce = hot ? 1 + 0.16 * Math.sin(prog(12.2, 12.55) * Math.PI) : 1;
      ctx.save(); ctx.translate(O + 640, 470); ctx.scale(bounce, bounce); ctx.translate(-(O + 640), -470);
      const np = feltText('emph' + hot, S.emphasis, S.emphPx || 84, hot ? '#d9564a' : '#2f5f9a', undefined, { back: '#f4ecdc' });
      put(np, O + 640 - np.w / 2, 420, 11.8, { sb: 18, sx: 6, sy: 10 });
      ctx.restore();
      if (hot) put(starSpr(), O + 640 + np.w / 2 - 10, 360, 12.2, { rot: 0.1 });
    }
    ctx.restore();

    put(tagSpr('Plot to Plate with June', 30), 24, 16, 2.25, { rot: -0.02 });
    if (t >= 12.9) {
      const dim = H.clamp((t - 13.0) / 0.4) * 0.35; ctx.fillStyle = `rgba(40,25,15,${dim})`; ctx.fillRect(0, 0, W, H_);
      put(feltSpr('endback', circPts(600, 200, 600, 200, 140, 0.03, 5), '#f3ecdc', 1200, 400), 40, 160, 12.95, { sb: 18 });
      const tg = tagSpr(S.title, S.titlePx || 50, '#2f6b4f');
      put(tg, 640 - tg.w / 2, 270, 13.1, { sb: 16, rot: -0.01 });
      const t2 = tagSpr(S.subtitle, 32, '#c8443a');
      put(t2, 640 - t2.w / 2, 395, 13.45, { sb: 12, rot: 0.01 });
    }
    ctx.save(); ctx.globalCompositeOperation = 'soft-light';
    const lg = ctx.createRadialGradient(380 + t * 10, 190, 60, 600, 360, 900); lg.addColorStop(0, 'rgba(255,245,220,0.6)'); lg.addColorStop(1, 'rgba(30,20,10,0.62)');
    ctx.fillStyle = lg; ctx.fillRect(0, 0, W, H_); ctx.restore();
    H.vignette(ctx, W, H_, 0.55, '35,20,10');
    H.grain(ctx, W, H_, 0.025, 6 + Math.floor(t * 12));
  };
  window.DURATION = 15;
  window.explainer = EXPLAIN;
  // vertical (9:16) caption overlay drawn with the same felt tags: title on top, "Link in bio" below
  window.overlay = (ctx) => {
    const S = window.SPEC;
    ctx.save(); const sc = 1080 / 1280; ctx.scale(sc, sc);
    const W = 1280, top = tagSpr(S.title, S.vTitlePx || 58, '#2f6b4f'), bot = tagSpr('Link in bio', 54, '#c8443a');
    const draw = (spr, x, y, rot) => { ctx.save(); ctx.shadowColor = 'rgba(40,20,10,0.5)'; ctx.shadowBlur = 16; ctx.shadowOffsetY = 8; ctx.translate(x + spr.w / 2, y + spr.h / 2); ctx.rotate(rot); ctx.drawImage(spr, -spr.w / 2 - spr.pad, -spr.h / 2 - spr.pad); ctx.restore(); };
    draw(top, W / 2 - top.w / 2, 330, -0.02); draw(bot, W / 2 - bot.w / 2, 1760, 0.02);
    ctx.restore();
  };
}
