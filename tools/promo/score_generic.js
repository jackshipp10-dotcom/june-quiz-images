// Sound for the Gift Set promo: felt landing on quilted cotton, a needle through felt, buttons, the quilt drawn along.
// Times mirror EXPLAIN() in explain_gift.js (put(): landing at st + 0.2).
window.scoreSound = function (k) {
  const L = 0.2;
  const seg = (t, a, b) => H.ease.inOut(H.clamp((t - a) / (b - a)));
  const cam = (t) => 1280 * seg(t, 2.0, 2.6) + 1280 * seg(t, 5.6, 6.2) + 1280 * seg(t, 9.0, 9.6);
  const pan = (wx, t) => H.clamp(((wx - cam(t)) / 1280) * 2 - 1, -1, 1) * 0.6;
  let seed = 11; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const fump = (t, g = 1, p = 0, minor = true) => {
    k.noise(t, { dur: 0.09, color: 'brown', filter: 'lowpass', f: 420, gain: 0.42 * g, a: 0.006, pan: p, minor });
    k.noise(t, { dur: 0.05, color: 'pink', filter: 'bandpass', f: 700, q: 0.8, gain: 0.1 * g, a: 0.004, pan: p, minor });
    k.tone(t, { f: [[0, 120], [0.07, 70]], dur: 0.09, gain: 0.12 * g, pan: p, minor });
  };
  const pass = (t, g = 1, p = 0, minor = true) => {
    k.noise(t, { dur: 0.025, filter: 'bandpass', f: 800, q: 1.3, gain: 0.26 * g, a: 0.002, pan: p, minor });
    const pd = 0.07 + rnd() * 0.03;
    k.noise(t + 0.03, { dur: pd, filter: 'bandpass', f: [[0, 1400], [pd, 950]], q: 0.9, gain: 0.15 * g, a: pd * 0.6, pan: p, minor });
  };
  const sew = (t0, t1, g, p0, p1) => { for (let t = t0; t < t1 - 0.03; t += 0.115 + rnd() * 0.02) pass(t, g, p0 + (p1 - p0) * ((t - t0) / (t1 - t0))); };
  const button = (t, g = 1, p = 0, minor = true) => { k.play('tock', t, { f: 520, gain: 0.8 * g, pan: p, minor }); k.noise(t, { dur: 0.04, color: 'brown', filter: 'lowpass', f: 500, gain: 0.2 * g, pan: p, minor }); };
  const drag = (t, d, g = 1) => {
    k.noise(t, { dur: d + 0.1, color: 'pink', filter: 'bandpass', f: [[0, 320], [d * 0.5, 700], [d + 0.1, 320]], q: 0.6, gain: 0.1 * g, a: d * 0.45 });
    k.noise(t, { dur: d + 0.1, color: 'brown', filter: 'lowpass', f: 280, gain: 0.075 * g, a: d * 0.5 });
  };

  k.bed('room', 0, 15, { gain: 0.4 });
  k.music('pad', 0.2, 14.8, { bpm: 62, gain: 0.22, chords: [['C3', 'E3', 'G3', 'D4'], ['A2', 'E3', 'G3', 'C4'], ['F2', 'A2', 'C3', 'G3'], ['G2', 'B2', 'D3', 'A3']] });

  // BEAT 1: oval, felt letters, blanket stitch
  fump(0.0 + L, 1.1, 0, false);
  {
    const ts = [];
    [...window.SPEC.hook[0]].forEach((ch, i) => ch !== ' ' && ts.push([0.15 + i * 0.05 + L, i / 10]));
    [...window.SPEC.hook[1]].forEach((ch, i) => ch !== ' ' && ts.push([0.7 + i * 0.05 + L, i / 10]));
    let last = -1; ts.forEach(([t, u]) => { if (t - last >= 0.09) { fump(t, 0.55, (u - 0.5) * 0.8); last = t; } });
  }
  sew(0.4, 1.8, 0.6, -0.4, 0.4);

  // BEAT 2: pan, three pages and their tags, heading
  drag(2.0, 0.6, 1);
  fump(2.25 + L, 0.5, -0.8);
  [0, 1, 2].forEach((i) => { const st = 2.4 + i * 0.35; fump(st + L, 1.15, (i - 1) * 0.45, false); fump(st + 0.35 + L, 0.5, (i - 1) * 0.45); });
  fump(4.4 + L, 1.2, 0, false);

  // BEAT 3: pan, arrow sewn in, hero lands, fact tags, ring, heart
  drag(5.6, 0.6, 0.8);
  sew(6.0, 6.45, 0.7, -0.5, -0.1);
  fump(6.2 + L, 1.4, -0.1, false);
  fump(6.9 + L, 0.6, 0.4); fump(7.4 + L, 0.6, 0.4);
  sew(7.9, 8.5, 0.6, -0.3, 0.3);
  fump(8.45 + L, 0.7, 0.2); k.play('pop', 8.45 + L, { gain: 0.35, pan: 0.2 });

  // BEAT 4: pan, three steps joined by thread arrows, emphasis
  drag(9.0, 0.6, 1);
  sew(9.6, 11.6, 0.25, -0.5, 0.5);
  [0, 1, 2].forEach((i) => { const st = 9.75 + i * 0.7; fump(st + L, 0.85, (i - 1) * 0.5, false); if (i < 2) sew(st + 0.3, st + 0.65, 0.7, (i - 1) * 0.5, (i - 0.5) * 0.5); });
  fump(11.8 + L, 1.2, 0, false);
  k.play('impact', 12.2, { gain: 1.5, pan: 0.1 });
  k.play('ding', 12.2, { f: 'E5', gain: 0.6, pan: 0.2 });
  fump(12.2 + L, 1.5, 0.4, false);

  // BEAT 5: takeaway oval and tags, gentle resolve
  fump(12.95 + L, 1.3, 0, false);
  fump(13.1 + L, 0.7, 0); fump(13.45 + L, 0.6, 0);
  ['C4', 'G4', 'E5'].forEach((f, i) => k.play('ding', 13.75 + i * 0.09, { f, gain: 0.38 - i * 0.03, pan: (i - 1) * 0.25 }));
};
