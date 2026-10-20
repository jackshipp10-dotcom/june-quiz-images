import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

R = "/home/claude/products/render/"
PH = "/mnt/user-data/uploads/Plot to Plate June/Library/Photos/"
YP = "/mnt/user-data/uploads/Plot to Plate June/Digital Product/Payhip/Listing images Oct 2026/Year/"
FT = "/tmp/claude-0/fonts/"
OUT = "/home/claude/products/listing/"
S = 2000
GREEN = (46, 71, 51); CREAM = (251, 247, 238); INK = (31, 46, 34); TERRA = (180, 83, 47); SAGE = (92, 122, 78); GOLD = (226, 174, 62)
PALE = (238, 243, 232)


def f(name, size):
    return ImageFont.truetype(FT + name, size)


HEAD = lambda s: f("fraunces-600.ttf", s)
BODY = lambda s: f("figtree-400.ttf", s)
BODYM = lambda s: f("figtree-500.ttf", s)
BODYB = lambda s: f("figtree-700.ttf", s)


def cover_crop(im, w, h, fx=0.5, fy=0.5):
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r + 1), int(im.height * r + 1)), Image.LANCZOS)
    x = int((im.width - w) * fx); y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def paper(img, w, angle=0, shadow=28):
    img = img.convert("RGBA")
    h = int(img.height * w / img.width)
    img = img.resize((w, h), Image.LANCZOS)
    pad = shadow * 3
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((pad + shadow // 2, pad + shadow, pad + w + shadow // 2, pad + h + shadow), fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(shadow))
    canvas.alpha_composite(sh); canvas.alpha_composite(img, (pad, pad))
    if angle:
        canvas = canvas.rotate(angle, resample=Image.BICUBIC, expand=True)
    return canvas


def paste_c(base, top, cx, cy):
    base.alpha_composite(top, (int(cx - top.width / 2), int(cy - top.height / 2)))


def text_block(d, x, y, lines, font, fill, gap=1.3, maxw=None):
    for ln in lines:
        if maxw and not ln:
            y += int(font.size * gap * 0.6); continue
        if maxw:
            for sub in wrap(d, ln, font, maxw):
                d.text((x, y), sub, font=font, fill=fill); y += int(font.size * gap)
        else:
            d.text((x, y), ln, font=font, fill=fill); y += int(font.size * gap)
    return y


def wrap(d, txt, font, maxw):
    words, out, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            out.append(cur); cur = w
    if cur: out.append(cur)
    return out


def pill(d, x, y, txt, bg, fg, font):
    w = d.textlength(txt, font=font) + 56
    d.rounded_rectangle((x, y, x + w, y + font.size + 34), radius=(font.size + 34) // 2, fill=bg)
    d.text((x + 28, y + 15), txt, font=font, fill=fg)
    return x + w


def blurred_bg(photo, fx=0.5, fy=0.5, dark=0.55, blur=10):
    bg = cover_crop(Image.open(PH + photo).convert("RGB"), S, S, fx, fy)
    bg = bg.filter(ImageFilter.GaussianBlur(blur))
    bg = ImageEnhance.Brightness(bg).enhance(dark)
    return bg.convert("RGBA")


def badge_row(d, x, y, items):
    for t in items:
        x = pill(d, x, y, t, CREAM, GREEN, BODYB(40)) + 22


def save(im, name):
    os.makedirs(OUT + os.path.dirname(name), exist_ok=True)
    im.convert("RGB").save(OUT + name, quality=90)


# ---------------- Wall chart ----------------
def chart_images():
    uk = Image.open(R + "ukA3-1.png"); low = Image.open(R + "ukA3low-1.png"); fr = Image.open(R + "frA3-1.png")
    big = Image.open(R + "ukbig-1.png")
    # 1 hero
    im = blurred_bg("plot_plan_notebook_tea_snowy_window.png", 0.5, 0.75, 0.5)
    d = ImageDraw.Draw(im)
    d.text((110, 120), "PLOT TO PLATE WITH JUNE", font=BODYB(44), fill=(220, 229, 211))
    d.text((110, 185), "UK Sowing and", font=HEAD(128), fill=CREAM)
    d.text((110, 330), "Harvest Chart", font=HEAD(128), fill=CREAM)
    paste_c(im, paper(uk, 1700, angle=-2), S / 2, 1150)
    badge_row(d, 110, 1780, ["35 crops", "Every month", "Instant download"])
    save(im, "chart/chart_1_hero.jpg")
    # 2 detail
    im = Image.new("RGBA", (S, S), CREAM + (255,)); d = ImageDraw.Draw(im)
    crop = big.crop((0, int(big.height * 0.175), int(big.width * 0.55), int(big.height * 0.585)))
    paste_c(im, paper(crop, 1780, shadow=18), S / 2, 1150)
    d.text((110, 110), "Every crop, every fortnight", font=HEAD(96), fill=GREEN)
    d.text((110, 240), "When to sow indoors, sow outside, plant out and pick, in early and late", font=BODY(46), fill=INK)
    d.text((110, 300), "halves of each month, set for UK gardens.", font=BODY(46), fill=INK)
    save(im, "chart/chart_2_detail.jpg")
    # 3 cook strip and frost
    im = Image.new("RGBA", (S, S), CREAM + (255,)); d = ImageDraw.Draw(im)
    d.text((110, 140), "Grow it, then cook it", font=HEAD(110), fill=GREEN)
    import numpy as np
    arr = np.asarray(big.convert("RGB")).astype(int)
    g = (abs(arr[:, :, 0] - 46) < 12) & (abs(arr[:, :, 1] - 71) < 12) & (abs(arr[:, :, 2] - 51) < 12)
    rows = np.where(g.mean(axis=1) > 0.6)[0]; rows = rows[rows > big.height * 0.7]
    cols = np.where(g[rows[0]:rows[-1]].mean(axis=0) > 0.6)[0]
    st = big.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
    cut = int(st.width * 0.5735)
    a1 = st.crop((0, 0, cut, st.height))
    a2 = Image.new("RGB", (cut, st.height), (46, 71, 51)); a2.paste(st.crop((cut, 0, st.width, st.height)), (cut - (st.width - cut), 0))
    for k, piece in enumerate((a1, a2)):
        pc = piece.resize((1800, int(piece.height * 1800 / piece.width)), Image.LANCZOS)
        im.alpha_composite(paper(pc, 1800, shadow=12), (100 - 36, 700 + k * (pc.height + 140) - 36))
    text_block(d, 110, 330, ["A cook it strip runs along the bottom with a seasonal dish for every month,", "from leek and potato soup in January to sprouts with chestnuts at Christmas."], BODY(48), INK)
    for k2, ph in enumerate(["pumpkin_soup_bowl_bread.png", "roast_parsnips_tray_a.png", "rhubarb_crumble_kitchen.png"]):
        tile = cover_crop(Image.open(PH + ph).convert("RGB"), 560, 560, 0.5, 0.55)
        m = Image.new("L", tile.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 559, 559), radius=40, fill=255)
        t = Image.new("RGBA", tile.size); t.paste(tile, (0, 0), m)
        im.alpha_composite(t, (110 + k2 * 620, 1340))
    text_block(d, 110, 1180, ["The usual last frost is marked, so you know when", "tomatoes, beans and courgettes can go outside."], BODY(48), INK)
    save(im, "chart/chart_3_cook.jpg")
    # 4 what's included
    im = Image.new("RGBA", (S, S), CREAM + (255,)); d = ImageDraw.Draw(im)
    d.text((110, 110), "What you get", font=HEAD(110), fill=GREEN)
    paste_c(im, paper(uk, 820, angle=-3, shadow=16), 560, 760)
    paste_c(im, paper(low, 820, angle=2, shadow=16), 1440, 760)
    d.text((300, 1150), "Full colour", font=BODYB(50), fill=INK); d.text((1180, 1150), "Low ink", font=BODYB(50), fill=INK)
    y = 1290
    for t in ["UK edition: dates set for UK gardens", "Any garden edition: counted from your own last frost date", "Sizes: A4, A3 and US Letter, landscape", "Colour and low ink versions of each, 12 PDFs in one zip"]:
        d.ellipse((120, y + 18, 146, y + 44), fill=TERRA); d.text((175, y), t, font=BODY(52), fill=INK); y += 92
    save(im, "chart/chart_4_included.jpg")
    # 5 any garden
    im = Image.new("RGBA", (S, S), PALE + (255,)); d = ImageDraw.Draw(im)
    d.text((110, 110), "Not in the UK?", font=HEAD(110), fill=GREEN)
    text_block(d, 110, 260, ["The any garden edition counts in weeks from your own last", "spring frost, so it works anywhere with a spring frost."], BODY(50), INK)
    paste_c(im, paper(fr, 1760, angle=1, shadow=18), S / 2, 1230)
    save(im, "chart/chart_5_anygarden.jpg")
    # 6 lifestyle: pinned on the potting bench fence
    base = cover_crop(Image.open(PH + "potting_bench_red_ribbon_fence.png").convert("RGB"), S, S, 0.5, 0.25).convert("RGBA")
    p = paper(uk, 1150, angle=-1, shadow=14)
    base.alpha_composite(p, (int(S / 2 - p.width / 2), 120))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((80, 1700, 1050, 1900), radius=40, fill=CREAM)
    d.text((130, 1735), "Print it and pin it up", font=HEAD(64), fill=GREEN); d.text((130, 1815), "by the back door", font=HEAD(64), fill=GREEN)
    save(base, "chart/chart_6_lifestyle.jpg")
    # 7 why UK dates
    im = Image.new("RGBA", (S, S), CREAM + (255,)); d = ImageDraw.Draw(im)
    d.text((110, 140), "Why UK dates matter", font=HEAD(110), fill=GREEN)
    y = text_block(d, 110, 330, [
        "Many sowing charts online follow American seasons. Follow them here and your seedlings can sit sulking in the cold.",
        "",
        "This chart is set for UK gardens, with a note for the north and Scotland (start about two weeks later) and the south west (often a little earlier).",
    ], BODY(56), INK, maxw=1780)
    big2 = big.crop((int(big.width * 0.0), int(big.height * 0.0), int(big.width * 0.62), int(big.height * 0.36)))
    paste_c(im, paper(big2, 1500, angle=-2, shadow=16), S / 2, y + (S - y) / 2)
    save(im, "chart/chart_7_uk.jpg")


# ---------------- Seed kit ----------------
def seed_images():
    pages = {i: Image.open(R + f"seed-{i:02d}.png") for i in range(1, 13)}
    im = blurred_bg("seed_packets_bundle_twine_tea.png", 0.5, 0.6, 0.5)
    d = ImageDraw.Draw(im)
    d.text((110, 120), "PLOT TO PLATE WITH JUNE", font=BODYB(44), fill=(220, 229, 211))
    d.text((110, 185), "June’s Seed Tin Kit", font=HEAD(128), fill=CREAM)
    for k, (pg, ang, cx) in enumerate([(4, -6, 560), (10, 5, 1440), (1, 0, 1000)]):
        paste_c(im, paper(pages[pg], 760, angle=ang, shadow=18), cx, 1080)
    badge_row(d, 110, 1780, ["12 pages", "A4 and US Letter", "Instant download"])
    save(im, "seed/seed_1_hero.jpg")
    im = Image.new("RGBA", (S, S), CREAM + (255,)); d = ImageDraw.Draw(im)
    d.text((110, 110), "What’s inside", font=HEAD(110), fill=GREEN)
    thumbs = [(2, "Seed inventory"), (4, "Seed cards"), (6, "Month dividers"), (8, "Swap envelope"), (9, "Swap list"), (10, "Plant labels")]
    for i, (pg, lab) in enumerate(thumbs):
        cx = 360 + (i % 3) * 640; cy = 640 + (i // 3) * 820
        paste_c(im, paper(pages[pg], 470, shadow=12), cx, cy)
        tw = d.textlength(lab, font=BODYB(46)); d.text((cx - tw / 2, cy + 370), lab, font=BODYB(46), fill=INK)
    save(im, "seed/seed_2_inside.jpg")
    im = Image.new("RGBA", (S, S), GREEN + (255,)); d = ImageDraw.Draw(im)
    d.text((110, 120), "Labels for 32 crops", font=HEAD(110), fill=CREAM)
    d.text((110, 270), "Plus a page of blank ones. Print on card and pop one in every pot.", font=BODY(50), fill=(220, 229, 211))
    lab = Image.open(R + "seedlab-10.png"); lab = lab.crop((int(lab.width * 0.04), int(lab.height * 0.135), int(lab.width * 0.96), int(lab.height * 0.955)))
    paste_c(im, paper(lab, 1240, shadow=14), S / 2, 1170)
    save(im, "seed/seed_3_labels.jpg")
    base = cover_crop(Image.open(PH + "seed_envelopes_swapped_over_fence.png").convert("RGB"), S, S, 0.5, 0.55).convert("RGBA")
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((80, 80, 1300, 420), radius=40, fill=CREAM)
    d.text((130, 120), "Swap your spares", font=HEAD(84), fill=GREEN)
    text_block(d, 130, 245, ["A fold up seed envelope and a swap list,", "ready for seed swap season (January to March)."], BODY(46), INK)
    paste_c(base, paper(pages[8], 640, angle=6, shadow=16), 1560, 1450)
    save(base, "seed/seed_4_swap.jpg")
    im = Image.new("RGBA", (S, S), PALE + (255,)); d = ImageDraw.Draw(im)
    d.text((110, 110), "File seeds by month", font=HEAD(110), fill=GREEN)
    text_block(d, 110, 260, ["Twelve dividers with staggered tabs, so every month shows,", "and what’s usually sown or planted that month."], BODY(50), INK)
    paste_c(im, paper(pages[6], 820, angle=-3, shadow=16), 560, 1220)
    paste_c(im, paper(pages[7], 820, angle=3, shadow=16), 1440, 1220)
    save(im, "seed/seed_5_dividers.jpg")


# ---------------- Gift bundle ----------------
def bundle_images():
    uk = Image.open(R + "ukA3-1.png"); g1 = Image.open(R + "gift-1.png"); g2 = Image.open(R + "gift-2.png")
    seed1 = Image.open(R + "seed-01.png"); yc = Image.open(YP + "year_1_cover.jpg")
    im = blurred_bg("gifts_brown_paper_twine_potting_bench.png", 0.5, 0.45, 0.45)
    d = ImageDraw.Draw(im)
    d.text((110, 110), "THE GROW YOUR OWN GIFT SET", font=BODYB(44), fill=(242, 217, 160))
    d.text((110, 175), "A whole year of", font=HEAD(122), fill=CREAM)
    d.text((110, 315), "growing, to give", font=HEAD(122), fill=CREAM)
    paste_c(im, paper(uk, 1150, angle=-4, shadow=18), 640, 1000)
    paste_c(im, paper(yc.crop((314, 112, 1286, 1488)), 720, angle=3, shadow=20), 1390, 1020)
    paste_c(im, paper(seed1, 430, angle=-3, shadow=18), 520, 1500)
    paste_c(im, paper(g1.crop((g1.width // 2, 0, g1.width, g1.height)), 380, angle=4, shadow=18), 1740, 1560)
    badge_row(d, 110, 1820, ["3 products", "Printable gift card", "Instant download"])
    save(im, "bundle/bundle_1_hero.jpg")
    im = Image.new("RGBA", (S, S), CREAM + (255,)); d = ImageDraw.Draw(im)
    d.text((110, 110), "What’s in the gift set", font=HEAD(104), fill=GREEN)
    rows = [("The Year Planner", "51 pages: monthly guides, 21 crop cards, recipes and logs. Print, fillable and tablet versions.", "£11.99"),
            ("Sowing and Harvest Chart", "UK and any garden editions, A4, A3 and US Letter, colour and low ink.", "£3.95"),
            ("June’s Seed Tin Kit", "Seed cards, month dividers, swap envelopes, 32 plant labels.", "£3.50"),
            ("Printable gift card", "Folds in half, with June on the front and room for your message inside.", "included")]
    y = 330
    for t, desc, price in rows:
        d.rounded_rectangle((110, y, S - 110, y + 300), radius=36, fill=PALE)
        d.text((170, y + 40), t, font=HEAD(64), fill=GREEN)
        text_block(d, 170, y + 140, [desc], BODY(46), INK, maxw=S - 400)
        y += 340
    d.text((110, y + 40), "All four in one download, ready to print or give.", font=BODYB(56), fill=INK)
    save(im, "bundle/bundle_2_included.jpg")
    im = Image.new("RGBA", (S, S), GREEN + (255,)); d = ImageDraw.Draw(im)
    d.text((110, 120), "A card to give", font=HEAD(110), fill=CREAM)
    text_block(d, 110, 270, ["Print on card, fold in half, write your message.", "Perfect for a stocking or tucked into gardening gloves."], BODY(50), (220, 229, 211))
    paste_c(im, paper(g1.crop((g1.width // 2, 0, g1.width, g1.height)), 760, angle=-4, shadow=18), 620, 1250)
    paste_c(im, paper(g2, 1000, angle=3, shadow=18), 1400, 1300)
    save(im, "bundle/bundle_3_card.jpg")
    base = cover_crop(Image.open(PH + "wooden_trug_winter_veg_ribbon.png").convert("RGB"), S, S, 0.5, 0.5).convert("RGBA")
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((80, 1560, 1500, 1910), radius=40, fill=CREAM)
    d.text((130, 1600), "For the gardener who has everything", font=HEAD(66), fill=GREEN)
    text_block(d, 130, 1700, ["Nothing to post, nothing to wrap. Buy today,", "print tonight, give it tomorrow."], BODY(48), INK)
    save(base, "bundle/bundle_4_lifestyle.jpg")


if __name__ == "__main__":
    chart_images(); seed_images(); bundle_images(); print("ok")
