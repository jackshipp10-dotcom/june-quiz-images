import sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, LETTER, landscape
from reportlab.lib.colors import HexColor, white
sys.path.insert(0, os.path.dirname(__file__))
import wallchart as wc
from reportlab.pdfbase import pdfmetrics

GREEN, INK, MUTED, TERRA, SAGE, LINE, CREAM = wc.GREEN, wc.INK, wc.MUTED, wc.TERRA, wc.SAGE, wc.LINE, wc.CREAM
GOLD = HexColor("#E2AE3E")
HERE = os.path.dirname(__file__)
W, H = 297 * mm, 210 * mm  # A4 landscape design, folds to A5


def setup(c, ps):
    pw, ph = ps
    s = min(pw / W, ph / H)
    c.translate((pw - W * s) / 2, (ph - H * s) / 2); c.scale(s, s)


def outside(c):
    # left half = back, right half = front (fold down the middle)
    c.setFillColor(CREAM); c.rect(0, 0, W, H, fill=1, stroke=0)
    fx = W / 2
    c.setFillColor(GREEN); c.rect(fx, 0, W / 2, H, fill=1, stroke=0)
    d = 52 * mm; cx = fx + W / 4
    c.setFillColor(CREAM); c.circle(cx, H - 70 * mm, d / 2 + 1.8 * mm, fill=1, stroke=0)
    c.drawImage(os.path.join(HERE, "june_circle.png"), cx - d / 2, H - 70 * mm - d / 2, d, d, mask="auto")
    c.setFillColor(HexColor("#F2D9A0")); c.setFont("BodyB", 9); c.drawCentredString(cx, H - 110 * mm, "A GIFT FOR THE GROWING YEAR")
    c.setFillColor(CREAM); c.setFont("Head", 27); c.drawCentredString(cx, H - 124 * mm, "Something to")
    c.drawCentredString(cx, H - 136 * mm, "grow into")
    c.setFont("Body", 11); c.setFillColor(HexColor("#DCE5D3"))
    c.drawCentredString(cx, H - 147 * mm, "A year of planning, sowing and cooking")
    c.drawCentredString(cx, H - 153 * mm, "with June, for gardens across the UK")
    c.setFont("BodyM", 8.5); c.drawCentredString(cx, 14 * mm, "Plot to Plate with June")
    # back
    bx = W / 4
    c.setFillColor(GREEN); c.setFont("Head", 14); c.drawCentredString(bx, H / 2 + 6 * mm, "Plot to Plate with June")
    c.setFillColor(MUTED); c.setFont("Body", 9.5)
    c.drawCentredString(bx, H / 2 - 1 * mm, "Grow it, then cook it.")
    c.drawCentredString(bx, H / 2 - 7 * mm, "plottoplatejune.co.uk")
    c.setStrokeColor(LINE); c.setDash(3, 3); c.line(fx, 6 * mm, fx, H - 6 * mm); c.setDash()


def inside(c):
    c.setFillColor(white); c.rect(0, 0, W, H, fill=1, stroke=0)
    # left: what's inside
    x = 16 * mm; y = H - 22 * mm
    c.setFillColor(SAGE); c.setFont("BodyB", 9); c.drawString(x, y, "WHAT’S IN YOUR GIFT")
    c.setFillColor(GREEN); c.setFont("Head", 19); c.drawString(x, y - 11 * mm, "Your growing year")
    items = [
        ("The Year Planner", "Month by month guides, 21 crop cards, recipes and logs. Print it, type into it, or use it on a tablet."),
        ("The Sowing and Harvest Chart", "Every crop and every month on one page. Pin it up by the back door."),
        ("The Seed Tin Kit", "Seed cards, month dividers, swap envelopes and plant labels."),
    ]
    yy = y - 24 * mm
    for t, d in items:
        c.setFillColor(GOLD); c.circle(x + 2 * mm, yy + 1.3 * mm, 1.6 * mm, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("BodyB", 11); c.drawString(x + 7 * mm, yy, t)
        c.setFont("Body", 9.6); c.setFillColor(MUTED)
        ly = yy - 5.2 * mm
        for ln in wc.wrap(d, "Body", 9.6, W / 2 - x - 20 * mm):
            c.drawString(x + 7 * mm, ly, ln); ly -= 4.6 * mm
        yy = ly - 5 * mm
    by = yy - 32 * mm
    c.setFillColor(HexColor("#EEF3E8")); c.roundRect(x, by, W / 2 - x - 12 * mm, 30 * mm, 3 * mm, fill=1, stroke=0)
    c.setFillColor(GREEN); c.setFont("BodyB", 9.5); c.drawString(x + 5 * mm, by + 22 * mm, "Where to start")
    c.setFont("Body", 9.2); c.setFillColor(INK)
    tip = "Open the planner at this month, pick three crops from the year at a glance, and file their seed cards in the tin. That’s you started."
    ly = by + 16 * mm
    for ln in wc.wrap(tip, "Body", 9.2, W / 2 - x - 22 * mm):
        c.drawString(x + 5 * mm, ly, ln); ly -= 4.4 * mm
    # right: message
    fx = W / 2; rx = fx + 16 * mm; rw = W / 2 - 32 * mm
    c.setFillColor(TERRA); c.setFont("Head", 15)
    for i, lab in enumerate(["To", "From"]):
        yy = H - 30 * mm - i * 16 * mm
        c.drawString(rx, yy, lab)
        c.setStrokeColor(LINE); c.setLineWidth(0.6); c.line(rx + 16 * mm, yy - 1 * mm, rx + rw, yy - 1 * mm)
    c.setFillColor(SAGE); c.setFont("BodyB", 9); c.drawString(rx, H - 66 * mm, "A FEW WORDS")
    for k in range(6):
        yy = H - 78 * mm - k * 11 * mm
        c.line(rx, yy, rx + rw, yy)
    c.setFillColor(MUTED); c.setFont("Body", 9.2)
    note = "“There’s nothing quite like eating something you grew yourself. Start small, enjoy it, and don’t worry about the slugs.”"
    ly = 28 * mm
    for ln in wc.wrap(note, "Body", 9.2, rw):
        c.drawString(rx, ly, ln); ly -= 4.4 * mm
    c.setFillColor(TERRA); c.setFont("Head", 11); c.drawString(rx, ly - 1 * mm, "June")
    c.setStrokeColor(LINE); c.setDash(3, 3); c.line(fx, 6 * mm, fx, H - 6 * mm); c.setDash()


def howto(c):
    c.setFillColor(white); c.rect(0, 0, W, H, fill=1, stroke=0)
    x = 20 * mm; y = H - 24 * mm
    c.setFillColor(SAGE); c.setFont("BodyB", 9); c.drawString(x, y, "FOR THE GIVER")
    c.setFillColor(GREEN); c.setFont("Head", 22); c.drawString(x, y - 12 * mm, "How to give this gift")
    steps = [
        f"Print the gift card pages on card (160 to 200 gsm), {PAPER['sheet']} landscape, at actual size. Print pages 1 and 2 on the same sheet, double sided (flip on the short edge), so the message sits inside when you fold it.",
        f"Fold it in half down the dashed line. You now have a {PAPER['fold']} card with June on the front.",
        "Write your message inside and put it in an envelope, or tuck it into a seed tin or a pair of gardening gloves.",
        "Send the files to the person you’re giving it to by email, or print the pages they’ll use and put them in a ring binder.",
        "Short on time? Email them the files and send this card as a picture instead.",
    ]
    yy = y - 26 * mm
    for i, s in enumerate(steps, 1):
        c.setFillColor(TERRA); c.circle(x + 3.5 * mm, yy + 1.4 * mm, 3.5 * mm, fill=1, stroke=0)
        c.setFillColor(white); c.setFont("BodyB", 9.5); c.drawCentredString(x + 3.5 * mm, yy - 0.2 * mm, str(i))
        c.setFillColor(INK); c.setFont("Body", 10.5)
        ly = yy
        for ln in wc.wrap(s, "Body", 10.5, W - x - 40 * mm):
            c.drawString(x + 11 * mm, ly, ln); ly -= 5.4 * mm
        yy = ly - 5 * mm
    c.setFillColor(MUTED); c.setFont("Body", 8)
    c.drawString(x, 12 * mm, "Plot to Plate with June  ·  plottoplatejune.co.uk  ·  For personal use: you’re welcome to give the files to the one person you bought them for.")


PAPER = {"sheet": "A4", "fold": "A5"}


def build(path, ps, sheet, fold):
    PAPER["sheet"], PAPER["fold"] = sheet, fold
    c = canvas.Canvas(path, pagesize=ps)
    c.setTitle("June's Gift Card"); c.setAuthor("Plot to Plate with June")
    pw, ph = ps
    for fn in (outside, inside, howto):
        if fn is outside:
            c.setFillColor(CREAM); c.rect(0, 0, pw / 2, ph, fill=1, stroke=0)
            c.setFillColor(GREEN); c.rect(pw / 2, 0, pw / 2, ph, fill=1, stroke=0)
        setup(c, ps); fn(c); c.showPage()
    c.save()


if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    build(f"{out}/June's Gift Card A4.pdf", landscape(A4), "A4", "A5")
    build(f"{out}/June's Gift Card US Letter.pdf", landscape(LETTER), "US Letter", "half letter")
    print("ok")
