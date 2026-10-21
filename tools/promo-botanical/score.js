// Sound for the Botanical Plate promos: a nib on rag paper, prints laid down, a brush wash, pages turned along. Times mirror bengine.js.
window.scoreSound = function (k) {
  let seed = 23; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  // nib scratch: a run of tiny high, dry strokes
  const nib = (t0, t1, g = 1, p = 0) => { for (let t = t0; t < t1; t += 0.05 + rnd() * 0.05) { const d = 0.03 + rnd() * 0.05; k.noise(t, { dur: d, filter: 'bandpass', f: 3800 + rnd() * 2400, q: 2.2, gain: 0.11 * g * (0.6 + rnd() * 0.6), a: d * 0.3, pan: p + (rnd() - 0.5) * 0.15, minor: true }); } };
  // a print laid on paper: a soft papery pat
  const lay = (t, g = 1, p = 0) => { k.noise(t, { dur: 0.12, color: 'pink', filter: 'lowpass', f: 1500, gain: 0.32 * g, a: 0.004, pan: p }); k.noise(t, { dur: 0.06, color: 'brown', filter: 'lowpass', f: 300, gain: 0.25 * g, a: 0.003, pan: p }); };
  // brush wash: a short wet swish
  const brush = (t, d = 0.5, g = 1, p = 0) => k.noise(t, { dur: d, color: 'pink', filter: 'bandpass', f: [[0, 900], [d * 0.6, 1900], [d, 1200]], q: 0.7, gain: 0.09 * g, a: d * 0.4, pan: p, minor: true });
  // the sheet slides along to the next plate
  const turn = (t, d = 0.6, g = 1) => { k.noise(t, { dur: d + 0.1, color: 'pink', filter: 'bandpass', f: [[0, 600], [d * 0.5, 2600], [d + 0.1, 900]], q: 0.5, gain: 0.13 * g, a: d * 0.4 }); k.noise(t + d * 0.15, { dur: 0.25, filter: 'highpass', f: 4500, gain: 0.05 * g, a: 0.08 }); };

  k.bed('room', 0, 15, { gain: 0.3 });
  k.music('pad', 0.1, 14.9, { bpm: 60, gain: 0.2, chords: [['F2', 'C3', 'A3', 'E4'], ['D2', 'A2', 'F3', 'C4'], ['A#1', 'F2', 'D3', 'A3'], ['C2', 'G2', 'E3', 'D4']] });
  // a few music box notes across the piece
  [[0.3, 'A4'], [1.1, 'C5'], [2.5, 'F5'], [4.5, 'E5'], [6.3, 'C5'], [8.5, 'D5'], [10.0, 'A4'], [11.4, 'C5']].forEach(([t, f]) => k.play('ding', t, { f, gain: 0.16, pan: (rnd() - 0.5) * 0.5 }));

  // PLATE I: the plant is engraved, tinted; the hook is printed
  nib(0.05, 0.7, 1, -0.4); nib(0.25, 1.3, 0.7, -0.35); brush(0.6, 0.6, 1, -0.4); brush(1.05, 0.7, 0.8, -0.3);
  nib(0.2, 0.6, 0.5, 0.2); brush(1.0, 0.6, 0.9, 0.2);

  // PLATE II
  turn(2.0, 0.6, 1);
  [0, 1, 2].forEach((i) => { const st = 2.4 + i * 0.35; lay(st + 0.25, 0.9, (i - 1) * 0.5); nib(st + 0.3, st + 0.75, 0.6, (i - 1) * 0.5); });
  nib(4.7, 5.0, 0.7, 0);

  // PLATE III
  turn(5.6, 0.6, 0.9);
  brush(6.0, 0.8, 1, -0.3); lay(6.45, 1.2, -0.2);
  [0, 1].forEach((i) => nib(6.9 + i * 0.5, 7.25 + i * 0.5, 0.6, 0.4));
  nib(7.9, 8.6, 0.6, 0.5); brush(8.25, 0.5, 0.8, 0.5); nib(8.4, 8.8, 0.5, -0.1); brush(8.65, 0.4, 0.6, 0);

  // PLATE IV: the vine grows through three roundels, then the emphasis
  turn(9.0, 0.6, 1);
  nib(9.6, 11.6, 0.35, 0);
  [0, 1, 2].forEach((i) => { const st = 9.75 + i * 0.7; lay(st + 0.15, 0.7, (i - 1) * 0.5); nib(st, st + 0.4, 0.7, (i - 1) * 0.5); brush(st + 0.3, 0.45, 0.6, (i - 1) * 0.5); });
  brush(11.9, 0.6, 1.1, 0);
  k.play('ding', 12.2, { f: 'A5', gain: 0.45, pan: 0.2 }); k.play('ding', 12.32, { f: 'F5', gain: 0.32, pan: -0.1 });
  lay(12.2, 0.8, 0.1); brush(12.25, 0.5, 0.9, 0.4);

  // END: the label is pasted down and engraved
  lay(13.1, 1.3, 0); nib(13.0, 13.7, 0.6, 0); brush(13.45, 0.5, 0.6, -0.3); brush(13.5, 0.5, 0.6, 0.3);
  ['F4', 'C5', 'A5'].forEach((f, i) => k.play('ding', 13.8 + i * 0.12, { f, gain: 0.32 - i * 0.04, pan: (i - 1) * 0.25 }));
};
