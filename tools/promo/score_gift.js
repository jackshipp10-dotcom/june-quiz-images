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
    [...'A gift for'].forEach((ch, i) => ch !== ' ' && ts.push([0.15 + i * 0.06 + L, i / 10]));
    [...'a gardener'].forEach((ch, i) => ch !== ' ' && ts.push([0.7 + i * 0.06 + L, i / 10]));
    let last = -1; ts.forEach(([t, u]) => { if (t - last >= 0.09) { fump(t, 0.55, (u - 0.5) * 0.8); last = t; } });
  }
  sew(0.4, 1.8, 0.6, -0.4, 0.4);

  // BEAT 2: pan, three products and their tags, plus signs, heading
  drag(2.0, 0.6, 1);
  fump(2.25 + L, 0.5, -0.8);
  [[2.4, 1475], [2.75, 1900], [3.1, 2355]].forEach(([st, x]) => fump(st + L, 1.15, pan(x, st + L), false));
  [[2.75, 1430], [3.1, 1900], [3.45, 2350]].forEach(([st, x]) => fump(st + L, 0.5, pan(x, st + L)));
  sew(3.8, 4.1, 0.6, pan(1645, 3.8), pan(1645, 4.1)); sew(4.15, 4.45, 0.6, pan(2150, 4.15), pan(2150, 4.45));
  fump(4.5 + L, 1.2, pan(1900, 4.7), false);

  // BEAT 3: pan, arrow into the parcel, gift card, ring, heart
  drag(5.6, 0.6, 0.8);
  sew(6.0, 6.5, 0.7, pan(2580, 6.0), pan(2810, 6.5));
  fump(6.2 + L, 1.4, pan(2990, 6.4), false); button(6.2 + L + 0.05, 0.4, pan(2990, 6.45));
  fump(6.6 + L, 0.5, pan(2990, 6.8));
  fump(7.2 + L, 1.1, pan(3405, 7.4), false);
  fump(7.55 + L, 0.5, pan(3405, 7.75));
  sew(7.9, 8.5, 0.6, pan(3220, 7.9), pan(3600, 8.5));
  fump(8.45 + L, 0.7, pan(3545, 8.65)); k.play('pop', 8.45 + L, { gain: 0.35, pan: pan(3545, 8.65) });

  // BEAT 4: pan, three steps joined by thread arrows
  drag(9.0, 0.6, 1);
  sew(9.6, 11.6, 0.25, pan(3900, 9.6), pan(5000, 11.6));
  [[9.75, 4000], [10.45, 4440], [11.15, 4870]].forEach(([st, x], i) => {
    fump(st + L, 0.85, pan(x, st + L), false);
    if (i < 2) sew(st + 0.3, st + 0.65, 0.7, pan(x + 330, st + 0.3), pan(x + 420, st + 0.65));
  });
  fump(11.8 + L, 1.2, pan(4480, 12.0), false);
  // "Nothing to post" turns red and bounces, felt star lands: the biggest hit
  k.play('impact', 12.2, { gain: 1.5, pan: 0.1 });
  k.play('ding', 12.2, { f: 'E5', gain: 0.6, pan: 0.2 });
  fump(12.2 + L, 1.5, pan(4980, 12.4), false);

  // BEAT 5: takeaway oval and tags, gentle resolve
  fump(12.95 + L, 1.3, 0, false);
  fump(13.1 + L, 0.7, 0); fump(13.45 + L, 0.6, 0);
  ['C4', 'G4', 'E5'].forEach((f, i) => k.play('ding', 13.75 + i * 0.09, { f, gain: 0.38 - i * 0.03, pan: (i - 1) * 0.25 }));
};
