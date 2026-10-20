const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const { spawn } = require('child_process'); const fs = require('fs');
(async () => {
  const [mode, prod, ...ts] = process.argv.slice(2), D = 15, FPS = 30, out = __dirname + '/' + prod + '/';
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('err:', e.message));
  await p.goto('file://' + __dirname + '/render.html?p=' + prod); await p.evaluate(() => window.ready);
  if (mode === 'stills') { for (const t of ts) { const d = await p.evaluate((t) => window.frame(+t), t); fs.writeFileSync(out + 's_' + t + '.jpg', Buffer.from(d.split(',')[1], 'base64')); } }
  if (mode === 'overlay') { const d = await p.evaluate(() => window.ov()); fs.writeFileSync(out + 'overlay.png', Buffer.from(d.split(',')[1], 'base64')); }
  if (mode === 'video') {
    const d = await p.evaluate(() => window.ov()); fs.writeFileSync(out + 'overlay.png', Buffer.from(d.split(',')[1], 'base64'));
    const a = await p.evaluate(() => window.audio()); fs.writeFileSync(out + 'audio.f32', Buffer.from(a.b64, 'base64')); console.log(prod, 'audio peak', a.peak.toFixed(2));
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', out + 'master.mp4'], { stdio: ['pipe', 'ignore', 'inherit'] });
    for (let i = 0; i < D * FPS; i++) { const d = await p.evaluate((t) => window.frame(t), i / FPS); if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r)); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); console.log(prod, 'frames done');
  }
  await b.close();
})();
