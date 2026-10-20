import sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.colors import HexColor, white
sys.path.insert(0, os.path.dirname(__file__))
import wallchart as wc  # fonts and colours
from reportlab.pdfbase import pdfmetrics

GREEN, INK, MUTED, TERRA, SAGE, LINE, CREAM = wc.GREEN, wc.INK, wc.MUTED, wc.TERRA, wc.SAGE, wc.LINE, wc.CREAM
PALE = HexColor("#EEF3E8")
W, H = 210 * mm, 297 * mm
M = 14 * mm
HERE = os.path.dirname(__file__)


def page_setup(c, ps):
    pw, ph = ps
    s = min(pw / W, ph / H)
    c.translate((pw - W * s) / 2, (ph - H * s) / 2); c.scale(s, s)


def head(c, kicker, title, sub=None):
    c.setFillColor(SAGE); c.setFont("BodyB", 8.5); c.drawString(M, H - 18 * mm, kicker.upper())
    c.setFillColor(GREEN); c.setFont("Head", 22); c.drawString(M, H - 27 * mm, title)
    y = H - 27 * mm
    if sub:
        c.setFillColor(MUTED); c.setFont("Body", 10)
        for ln in wc.wrap(sub, "Body", 10, W - 2 * M):
            y -= 5.2 * mm; c.drawString(M, y, ln)
    c.setStrokeColor(GREEN); c.setLineWidth(0.8); c.line(M, y - 4 * mm, W - M, y - 4 * mm)
    return y - 9 * mm


def foot(c, n):
    c.setFillColor(MUTED); c.setFont("Body", 7.5)
    c.drawString(M, 9 * mm, "June’s Seed Tin Kit  ·  Plot to Plate with June  ·  For personal use only")
    c.drawRightString(W - M, 9 * mm, str(n))


def table(c, y, cols, rows=None, rh=8.2 * mm, bottom=16 * mm):
    x = M; tw = W - 2 * M
    total = sum(w for _, w in cols)
    xs = [x]
    for _, w in cols:
        xs.append(xs[-1] + w / total * tw)
    c.setFillColor(GREEN); c.roundRect(x, y - 7 * mm, tw, 7 * mm, 1.5 * mm, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("BodyB", 8.2)
    for i, (name, _) in enumerate(cols):
        c.drawString(xs[i] + 1.8 * mm, y - 4.6 * mm, name)
    y -= 7 * mm
    n = 0
    while y - rh >= bottom and (rows is None or n < rows):
        if n % 2 == 1:
            c.setFillColor(HexColor("#F5F7F2")); c.rect(x, y - rh, tw, rh, fill=1, stroke=0)
        c.setStrokeColor(LINE); c.setLineWidth(0.4); c.line(x, y - rh, x + tw, y - rh)
        y -= rh; n += 1
    c.setStrokeColor(LINE)
    for xx in xs[1:-1]:
        c.line(xx, y, xx, y + n * rh)
    return y


def cover(c):
    c.setFillColor(GREEN); c.rect(0, H - 120 * mm, W, 120 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#DCE5D3")); c.setFont("BodyB", 9); c.drawString(M, H - 22 * mm, "PLOT TO PLATE WITH JUNE")
    c.setFillColor(CREAM); c.setFont("Head", 38); c.drawString(M, H - 42 * mm, "June’s Seed Tin Kit")
    c.setFont("Body", 13); c.setFillColor(HexColor("#DCE5D3"))
    c.drawString(M, H - 52 * mm, "Keep track of your seeds, swap the spares, and label what you sow.")
    d = 62 * mm
    c.setFillColor(CREAM); c.circle(W - M - d / 2, H - 120 * mm, d / 2 + 2 * mm, fill=1, stroke=0)
    c.drawImage(os.path.join(HERE, "june_circle.png"), W - M - d, H - 120 * mm - d / 2, d, d, mask="auto")
    y = H - 140 * mm
    c.setFillColor(GREEN); c.setFont("Head", 15); c.drawString(M, y, "What’s inside")
    items = [
        ("Seed tin inventory", "every packet you own, with its sow by date"),
        ("Seed cards", "blank cards to fill in, one per crop, for the tin"),
        ("Month dividers", "file packets by the month you sow them"),
        ("Seed swap envelopes", "fold, fill and label spare seeds for friends"),
        ("My swap list", "what you have to give and what you’re after"),
        ("Plant labels", "ready made labels for 32 crops, plus blank ones"),
        ("Sowing record", "what you sowed, when, and how many came up"),
    ]
    y -= 9 * mm
    for t, d2 in items:
        c.setFillColor(TERRA); c.circle(M + 2 * mm, y + 1.2 * mm, 1.2 * mm, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("BodyB", 10.5); c.drawString(M + 6 * mm, y, t)
        c.setFont("Body", 10.5); c.setFillColor(MUTED)
        c.drawString(M + 6 * mm + pdfmetrics.stringWidth(t, "BodyB", 10.5) + 2 * mm, y, d2)
        y -= 7.5 * mm
    y -= 5 * mm
    c.setFillColor(PALE); c.roundRect(M, y - 34 * mm, W - 2 * M, 38 * mm, 4 * mm, fill=1, stroke=0)
    c.setFillColor(GREEN); c.setFont("Head", 12.5); c.drawString(M + 6 * mm, y - 4 * mm, "A note from me")
    note = ("My seeds live in an old biscuit tin, filed by the month I sow them. On the first of each month I open it, "
            "pull out that month’s cards, and I know exactly what’s going in. No more finding a packet of beans in June "
            "that should have gone in back in May. Print these on card if you can, cut them out with a cup of tea, and you’re set.")
    c.setFont("Body", 10); c.setFillColor(INK)
    yy = y - 10.5 * mm
    for ln in wc.wrap(note, "Body", 10, W - 2 * M - 12 * mm):
        c.drawString(M + 6 * mm, yy, ln); yy -= 5 * mm
    c.setFont("Head", 11); c.setFillColor(TERRA); c.drawString(M + 6 * mm, yy - 1 * mm, "June")
    c.setFillColor(MUTED); c.setFont("Body", 8)
    c.drawString(M, 14 * mm, "Printing tip: print at 100% (actual size). Card of 160 to 200 gsm works best for seed cards, dividers and labels.")
    c.drawString(M, 9 * mm, "Plot to Plate with June  ·  plottoplatejune.co.uk  ·  For personal use only")


def inventory(c, n):
    y = head(c, "Seed tin inventory", "Every packet I own", "List each packet as it goes in the tin. Seeds keep best somewhere cool, dry and dark; most last two to four years, parsnips only one.")
    table(c, y, [("Crop", 3), ("Variety", 3.4), ("From", 2.2), ("Sow by", 1.6), ("How many", 1.5), ("Notes", 3.3)])
    foot(c, n)


def seed_cards(c, n):
    y0 = head(c, "Seed cards", "One card per crop", "Cut along the dashed lines. Fill one in for each crop and file it behind the month you’ll sow it.")
    cw, ch = (W - 2 * M - 6 * mm) / 2, (y0 - 14 * mm - 2 * 6 * mm) / 3
    for r in range(3):
        for col in range(2):
            x = M + col * (cw + 6 * mm); y = y0 - r * (ch + 6 * mm)
            c.setStrokeColor(MUTED); c.setDash(2, 2); c.setLineWidth(0.5); c.rect(x, y - ch, cw, ch, fill=0, stroke=1); c.setDash()
            c.setFillColor(GREEN); c.rect(x, y - 9 * mm, cw, 9 * mm, fill=1, stroke=0)
            c.setFillColor(white); c.setFont("BodyB", 9); c.drawString(x + 3 * mm, y - 6 * mm, "CROP")
            c.setStrokeColor(HexColor("#9FB596")); c.line(x + 15 * mm, y - 6.6 * mm, x + cw - 4 * mm, y - 6.6 * mm)
            fields = ["Variety", "Sow indoors", "Sow outside", "Plant out", "Spacing", "Ready in", "Notes"]
            fy = y - 16 * mm
            step = (ch - 18 * mm) / len(fields)
            for f in fields:
                c.setFillColor(INK); c.setFont("BodyM", 8.6); c.drawString(x + 3 * mm, fy, f)
                c.setStrokeColor(LINE); c.setLineWidth(0.5)
                c.line(x + 26 * mm, fy - 0.8 * mm, x + cw - 4 * mm, fy - 0.8 * mm)
                fy -= step
    foot(c, n)


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
SOW_HINT = {
    "January": "Microgreens and pea shoots; plan and order seeds",
    "February": "Chillies with heat, broad beans, garlic in mild spells",
    "March": "Tomatoes, peas, lettuce, leeks, beetroot in modules",
    "April": "Carrots, beetroot, chard, peas, rocket outside",
    "May": "Beans, courgettes, squash, sweetcorn indoors",
    "June": "French beans, salad, carrots, kale outside",
    "July": "Salad, spring onions, carrots, chard",
    "August": "Spinach, rocket, spring cabbage, salad",
    "September": "Overwintering onions, salad under cover",
    "October": "Garlic, autumn onion sets",
    "November": "Garlic, broad beans, bare root fruit",
    "December": "Plan, order seeds, sort the tin",
}


def dividers(c, n, start):
    y0 = head(c, "Month dividers", "File your seeds by month", "Cut out and stand one behind each month\u2019s cards in the tin, January at the front. The tabs are staggered across and up, so every month shows.")
    cw = (W - 2 * M - 6 * mm) / 2
    ch = (y0 - 14 * mm - 2 * 6 * mm) / 3
    tabw = (cw - 6 * mm) / 6
    for k in range(6):
        i = start + k
        mname = MONTHS[i]
        col, row = k % 2, k // 2
        x = M + col * (cw + 6 * mm); y = y0 - row * (ch + 6 * mm)
        tall = i >= 6
        tabh = 15 * mm if tall else 8 * mm
        bodytop = y - 16 * mm; bottom = y - ch
        tx = x + 3 * mm + (i % 6) * tabw
        p = c.beginPath()
        p.moveTo(x, bottom); p.lineTo(x, bodytop); p.lineTo(tx, bodytop); p.lineTo(tx + 1.5 * mm, bodytop + tabh)
        p.lineTo(tx + tabw - 1.5 * mm, bodytop + tabh); p.lineTo(tx + tabw, bodytop); p.lineTo(x + cw, bodytop); p.lineTo(x + cw, bottom); p.close()
        c.setFillColor(PALE); c.setStrokeColor(MUTED); c.setDash(2, 2); c.setLineWidth(0.5)
        c.drawPath(p, fill=1, stroke=1); c.setDash()
        c.setFillColor(GREEN); c.setFont("BodyB", 8.5); c.drawCentredString(tx + tabw / 2, bodytop + tabh - 5 * mm, mname[:3])
        c.setFont("Head", 13); c.drawString(x + 4 * mm, bodytop - 8 * mm, mname)
        c.setFillColor(INK); c.setFont("BodyM", 8.2); c.drawString(x + 4 * mm, bodytop - 14.5 * mm, "Usually sown or planted:")
        c.setFont("Body", 8.2); c.setFillColor(MUTED)
        yy = bodytop - 19.5 * mm
        for ln in wc.wrap(SOW_HINT[mname], "Body", 8.2, cw - 8 * mm):
            c.drawString(x + 4 * mm, yy, ln); yy -= 4 * mm
        c.setStrokeColor(LINE)
        ly = yy - 3 * mm
        while ly > bottom + 5 * mm:
            c.line(x + 4 * mm, ly, x + cw - 4 * mm, ly); ly -= 6.5 * mm
    foot(c, n)


def envelope(c, n):
    y0 = head(c, "Seed swap envelope", "Fold, fill and share", "Cut round the solid outline, fold the side flaps in, fold the bottom up, glue, then fill and fold the top down.")
    # envelope net, centred
    bw, bh = 90 * mm, 110 * mm  # front panel
    cx = W / 2; top = y0 - 4 * mm
    fx0, fx1 = cx - bw / 2, cx + bw / 2
    flap_top = 30 * mm; side = 18 * mm; bottom_flap = 60 * mm
    ytop = top - flap_top; ybot = ytop - bh
    c.setStrokeColor(INK); c.setLineWidth(0.8)
    p = c.beginPath()
    p.moveTo(fx0, ytop); p.lineTo(fx0 + 8 * mm, top); p.lineTo(fx1 - 8 * mm, top); p.lineTo(fx1, ytop)
    p.lineTo(fx1 + side, ytop - 8 * mm); p.lineTo(fx1 + side, ybot + 8 * mm); p.lineTo(fx1, ybot)
    p.lineTo(fx1 - 4 * mm, ybot - bottom_flap); p.lineTo(fx0 + 4 * mm, ybot - bottom_flap); p.lineTo(fx0, ybot)
    p.lineTo(fx0 - side, ybot + 8 * mm); p.lineTo(fx0 - side, ytop - 8 * mm); p.close()
    c.setFillColor(white); c.drawPath(p, fill=1, stroke=1)
    c.setDash(3, 2); c.setStrokeColor(MUTED); c.setLineWidth(0.5)
    c.line(fx0, ytop, fx1, ytop); c.line(fx0, ybot, fx1, ybot); c.line(fx0, ytop, fx0, ybot); c.line(fx1, ytop, fx1, ybot); c.setDash()
    # front design
    c.setFillColor(GREEN); c.rect(fx0, ytop - 22 * mm, bw, 22 * mm, fill=1, stroke=0)
    c.setFillColor(CREAM); c.setFont("Head", 15); c.drawCentredString(cx, ytop - 11 * mm, "Seeds to share")
    c.setFont("Body", 8.5); c.setFillColor(HexColor("#DCE5D3")); c.drawCentredString(cx, ytop - 17 * mm, "from my plot to yours")
    fy = ytop - 32 * mm
    for f in ["Crop", "Variety", "Saved by", "Year saved", "Sow", "Notes"]:
        c.setFillColor(INK); c.setFont("BodyM", 9.5); c.drawString(fx0 + 6 * mm, fy, f)
        c.setStrokeColor(LINE); c.line(fx0 + 27 * mm, fy - 1 * mm, fx1 - 6 * mm, fy - 1 * mm)
        fy -= 12 * mm
    c.setFillColor(MUTED); c.setFont("Body", 7.5); c.drawCentredString(cx, ybot + 4 * mm, "Plot to Plate with June")
    c.setFont("Body", 8); c.drawCentredString(cx, ybot - bottom_flap / 2, "glue this flap")
    foot(c, n)


def swap_list(c, n):
    y = head(c, "My swap list", "What I have and what I’m after", "Take this to a seed swap or a plot neighbour. Most seed swaps run from January to March.")
    half = (W - 2 * M - 6 * mm) / 2
    for i, t in enumerate(["I have spare", "I’m looking for"]):
        x = M + i * (half + 6 * mm)
        c.setFillColor(GREEN if i == 0 else TERRA); c.roundRect(x, y - 8 * mm, half, 8 * mm, 1.5 * mm, fill=1, stroke=0)
        c.setFillColor(white); c.setFont("BodyB", 10); c.drawString(x + 3 * mm, y - 5.4 * mm, t)
        yy = y - 8 * mm
        while yy - 9 * mm > 16 * mm:
            c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(x, yy - 9 * mm, x + half, yy - 9 * mm)
            c.rect(x + 1.5 * mm, yy - 7 * mm, 3.4 * mm, 3.4 * mm, fill=0, stroke=1)
            yy -= 9 * mm
    foot(c, n)


LABELS = ["Tomato", "Chilli", "Pepper", "Courgette", "Squash", "Pumpkin", "Cucumber", "Sweetcorn", "Runner bean", "French bean",
          "Broad bean", "Pea", "Lettuce", "Salad leaves", "Rocket", "Spinach", "Chard", "Kale", "Cabbage", "Sprouts",
          "Beetroot", "Carrot", "Parsnip", "Radish", "Spring onion", "Leek", "Onion", "Garlic", "Basil", "Parsley",
          "Coriander", "Strawberry"]


def labels(c, n, names):
    y0 = head(c, "Plant labels", "Pop one in every pot", "Cut out, then glue to a lolly stick or slip into a clear label sleeve. Write the date you sowed or planted it underneath.")
    cols, rows = 4, 8
    lw = (W - 2 * M - (cols - 1) * 3 * mm) / cols
    lh = (y0 - 14 * mm - (rows - 1) * 3 * mm) / rows
    k = 0
    tints = [HexColor("#E2EFD9"), HexColor("#F5DFD5"), HexColor("#FAEBC7"), HexColor("#DDE9F3")]
    for r in range(rows):
        for col in range(cols):
            x = M + col * (lw + 3 * mm); y = y0 - r * (lh + 3 * mm)
            nm = names[k] if k < len(names) else None
            c.setFillColor(tints[(r + col) % 4] if nm else white); c.setStrokeColor(MUTED); c.setDash(2, 2); c.setLineWidth(0.5)
            c.roundRect(x, y - lh, lw, lh, 2.5 * mm, fill=1, stroke=1); c.setDash()
            if nm:
                c.setFillColor(GREEN); c.setFont("Head", 13); c.drawCentredString(x + lw / 2, y - lh / 2 + 0.5 * mm, nm)
                c.setFont("Body", 7); c.setFillColor(MUTED); c.drawCentredString(x + lw / 2, y - lh + 3.2 * mm, "date ____ / ____")
            else:
                c.setStrokeColor(LINE); c.line(x + 4 * mm, y - lh / 2 - 1 * mm, x + lw - 4 * mm, y - lh / 2 - 1 * mm)
                c.setFont("Body", 7); c.setFillColor(MUTED); c.drawCentredString(x + lw / 2, y - lh + 3.2 * mm, "date ____ / ____")
            k += 1
    foot(c, n)


def sowing_record(c, n):
    y = head(c, "Sowing record", "What I sowed and how it did", "Note how many seeds you sowed and how many came up. Old seed with a poor score can be sown more thickly, or replaced.")
    table(c, y, [("Date", 1.5), ("Crop and variety", 4.2), ("Where", 2.2), ("Sown", 1.2), ("Came up", 1.4), ("Notes", 4.5)])
    foot(c, n)


def build(path, ps):
    c = canvas.Canvas(path, pagesize=ps)
    c.setTitle("June's Seed Tin Kit"); c.setAuthor("Plot to Plate with June")
    c.setSubject("Seed inventory, seed cards, month dividers, seed swap envelopes and plant labels")
    pages = [cover, inventory, inventory, seed_cards, seed_cards,
             lambda c, n: dividers(c, n, 0), lambda c, n: dividers(c, n, 6),
             envelope, swap_list, lambda c, n: labels(c, n, LABELS), lambda c, n: labels(c, n, []), sowing_record]
    for i, fn in enumerate(pages, 1):
        page_setup(c, ps)
        if fn is cover:
            fn(c)
        else:
            fn(c, i)
        c.showPage()
    c.save()


if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    build(f"{out}/June's Seed Tin Kit A4.pdf", A4)
    build(f"{out}/June's Seed Tin Kit US Letter.pdf", LETTER)
    print("ok")
