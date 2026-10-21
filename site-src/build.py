"""Build June's website from the JSON in site-src/data into site/ (static files for Cloudflare Pages).

Run:  python3 site-src/build.py
Edit content in data/month.json (monthly), data/products.json (shop) and data/site.json (links).
"""
import json, os, html
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(ROOT), "site")
SITE = json.load(open(os.path.join(ROOT, "data/site.json")))
MONTH = json.load(open(os.path.join(ROOT, "data/month.json")))
PRODUCTS = [p for p in json.load(open(os.path.join(ROOT, "data/products.json")))["products"]]


def _smart(o, key=""):
    """Curly apostrophes in visible copy (not in urls or file names)."""
    if isinstance(o, dict):
        return {k: _smart(v, k) for k, v in o.items()}
    if isinstance(o, list):
        return [_smart(v, key) for v in o]
    if isinstance(o, str) and key not in ("url", "image", "anchor", "key", "slug", "payhip_code", "platform", "id", "calendar_image"):
        return o.replace("'", "\u2019")
    return o


MONTH = _smart(MONTH)
PRODUCTS = _smart(PRODUCTS)
e = html.escape


def quiz(medium, campaign, space=None):
    q = f"{SITE['quiz_url']}?utm_source=website&utm_medium={medium}&utm_campaign={campaign}"
    return q + (f"&space={space}" if space else "")


def page(path, title, desc, body, current=None, payhip=False, form=False, noindex=False):
    canon = SITE["domain"] + "/" + (path if path != "index.html" else "")
    canon = canon.replace("index.html", "")
    nav = [("Free quiz", "/quiz"), ("This month", "/this-month/"), ("Shop", "/shop/")]
    navhtml = "".join(f'<a href="{u}"{" aria-current=\"page\"" if current == u else ""}>{n}</a>' for n, u in nav)
    social = "".join(f'<a href="{s["url"]}" rel="me noopener" target="_blank">{s["name"]}</a>' for s in SITE["social"])
    scripts = ""
    head_js = '<script>window.PayhipConfig={enableCart:true};</script><script type="text/javascript" src="https://payhip.com/payhip.js"></script>' if payhip else ""
    if False:
        pass
    if form:
        scripts += f"<script>{FORM_JS}</script>"
    doc = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{"<meta name=\"robots\" content=\"noindex\">" if noindex else f'<link rel="canonical" href="{canon}">'}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="en_GB">
<meta property="og:image" content="{SITE['domain']}/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2E4733">
<link rel="icon" type="image/png" href="/img/favicon.png">
<link rel="apple-touch-icon" href="/img/icon-180.png">
<link rel="preload" href="/assets/fonts/zilla-slab-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/work-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
{head_js}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap"><a class="logo" href="/">{e(SITE['name'])}</a><nav class="nav" aria-label="Main">{navhtml}</nav></div></header>
<main id="main">
{body}
</main>
<footer class="site-foot"><div class="wrap">
<nav class="foot-links" aria-label="Footer"><a href="{quiz('footer','quiz')}">Free quiz</a><a href="/this-month/">This month</a><a href="/shop/">Shop</a><a href="/test/">Gardener Level Test</a><a href="/privacy/">Privacy</a></nav>
<div class="foot-social">{social}</div>
<p class="foot-note">Questions? Email <a href="mailto:{SITE['contact_email']}">{SITE['contact_email']}</a>. <a href="/privacy/#seller">Seller details</a>. Growing advice follows general UK guidance; check your seed packets for your variety. &copy; {date.today().year} {e(SITE['name'])}</p>
</div></footer>
{scripts}
</body>
</html>
"""
    dest = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w", encoding="utf-8").write(doc)


FORM_JS = r"""
document.querySelectorAll('form[data-ml]').forEach(function(f){
  f.addEventListener('submit',function(ev){
    ev.preventDefault();
    var msg=f.querySelector('.msg'), btn=f.querySelector('button');
    if(!f.querySelector('[name=consent]').checked){msg.textContent='Tick the box so I can email you.';return;}
    btn.disabled=true; msg.textContent='Sending...';
    fetch(f.action,{method:'POST',body:new FormData(f),mode:'no-cors'}).then(function(){
      msg.textContent='Nearly there. Check your inbox and tap the button in my email to confirm, and your calendar comes straight over.';
    }).catch(function(){msg.textContent='That didn’t send. Check your connection and try again.';btn.disabled=false;});
  });
});
"""


def packets(medium):
    out = []
    for s in MONTH["spaces"]:
        out.append(f'<a class="pk" href="{quiz(medium, "quiz_packets", s["key"])}"><img src="/img/space-{s["key"]}.jpg" alt="" width="240" height="240" loading="eager"><span>{e(s["name"])}</span></a>')
    return '<div class="packets">' + "".join(out) + "</div>"


def buy_button(p):
    if p["platform"] == "payhip":
        c = p["payhip_code"]
        return f'<a href="https://payhip.com/b/{c}" class="payhip-add-to-cart-button btn" data-theme="none" data-product="{c}">Add to basket</a>'
    return f'<a href="{p["url"]}" class="btn" target="_blank" rel="noopener">Buy on Etsy</a>'


def product_card(p, cls="prod", details=False, heading="h3"):
    url = f"/shop/{p['id']}/"
    extra = ""
    if details and p.get("detail"):
        extra = "<ul>" + "".join(f"<li>{e(d)}</li>" for d in p["detail"]) + "</ul>"
    more = f'<a class="more" href="{url}">See inside</a>' if cls == "shop-item" else ""
    return (f'<article class="{cls}"><a class="cover" href="{url}" tabindex="-1" aria-hidden="true"><img src="/img/{p["image"]}" alt="" width="280" height="396" loading="lazy"></a>'
            f'<{heading}><a href="{url}">{e(p["name"])}</a></{heading}><p>{e(p["line"])}</p>{extra}'
            f'<div class="buy">{price_html(p)}{buy_button(p)}</div>{more}</article>')


def price_html(p):
    # Optional sale: set "was_price" in products.json (e.g. "£12") and "price" to the sale price.
    if p.get("was_price"):
        return (f'<span class="price"><span class="sr">Was </span><s class="was">{e(p["was_price"])}</s> '
                f'<span class="sr">now </span>{e(p["price"])}</span>')
    return f'<span class="price">{e(p["price"])}</span>'


def calstrip():
    return (f'<div class="calstrip"><img src="/img/{MONTH["calendar_image"]}" alt="" width="64" height="96" loading="lazy">'
            f'<p>My one page sowing calendar for {MONTH["month"]}</p><a class="btn" href="/this-month/#calendar">Get it free by email</a></div>')


def videos():
    items = "".join(f'<a href="{v["url"]}" target="_blank" rel="noopener"><img src="/img/{v["image"]}" alt="" width="200" height="311" loading="lazy"><span>{e(v["title"])}</span></a>' for v in MONTH["videos"])
    return f'<div class="videos">{items}</div>'


# ---------- Home ----------
featured = [p for p in PRODUCTS if p.get("featured")]
prod_cls = "products swipe" if len(featured) >= 3 else "products"
home = f"""
<section class="section wrap" aria-labelledby="quiz-h">
  <h1 id="quiz-h" class="h-home">What can you grow?</h1>
  <p class="lede">Pick your space for my free quiz. It takes a minute, and there’s a recipe at the end.</p>
  {packets('home')}
  <p class="quiz-go"><a class="btn" href="{quiz('home','quiz_button')}">Take the free quiz</a></p>
</section>
<div class="wrap home-cols">
  <section class="section" aria-labelledby="month-h">
    <div class="section-head"><h2 id="month-h">This month</h2><a class="btn-outline" href="/this-month/">All of {MONTH['month']}</a></div>
    <div class="cards3">{''.join(f'<a class="pcard" href="/this-month/#{c["anchor"]}"><img src="/img/{c["image"]}" alt="" width="200" height="200" loading="lazy"><b>{e(c["label"])}</b><span>{e(c["text"])}</span></a>' for c in MONTH['home_cards'])}</div>
    <div class="after-cards"><a class="btn btn-paper btn-block" href="/this-month/#calendar">Get my free {MONTH['month']} calendar by email</a></div>
  </section>
  <section class="section" aria-labelledby="shop-h">
    <div class="section-head"><h2 id="shop-h">My planners</h2><a class="btn-outline" href="/shop/">Visit the shop</a></div>
    <div class="{prod_cls}">{''.join(product_card(p) for p in featured)}</div>
  </section>
</div>
<section class="section wrap" aria-labelledby="vid-h">
  <div class="section-head"><h2 id="vid-h">Latest from my garden</h2><a class="btn-outline" href="https://www.youtube.com/channel/UC1bVDsqIYnrKo_AoTm29bSQ" target="_blank" rel="noopener">YouTube</a></div>
  {videos()}
</section>
"""
page("index.html", "Plot to Plate with June | Grow your own veg in the UK",
     "Find out what you can grow in your space with June's free quiz, see what to sow and cook this month, and get her free UK sowing calendar.",
     home, payhip=True)


# ---------- This month ----------
def items(lst):
    return '<div class="grid2">' + "".join(
        f'<article class="item"><img src="/img/{i["image"]}" alt="" width="300" height="300" loading="lazy"><div><h3>{e(i["name"])}</h3><p>{e(i["note"])}</p></div></article>' for i in lst) + "</div>"


picks = '<div class="picks">' + "".join(f'<figure><img src="/img/{i["image"]}" alt="" width="240" height="240" loading="lazy"><figcaption>{e(i["name"])}</figcaption></figure>' for i in MONTH["pick"]) + "</div>"
spaces = '<div class="spaces">' + "".join(
    f'<a class="pk" href="{quiz("this_month", "spaces", s["key"])}"><img src="/img/space-{s["key"]}.jpg" alt="" width="240" height="240" loading="lazy"><span>{e(s["name"])}</span><p>{e(s["tip"])}</p><em>Take the quiz</em></a>' for s in MONTH["spaces"]) + "</div>"
r = MONTH["recipe"]
form_html = ""
cf = SITE["calendar_form"]
if cf.get("action"):
    form_html = f"""<form data-ml action="{cf['action']}" method="post">
  <label for="cal-email">Your email address</label>
  <input id="cal-email" type="email" name="fields[email]" autocomplete="email" required placeholder="you@example.com">
  <label class="consent"><input type="checkbox" name="consent" value="1"> <span>{e(cf['consent'])} See my <a href="/privacy/">privacy notice</a>.</span></label>
  <input type="hidden" name="ml-submit" value="1"><input type="hidden" name="anticsrf" value="true">
  <button class="btn" type="submit">Email me the calendar</button>
  <p class="msg" role="status" aria-live="polite"></p>
</form>"""
tm = f"""
<section class="page-hero wrap">
  <h1>{MONTH['month']} in the garden</h1>
  <p>{e(MONTH['intro'])}</p>
  <blockquote class="quote">“{e(MONTH['quote'])}”</blockquote>
</section>
<section class="section wrap" id="calendar" aria-labelledby="cal-h">
  <div class="signup">
    <div class="row"><img src="/img/{MONTH['calendar_image']}" alt="June's {MONTH['month']} sowing calendar" width="84" height="126"><div><h2 id="cal-h">My free {MONTH['month']} calendar</h2><p class="small">One page: what to sow, plant, pick and cook, week by week.</p><p class="small" style="margin-top:8px">Pop your email in below and I'll send it straight over, then a new one at the start of every month.</p></div></div>{form_html}
  </div>
</section>
<section class="section wrap" id="sow" aria-labelledby="sow-h"><div class="section-head"><h2 id="sow-h">Sow this month</h2></div>{items(MONTH['sow'])}</section>
<section class="section wrap" id="plant" aria-labelledby="plant-h"><div class="section-head"><h2 id="plant-h">Plant this month</h2></div>{items(MONTH['plant'])}</section>
<section class="section wrap" id="pick" aria-labelledby="pick-h"><div class="section-head"><h2 id="pick-h">Pick now</h2></div>{picks}<p class="also">Also ready: {e(MONTH['pick_also'])}.</p></section>
<section class="section wrap" id="space" aria-labelledby="space-h"><div class="section-head"><h2 id="space-h">Your space this month</h2></div><p class="lede">One job for each kind of grower. Not sure which you are? Tap yours for the quiz.</p>{spaces}</section>
<section class="section wrap" id="cook" aria-labelledby="cook-h"><div class="section-head"><h2 id="cook-h">Cook it</h2></div>
  <article class="recipe"><img src="/img/{r['image']}" alt="{e(r['title'])}" width="380" height="475" loading="lazy"><div class="body"><h3>{e(r['title'])}</h3><p class="serves">{e(r['serves'])}</p>
  <h4>You’ll need</h4><ul>{''.join(f'<li>{e(i)}</li>' for i in r['ingredients'])}</ul>
  <h4>Method</h4><ol>{''.join(f'<li>{e(s)}</li>' for s in r['steps'])}</ol></div></article></section>
<section class="section wrap" id="jobs" aria-labelledby="jobs-h"><div class="section-head"><h2 id="jobs-h">Jobs to tick off</h2></div><ul class="jobs">{''.join(f'<li>{e(j)}</li>' for j in MONTH['jobs'])}</ul></section>
<section class="section wrap" aria-labelledby="vid-h"><div class="section-head"><h2 id="vid-h">Latest from my garden</h2><a class="btn-outline" href="https://www.youtube.com/channel/UC1bVDsqIYnrKo_AoTm29bSQ" target="_blank" rel="noopener">YouTube</a></div>{videos()}</section>
"""
page("this-month/index.html", f"What to sow, plant and cook in {MONTH['month']} (UK) | Plot to Plate with June",
     f"June's UK guide to {MONTH['month']}: what to sow, plant and pick, one job for every kind of space, a seasonal recipe and her free sowing calendar.",
     tm, current="/this-month/", form=bool(cf.get("action")))


# ---------- Shop ----------
shop = f"""
<section class="page-hero wrap">
  <h1>My shop</h1>
  <p>Planners and printables written for UK gardens, windowsills and allotments. Instant download, print at home as often as you like.</p>
</section>
<section class="section wrap" aria-label="Products">
  <div class="shop-grid">{''.join(product_card(p, cls='shop-item', heading='h2') for p in PRODUCTS)}</div>
</section>
<section class="section wrap">
  <div class="notice"><p><b>Not sure where to start?</b> My free quiz tells you what to grow in your space, and which planner suits you.</p><a class="btn" href="{quiz('shop','quiz')}">Take the free quiz</a></div>
  <p class="foot-note" style="margin-top:14px">Sold by {e(SITE['seller']['trading_as'])} (<a href="/privacy/#seller">seller details</a>). Add what you want to your basket, then check out once. Checkout is handled securely by Payhip, which emails your downloads straight away. These are digital downloads, so nothing is posted, and your 14 day right to cancel ends once the download starts.</p>
</section>
"""
page("shop/index.html", "Printable UK veg growing planners | Plot to Plate with June",
     "June's printable planners, sowing charts, seed kit and gift set for UK veg growers. Instant download, print at home.",
     shop, current="/shop/", payhip=True)


# ---------- Product pages ----------
GALLERY_JS = r"""
document.querySelectorAll('.gallery').forEach(function(g){
  var stage=g.querySelector('.stage'), items=[].slice.call(stage.children), thumbs=[].slice.call(g.querySelectorAll('.thumbs button'));
  function mark(i){
    thumbs.forEach(function(t,k){t.setAttribute('aria-current',k===i?'true':'false');});if(thumbs[i]){var s=thumbs[i].parentNode;s.scrollTo({left:thumbs[i].offsetLeft-s.offsetLeft-(s.clientWidth-thumbs[i].offsetWidth)/2,behavior:'smooth'});}
    items.forEach(function(it,k){var v=it.querySelector('video');if(v){if(k===i){v.play().catch(function(){});}else{v.pause();}}});
  }
  thumbs.forEach(function(t,i){t.addEventListener('click',function(){stage.scrollTo({left:items[i].offsetLeft-stage.offsetLeft,behavior:'smooth'});mark(i);});});
  var tid;stage.addEventListener('scroll',function(){clearTimeout(tid);tid=setTimeout(function(){mark(Math.round(stage.scrollLeft/stage.clientWidth));},80);},{passive:true});
});
"""


def product_page(p):
    pg = p["page"]
    pid = p["id"]
    url = f"/shop/{pid}/"
    n = pg["gallery"]
    vid = (f'<div class="slide"><video src="/video/{p["video"]}" poster="/video/{pid}.jpg" muted loop playsinline preload="none" aria-label="A 15 second look at the {e(p["name"][4:] if p["name"].startswith("The ") else p["name"])}" controls></video></div>',
           f'<button type="button" aria-label="Play the video" aria-current="false"><img src="/video/{pid}.jpg" alt="" width="160" height="90" loading="lazy"><span class="play" aria-hidden="true"></span></button>') if p.get("video") else None
    slides = [f'<div class="slide"><img src="/img/products/{pid}/{i:02d}.jpg" alt="{e(p["name"])}, picture {i} of {n}" width="1000" height="1000"{"" if i == 1 else ' loading="lazy"'}></div>' for i in range(1, n + 1)]
    thumbs = [f'<button type="button" aria-label="Show picture {i}" aria-current="{"true" if i == 1 else "false"}"><img src="/img/products/{pid}/{i:02d}-t.jpg" alt="" width="160" height="160" loading="lazy"></button>' for i in range(1, n + 1)]
    if vid:
        slides.insert(1, vid[0]); thumbs.insert(1, vid[1])
    secs = ""
    for sec in pg["sections"]:
        tag = "ol" if len(sec) > 2 and sec[2] == "ol" else "ul"
        secs += f'<h2>{e(sec[0])}</h2><{tag}>' + "".join(f"<li>{e(x)}</li>" for x in sec[1]) + f"</{tag}>"
    if pg.get("note"):
        secs += f'<p class="note">{e(pg["note"])}</p>'
    if pg.get("more"):
        q, other, txt = pg["more"]
        op = next(x for x in PRODUCTS if x["id"] == other)
        secs += f'<p class="cross"><b>{e(q)}</b> {e(txt)} <a href="/shop/{other}/">See the {e(op["name"])}</a></p>'
    intro = "".join(f"<p>{e(x)}</p>" for x in pg["intro"])
    related = [x for x in PRODUCTS if x["id"] != pid][:3]
    price_num = p["price"].replace("\u00a3", "")
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": p["line"] + ". " + " ".join(pg["intro"]),
          "image": [f"{SITE['domain']}/img/products/{pid}/{i:02d}.jpg" for i in range(1, n + 1)],
          "brand": {"@type": "Brand", "name": SITE["name"]},
          "offers": {"@type": "Offer", "url": SITE["domain"] + url, "priceCurrency": "GBP", "price": price_num, "availability": "https://schema.org/InStock"}}
    body = f"""
<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/shop/">Shop</a><span aria-hidden="true">/</span><span>{e(p['name'])}</span></nav></div>
<section class="pdp wrap">
  <div class="gallery"><div class="stage">{''.join(slides)}</div><div class="thumbs">{''.join(thumbs)}</div></div>
  <div class="pinfo">
    <h1>{e(p['name'])}</h1>
    <p class="lead">{e(p['line'])}</p>
    <div class="buy">{price_html(p)}{buy_button(p)}</div>
    <ul class="ticks"><li>Instant download, nothing is posted</li><li>Print at home as often as you like</li><li>Secure checkout by Payhip</li></ul>
    <div class="intro">{intro}</div>
  </div>
</section>
<section class="pdp-more wrap">{secs}
  <p class="foot-note">Good to know: this is a digital download, so nothing is posted. Because it’s available immediately, your 14 day right to cancel ends once the download starts. For personal use only. Sold by {e(SITE['seller']['trading_as'])} (<a href="/privacy/#seller">seller details</a>).</p>
</section>
<section class="section wrap" aria-labelledby="rel-h"><div class="section-head"><h2 id="rel-h">You might also like</h2><a class="btn-outline" href="/shop/">All products</a></div>
  <div class="shop-grid related">{''.join(product_card(x, cls='shop-item', heading='h3') for x in related)}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script>{GALLERY_JS}</script>
"""
    desc = (p["line"] + ". " + " ".join(pg["intro"]))[:300]
    page(f"shop/{pid}/index.html", f"{pg['title']} | Plot to Plate with June", desc, body, current="/shop/", payhip=True)


for _p in PRODUCTS:
    if _p.get("page"):
        product_page(_p)


# ---------- Quiz result page (linked from the quiz welcome email) ----------
QR = _smart(json.load(open(os.path.join(ROOT, "data/quiz_results.json"))))
QR_IMG = {"windowsill-grower": "space-windowsill.jpg", "patio-potter": "space-patio.jpg", "small-bed-starter": "space-small-bed.jpg", "plot-keeper": "space-allotment.jpg"}


def qr_section(r):
    five = "".join(f"<li><b>{e(c['crop'])}:</b> {e(c['text'])}</li>" for c in r["five"])
    rec = "".join(f"<div class=\"qr-rec\"><h3>{e(x['title'])}</h3><p>{e(x['method'])}</p></div>" for x in r["recipes"])
    return (f'<section class="qr" id="{r["key"]}" data-name="{e(r["name"].lower())}">'
            f'<div class="qr-head"><img src="/img/{QR_IMG[r["key"]]}" alt="" width="120" height="120"><div><p class="kicker">Your result</p><h2>{e(r["name"])}</h2><p>{e(r["intro"])}</p></div></div>'
            f'<h3>Your starter five</h3><ol class="qr-five">{five}</ol>'
            f'<div class="qr-now"><b>Right now:</b> {e(r["right_now"])}</div>'
            f'<h3>Two things to cook</h3><div class="qr-recs">{rec}</div></section>')


QR_JS = r"""
(function(){
  var p=new URLSearchParams(location.search).get('r')||location.hash.slice(1)||'';
  var k=p.toLowerCase().replace(/[^a-z]+/g,' ').trim();
  var secs=[].slice.call(document.querySelectorAll('.qr')), tabs=[].slice.call(document.querySelectorAll('.qr-tabs button'));
  function show(i){secs.forEach(function(s,j){s.hidden=j!==i;});tabs.forEach(function(t,j){t.setAttribute('aria-pressed',j===i?'true':'false');});}
  var i=secs.findIndex(function(s){return s.dataset.name===k||s.id===p.toLowerCase();});
  show(i<0?0:i);
  tabs.forEach(function(t,j){t.addEventListener('click',function(){show(j);});});
})();
"""

qr_body = f"""
<section class="page-hero wrap"><h1>Your starter plan</h1><p>Your five easiest crops, one job for right now, and two things to cook. Pick your result if it isn\u2019t showing.</p>
<div class="qr-tabs" role="group" aria-label="Quiz results">{''.join(f'<button type="button" aria-pressed="false">{e(r["name"])}</button>' for r in QR)}</div></section>
<div class="wrap qr-wrap">{''.join(qr_section(r) for r in QR)}
<div class="notice" style="margin-top:22px"><p><b>Your free sowing calendar</b> comes by email at the start of each month.</p><a class="btn" href="/shop/">See June\u2019s planners</a></div></div>
<script>{QR_JS}</script>
"""
page("your-result/index.html", "Your grow your own starter plan | Plot to Plate with June",
     "Your five easiest crops, one job for right now and two seasonal recipes, from June's free quiz.", qr_body, noindex=True)


# ---------- The Gardener Level Test ----------
from test_svgs import SVGS
GT = _smart(json.load(open(os.path.join(ROOT, "data/test.json"))))
GT_FORM = "https://assets.mailerlite.com/jsonp/2722815/forms/201962470142641565/subscribe"
gt_data = {"levels": GT["levels"], "form": GT_FORM, "svgs": SVGS,
           "questions": [{k: q[k] for k in ("fmt", "q", "img", "alt", "options", "answer", "why") if k in q} for q in GT["questions"]]}
gt_json = json.dumps(gt_data, ensure_ascii=False).replace("</", "<\\/")
gt_body = f"""
<link rel="stylesheet" href="/assets/test.css">
<section class="page-hero wrap" style="text-align:center"><h1>The Gardener Level Test</h1><p style="margin-inline:auto">Are you a Seedling or a Head Gardener? 15 questions to find out how good a gardener you really are.</p></section>
<div class="gt-wrap"><div id="gt" class="gt"><div class="gt-card"><p>Loading the test…</p><noscript><p>The test needs JavaScript switched on to run.</p></noscript></div></div></div>
<script type="application/json" id="gt-data">{gt_json}</script>
<script src="/assets/test.js" defer></script>
"""
page("test/index.html", "The Gardener Level Test: how good a gardener are you? | Plot to Plate with June",
     "15 quick questions, from easy to tricky. Find out if you're a Seedling, Sprout, Green Fingers or Head Gardener.", gt_body, current="/test/")

TICK_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CROSS_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/></svg>'


def bd_item(n, q):
    ans = q["options"][q["answer"]]["label"]
    if q["fmt"] == "tt" and q["q"].startswith("Which courgette flower"):
        ans = "The male flower, on a thin stalk"
    return (f'<li class="bd-item" data-n="{n}"><p class="bd-n"><span class="bd-ico"></span>Question {n + 1}</p>'
            f'<h3>{e(q["q"])}</h3><p class="bd-ans">Answer: {e(ans)}</p><p>{e(q["why"])}</p>'
            f'<p class="bd-tip"><b>June’s tip:</b> {e(q["tip"])}</p></li>')


BD_JS = r"""
(function(){
  var a=(new URLSearchParams(location.search).get('a')||'').replace(/[^01]/g,'');
  var LV=%s, T='%s', X='%s';
  if(a.length!==15){document.getElementById('bd-sum').hidden=true;return;}
  var s=a.split('').filter(function(c){return c==='1';}).length, lv=0;
  LV.forEach(function(l,n){if(s>=l.min&&s<=l.max)lv=n;});
  document.getElementById('bd-level').textContent=LV[lv].name;
  document.getElementById('bd-score').textContent=s+' out of 15';
  [].forEach.call(document.querySelectorAll('.bd-item'),function(li){
    var ok=a.charAt(+li.dataset.n)==='1'; li.classList.add(ok?'ok':'no');
    li.querySelector('.bd-ico').innerHTML=ok?T:X;
    li.querySelector('.bd-n').insertAdjacentText('beforeend',ok?' · you got this':' · one to learn');
  });
  var miss=document.querySelector('.bd-item.no'); if(miss) document.getElementById('bd-jump').href='#'+(miss.id='q'+miss.dataset.n); else document.getElementById('bd-jump').hidden=true;
})();
""" % (json.dumps([{"name": l["name"], "min": l["min"], "max": l["max"]} for l in GT["levels"]]), TICK_SVG, CROSS_SVG)

bd_body = f"""
<link rel="stylesheet" href="/assets/test.css">
<section class="page-hero wrap" style="max-width:720px"><h1>Your test breakdown</h1><p>Every answer explained, with a tip from me for each one.</p></section>
<div class="bd">
<div class="bd-sum" id="bd-sum"><div><p class="gt-kicker">Your level</p><h2 id="bd-level"></h2><p id="bd-score"></p><p style="margin-top:6px"><a id="bd-jump" href="#">Jump to the first one you missed</a></p></div></div>
<ol class="bd-list">{''.join(bd_item(n, q) for n, q in enumerate(GT["questions"]))}</ol>
<div class="notice bd-next"><p><b>Think you can do better?</b> Have another go, or send it to a friend and see who really has the green fingers.</p><a class="btn" href="/test/">Take the test again</a></div>
<div class="notice bd-next"><p><b>Want to know what to sow this month?</b> Have a look at this month’s jobs, crops and recipe.</p><a class="btn-outline" href="/this-month/">This month in the garden</a></div>
</div>
<script>{BD_JS}</script>
"""
page("test/breakdown/index.html", "Your Gardener Level Test breakdown | Plot to Plate with June",
     "Every answer from the Gardener Level Test explained, with a tip for each.", bd_body, noindex=True)


# ---------- Privacy ----------
priv = f"""
<div class="wrap"><article class="prose">
<h1>Privacy</h1>
<p>Last updated {date.today().strftime('%-d %B %Y')}.</p>
<h2 id="seller">Who runs this site</h2>
<p>{e(SITE['seller']['trading_as'])} is run by {e(SITE['seller']['name'])}, {e(SITE['seller']['address'])}. You can contact us at {SITE['contact_email']}.</p>
<h2>What we collect</h2>
<p><b>The quiz.</b> If you take the free quiz, your answers and, if you choose to give it, your name and email are collected by Tally (our form provider). If you tick the box to hear from us, your email, name and quiz answers are added to our mailing list.</p>
{"<p><b>The calendar by email.</b> If you sign up for the monthly calendar, your email is added to our mailing list.</p>" if SITE["calendar_form"].get("action") else ""}
<p><b>Mailing list.</b> Our emails are sent with MailerLite. We use your details only to send you the emails you asked for, such as your quiz result, growing tips and the monthly calendar. Every email has an unsubscribe link, and you can ask us to delete your details at any time.</p>
<p><b>Buying a planner.</b> Purchases are handled by Payhip, which processes your payment and email to deliver your download. Pages with a Buy button load Payhip’s checkout script, which may set its own cookies to run the checkout. We don’t see or store your card details.</p>
<p><b>Visits to this site.</b> We use Cloudflare Web Analytics to count visits. It doesn’t use cookies or track you across other sites. This site sets no cookies of its own.</p>
<h2>Why we can use your details</h2>
<p>We email you only because you asked us to (your consent). You can withdraw it whenever you like by unsubscribing.</p>
<h2>How long we keep them</h2>
<p>Until you unsubscribe or ask us to delete them.</p>
<h2>Your rights</h2>
<p>You can ask to see, correct or delete the details we hold about you by emailing {SITE['contact_email']}. If you’re unhappy with how we’ve handled your data, you can complain to the Information Commissioner's Office at ico.org.uk.</p>
</article></div>
"""
page("privacy/index.html", "Privacy | Plot to Plate with June", "How Plot to Plate with June handles your details.", priv)


# ---------- 404, redirects, sitemap, robots ----------
nf = f"""<section class="page-hero wrap"><h1>That page has wandered off</h1><p>Try the home page, or see what to do in the garden this month.</p>
<p style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="/">Home</a><a class="btn-outline" href="/this-month/">This month</a></p></section>"""
page("404.html", "Page not found | Plot to Plate with June", "Page not found.", nf, noindex=True)

open(os.path.join(OUT, "_redirects"), "w").write(
    f"/calendar {SITE['calendar_file']} 302\n/quiz {SITE['quiz_url']}?utm_source=website&utm_medium=short_link&utm_campaign=quiz 302\n")
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")
urls = ["/", "/this-month/", "/shop/", "/test/"] + [f"/shop/{x['id']}/" for x in PRODUCTS if x.get("page")] + ["/privacy/"]
open(os.path.join(OUT, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{SITE['domain']}{u}</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n" for u in urls) + "</urlset>\n")
print("Built", OUT)
