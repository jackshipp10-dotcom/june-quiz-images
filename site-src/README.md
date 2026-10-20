# June's website (plottoplatejune.co.uk)

Static site served by Cloudflare Pages from the `site/` folder of this repo (no build command).

- Edit content in `site-src/data/`: `month.json` (This month, updated on the 28th), `products.json` (shop), `site.json` (links, calendar form).
- Run `python3 site-src/build.py` to regenerate `site/`, then commit and push. Pages deploys automatically.
- Images live in `site/img/` (JPEG, about 600px squares for month photos, 560px wide portrait covers for products).
- Adding a product: add an entry to `products.json` (platform `payhip` with `payhip_code`, or `etsy` with `url`) and its cover in `site/img/`. The home page switches to a swipe row at 3 or more featured products.
- `/calendar` and `/quiz` short links are in `site/_redirects` (generated).
