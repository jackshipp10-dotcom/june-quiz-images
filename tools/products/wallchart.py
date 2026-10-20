import sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A3, A4, LETTER, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
sys.path.insert(0, os.path.dirname(__file__))
from chart_data import GROUPS, ALL_YEAR, COOK, FROST

F = "/tmp/claude-0/fonts/"
pdfmetrics.registerFont(TTFont("Head", F + "fraunces-600.ttf"))
pdfmetrics.registerFont(TTFont("Body", F + "figtree-400.ttf"))
pdfmetrics.registerFont(TTFont("BodyM", F + "figtree-500.ttf"))
pdfmetrics.registerFont(TTFont("BodyB", F + "figtree-700.ttf"))

INK = HexColor("#1F2E22")
GREEN = HexColor("#2E4733")
SAGE = HexColor("#5C7A4E")
CREAM = HexColor("#FBF7EE")
ROWALT = HexColor("#F2EDE0")
LINE = HexColor("#D9D2C0")
MUTED = HexColor("#6B7466")
TERRA = HexColor("#B4532F")

KINDS = ["I", "S", "P", "H"]
LABEL = {"I": "Sow indoors or under cover", "S": "Sow outside", "P": "Plant out", "H": "Pick and eat"}
COL = {"I": "#6F9CC2", "S": "#7FAE63", "P": "#D2805F", "H": "#E2AE3E"}
TINT = {"I": "#C4D9EB", "S": "#CDE3BF", "P": "#EFCBBC", "H": "#F5DDA0"}
GROUP_SHORT = ["SALADS", "ROOTS", "CABBAGES", "PEAS, BEANS", "TENDER", "HERBS", "FRUIT"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

W, H = 420 * mm, 297 * mm  # design canvas = A3 landscape


def setup(c, pagesize, bg=None):
    pw, ph = pagesize
    if bg is not None:
        c.setFillColor(bg); c.rect(0, 0, pw, ph, fill=1, stroke=0)
    s = min(pw / W, ph / H)
    c.translate((pw - W * s) / 2, (ph - H * s) / 2)
    c.scale(s, s)


def text_fit(c, txt, font, size, maxw):
    while pdfmetrics.stringWidth(txt, font, size) > maxw and size > 4:
        size -= 0.25
    return size


def wrap(txt, font, size, maxw):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(t, font, size) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def header(c, title, sub, low):
    top = H - 12 * mm
    if not low:
        c.setFillColor(GREEN); c.roundRect(12 * mm, top - 30 * mm, W - 24 * mm, 30 * mm, 4 * mm, fill=1, stroke=0)
        tc, sc = CREAM, HexColor("#DCE5D3")
    else:
        tc, sc = GREEN, MUTED
    c.setFillColor(sc); c.setFont("BodyB", 9); c.drawString(20 * mm, top - 8 * mm, "PLOT TO PLATE WITH JUNE")
    c.setFillColor(tc); c.setFont("Head", 27); c.drawString(20 * mm, top - 19 * mm, title)
    c.setFillColor(sc); c.setFont("Body", 11.5); c.drawString(20 * mm, top - 26 * mm, sub)
    if low:
        c.setStrokeColor(GREEN); c.setLineWidth(1.2); c.line(12 * mm, top - 30 * mm, W - 12 * mm, top - 30 * mm)
    d = 30 * mm; px = W - 12 * mm - 8 * mm - d; py = top - 30 * mm - 6 * mm
    if not low:
        c.setFillColor(CREAM); c.circle(px + d / 2, py + d / 2, d / 2 + 1.4 * mm, fill=1, stroke=0)
        c.drawImage(os.path.join(os.path.dirname(__file__), "june_circle.png"), px, py, d, d, mask="auto")
    c.setFillColor(GREEN if low else CREAM); c.setFont("Head", 11)
    return top - 30 * mm


def legend(c, y, low, x0=None):
    x = x0 or 20 * mm
    c.setFont("BodyM", 9.5)
    for k in KINDS:
        draw_bar(c, x, y - 1.2 * mm, 9 * mm, 4.4 * mm, k, low, letter=True)
        c.setFillColor(INK); c.drawString(x + 11 * mm, y + 0.2 * mm, LABEL[k])
        x += 11 * mm + pdfmetrics.stringWidth(LABEL[k], "BodyM", 9.5) + 9 * mm
    c.setFillColor(MUTED); c.setFont("Body", 9)
    c.drawString(x, y + 0.2 * mm, "Two colours in one bar: either way works, sow outside or plant out.")
    return x


def draw_bar(c, x, y, w, h, k, low, letter=False, r=None):
    r = min(r if r is not None else 1.1 * mm, h / 2)
    if low:
        c.setFillColor(HexColor(TINT[k])); c.setStrokeColor(HexColor(COL[k])); c.setLineWidth(0.6)
        c.roundRect(x, y, w, h, r, fill=1, stroke=1)
    else:
        c.setFillColor(HexColor(COL[k])); c.roundRect(x, y, w, h, r, fill=1, stroke=0)
    if letter and w >= 3.4 * mm:
        c.setFillColor(INK if low else white); c.setFont("BodyB", 7.2)
        c.drawCentredString(x + min(w, 9 * mm) / 2 if w > 12 * mm else x + w / 2, y + h / 2 - 2.5, k)


def footer(c, lines):
    c.setFillColor(MUTED); c.setFont("Body", 9.4)
    y = 8 * mm + (len(lines) - 1) * 4.2 * mm
    for ln in lines:
        c.drawString(12 * mm, y, ln); y -= 4.2 * mm
    c.setFont("BodyM", 9.4)
    c.drawRightString(W - 12 * mm, 9 * mm, "plottoplatejune.co.uk  ·  For personal use only")


def uk_chart(path, pagesize, low=False):
    c = canvas.Canvas(path, pagesize=pagesize)
    c.setTitle("June's UK Sowing and Harvest Chart"); c.setAuthor("Plot to Plate with June")
    c.setSubject("What to sow, plant and pick each month in a UK garden")
    setup(c, pagesize, None if low else CREAM)
    y = header(c, "June’s UK Sowing and Harvest Chart", "What to sow, plant out and pick, month by month, for gardens, patios and allotments across the UK", low)
    y -= 9 * mm
    legend(c, y, low)
    y -= 6 * mm

    x0 = 12 * mm; namew = 58 * mm; gx = x0 + namew; gw = W - 12 * mm - gx; cw = gw / 24
    # month header
    c.setFont("BodyB", 10)
    for i, m in enumerate(MONTHS):
        mx = gx + i * 2 * cw
        if not low and i % 2 == 0:
            pass
        c.setFillColor(GREEN); c.drawCentredString(mx + cw, y - 4 * mm, m)
    y -= 6.5 * mm
    rows = sum(len(g[1]) for g in GROUPS) + 1
    cook_h = 19 * mm; foot = 18 * mm
    avail = y - cook_h - foot
    rh = avail / rows
    table_top = y
    stripw = 7 * mm
    for gi, (gname, crops) in enumerate(GROUPS):
        gtop = y
        for i, (name, kinds) in enumerate(crops):
            if i % 2 == 0:
                c.setFillColor(ROWALT if not low else HexColor("#F4F4F1")); c.rect(x0 + stripw + 1 * mm, y - rh, W - 24 * mm - stripw - 1 * mm, rh, fill=1, stroke=0)
            c.setFillColor(INK); fs = text_fit(c, name, "BodyM", 10, namew - stripw - 4 * mm); c.setFont("BodyM", fs)
            c.drawString(x0 + stripw + 3 * mm, y - rh / 2 - 3.3, name)
            draw_crop(c, kinds, gx, y, cw, rh, low)
            y -= rh
        sc = [HexColor("#7FAE63"), HexColor("#B4532F"), HexColor("#4F7A55"), HexColor("#8E6BB0"), HexColor("#D2805F"), HexColor("#5C8F8A"), HexColor("#B8485E")][gi]
        c.setFillColor(sc if not low else white); c.setStrokeColor(sc); c.setLineWidth(0.8)
        c.roundRect(x0, y + 0.5 * mm, stripw, gtop - y - 1 * mm, 1.5 * mm, fill=1, stroke=1 if low else 0)
        c.saveState(); c.translate(x0 + stripw / 2 + 1.1 * mm, (gtop + y) / 2); c.rotate(90)
        lab = GROUP_SHORT[gi]
        c.setFillColor(white if not low else sc); c.setFont("BodyB", text_fit(c, lab, "BodyB", 8, gtop - y - 3 * mm))
        c.drawCentredString(0, 0, lab); c.restoreState()
    ay_y = y
    y -= rh
    table_bottom = y
    # vertical month lines
    c.setStrokeColor(LINE); c.setLineWidth(0.5)
    for i in range(13):
        mx = gx + i * 2 * cw
        c.line(mx, table_top, mx, table_bottom)
    c.setDash(1, 2); c.setLineWidth(0.3)
    for i in range(12):
        mx = gx + (2 * i + 1) * cw
        c.line(mx, table_top, mx, table_bottom)
    c.setDash()
    # all year row, drawn over the grid
    y = ay_y
    c.setFillColor(INK); c.setFont("BodyM", text_fit(c, ALL_YEAR[0], "BodyM", 9.6, namew - 3 * mm))
    c.drawString(x0 + 3 * mm, y - rh / 2 - 3.2, ALL_YEAR[0])
    bh = rh * 0.62
    c.setFillColor(HexColor("#E7EEE2") if not low else white); c.setStrokeColor(SAGE); c.setLineWidth(0.5)
    c.roundRect(gx + 0.6 * mm, y - rh / 2 - bh / 2, gw - 1.2 * mm, bh, 1.1 * mm, fill=1, stroke=1)
    c.setFillColor(GREEN); c.setFont("BodyM", 8.4); c.drawCentredString(gx + gw / 2, y - rh / 2 - 2.6, ALL_YEAR[1])
    # frost marker (mid to late May)
    fx = gx + 9.5 * cw
    c.setStrokeColor(HexColor("#4E7FA8")); c.setLineWidth(0.9); c.setDash(3, 2)
    c.line(fx, table_top, fx, table_bottom + rh); c.setDash()
    c.setFillColor(HexColor("#4E7FA8")); c.setFont("BodyB", 9.2)
    c.drawString(fx + 1.2 * mm, table_top + 1.2 * mm, "last frost")

    # cook strip
    y = table_bottom - 3 * mm
    ch = cook_h - 4 * mm
    if not low:
        c.setFillColor(GREEN); c.roundRect(x0, y - ch, W - 24 * mm, ch, 3 * mm, fill=1, stroke=0)
        lc, tc = HexColor("#F2D9A0"), CREAM
    else:
        c.setStrokeColor(GREEN); c.setLineWidth(0.8); c.roundRect(x0, y - ch, W - 24 * mm, ch, 3 * mm, fill=0, stroke=1)
        lc, tc = TERRA, INK
    c.setFillColor(lc); c.setFont("Head", 15); c.drawString(x0 + 5 * mm, y - ch / 2 - 1, "Cook it")
    c.setFont("Body", 8.2); c.setFillColor(tc)
    c.drawString(x0 + 5 * mm, y - ch / 2 - 5.2 * mm, "What I’d make that month")
    for i, (m, dish) in enumerate(COOK):
        mx = gx + i * 2 * cw
        lines = wrap(dish, "BodyM", 8.4, 2 * cw - 3 * mm)
        ty = y - ch / 2 + (len(lines) - 1) * 1.7 * mm - 1
        c.setFillColor(tc); c.setFont("BodyM", 8.4)
        for ln in lines:
            c.drawCentredString(mx + cw, ty, ln); ty -= 3.4 * mm
    footer(c, [
        "Dates are a guide for the middle of England. In the north and Scotland start about two weeks later; in the south and south west you can often start a little earlier.",
        "Tender crops (tomatoes, beans, courgettes, squash, sweetcorn) go outside only once your frost risk has passed, usually mid to late May. Check your seed packet for your variety.",
    ])
    c.showPage(); c.save()


def draw_crop(c, kinds, gx, ytop, cw, rh, low):
    # Lane 1: getting it going (I, S, P). Lane 2: pick and eat (H).
    pad = rh * 0.1; gap = 0.5 * mm
    lh = (rh - 2 * pad - gap) / 2
    y1 = ytop - pad - lh
    y2 = y1 - gap - lh
    act = {i: tuple(k for k in "ISP" if any(a <= i <= b for a, b in kinds.get(k, []))) for i in range(1, 26)}
    i = 1
    while i <= 24:
        st = act[i]
        if not st:
            i += 1; continue
        j = i
        while j + 1 <= 24 and act[j + 1] == st:
            j += 1
        x = gx + (i - 1) * cw + 0.4 * mm; w = (j - i + 1) * cw - 0.8 * mm
        if len(st) == 1:
            draw_bar(c, x, y1, w, lh, st[0], low)
        else:
            hh = lh / len(st)
            for n, k in enumerate(st):
                draw_bar(c, x, y1 + lh - (n + 1) * hh, w, hh, k, low, r=0.4 * mm)
        i = j + 1
    for a, b in kinds.get("H", []):
        draw_bar(c, gx + (a - 1) * cw + 0.4 * mm, y2, (b - a + 1) * cw - 0.8 * mm, lh, "H", low)


def frost_chart(path, pagesize, low=False):
    c = canvas.Canvas(path, pagesize=pagesize)
    c.setTitle("June's Sowing Chart for Any Garden"); c.setAuthor("Plot to Plate with June")
    c.setSubject("When to sow and plant, counted from your last spring frost date")
    setup(c, pagesize, None if low else CREAM)
    y = header(c, "June’s Sowing Chart for Any Garden", "When to sow and plant out, counted in weeks from your last spring frost. Works anywhere with a spring frost.", low)
    y -= 9 * mm
    kinds3 = ["I", "S", "P"]
    x = 20 * mm; c.setFont("BodyM", 9.5)
    for k in kinds3:
        draw_bar(c, x, y - 1.2 * mm, 9 * mm, 4.4 * mm, k, low, letter=True)
        c.setFillColor(INK); c.drawString(x + 11 * mm, y + 0.2 * mm, LABEL[k])
        x += 11 * mm + pdfmetrics.stringWidth(LABEL[k], "BodyM", 9.5) + 9 * mm
    c.setFillColor(MUTED); c.setFont("Body", 9)
    c.drawString(x, y + 0.2 * mm, "Two colours in one bar: either way works.  How to use it: look up your average last frost date, write it under the last frost line, then count the weeks either side.")
    y -= 7 * mm
    x0 = 12 * mm; namew = 50 * mm; notew = 82 * mm
    gx = x0 + namew; gw = W - 12 * mm - notew - 3 * mm - gx
    wk0, wk1 = -12, 20
    def wx(w): return gx + (w - wk0) / (wk1 - wk0) * gw
    # week header
    c.setFont("BodyB", 8.6); c.setFillColor(GREEN)
    for w in range(wk0, wk1 + 1, 2):
        lab = "Last frost" if w == 0 else str(abs(w))
        c.drawCentredString(wx(w), y - 3.5 * mm, lab)
    c.setFont("BodyB", 8.6)
    c.drawString(W - 12 * mm - notew + 6 * mm, y - 3.5 * mm, "WHEN TO PICK")
    c.setFont("BodyM", 9.4); c.setFillColor(MUTED)
    c.drawString(gx, y - 8 * mm, "Weeks before your last frost")
    c.drawRightString(gx + gw, y - 8 * mm, "Weeks after your last frost")
    y -= 10 * mm
    table_top = y
    foot = 22 * mm
    rh = (y - foot) / len(FROST)
    for i, (name, kinds, note) in enumerate(FROST):
        if i % 2 == 0:
            c.setFillColor(ROWALT if not low else HexColor("#F6F6F4")); c.rect(x0, y - rh, W - 24 * mm, rh, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("BodyM", text_fit(c, name, "BodyM", 9.4, namew - 3 * mm))
        c.drawString(x0 + 2 * mm, y - rh / 2 - 3.1, name)
        lh = rh * 0.42; ly = y - rh / 2 - lh / 2
        act = {w: tuple(k for k in kinds3 if any(a <= w <= b for a, b in kinds.get(k, []))) for w in range(wk0, wk1 + 2)}
        w = wk0
        while w <= wk1:
            st = act[w]
            if not st:
                w += 1; continue
            e = w
            while e + 1 <= wk1 and act[e + 1] == st:
                e += 1
            bx = wx(w) + 0.4 * mm; bw = wx(e + 1) - wx(w) - 0.8 * mm
            if len(st) == 1:
                draw_bar(c, bx, ly, bw, lh, st[0], low)
            else:
                hh = lh / len(st)
                for n, k in enumerate(st):
                    draw_bar(c, bx, ly + lh - (n + 1) * hh, bw, hh, k, low, r=0.4 * mm)
            w = e + 1
        c.setFillColor(INK); c.setFont("Body", text_fit(c, note, "Body", 8.6, notew - 8 * mm))
        c.drawString(W - 12 * mm - notew + 6 * mm, y - rh / 2 - 3, note)
        y -= rh
    table_bottom = y
    c.setStrokeColor(LINE); c.setLineWidth(0.4)
    for w in range(wk0, wk1 + 1, 2):
        c.line(wx(w), table_top, wx(w), table_bottom)
    c.setStrokeColor(HexColor("#4E7FA8")); c.setLineWidth(1.2)
    c.line(wx(0), table_top + 1 * mm, wx(0), table_bottom)
    c.setFillColor(HexColor("#4E7FA8")); c.setFont("BodyB", 8)
    c.drawCentredString(wx(0), table_bottom - 4 * mm, "My last frost date: ____________")
    footer(c, [
        "Find your average last spring frost date online (search “last frost date” with your town or postcode). In much of the UK it falls between mid April and late May.",
        "Frost tender crops (tomatoes, beans, courgettes, squash, sweetcorn, basil) go outside only after it. Timings are a general guide; your seed packet has the final word.",
    ])
    c.showPage(); c.save()


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    sizes = {"A3": landscape(A3), "A4": landscape(A4), "US Letter": landscape(LETTER)}
    for sname, ps in sizes.items():
        for low in (False, True):
            tag = " low ink" if low else ""
            uk_chart(f"{out}/UK Sowing and Harvest Chart {sname}{tag}.pdf", ps, low)
            frost_chart(f"{out}/Any Garden Sowing Chart {sname}{tag}.pdf", ps, low)
    print("done")
