# Simple hand drawn style illustrations for the Gardener Level Test tiles.
# Each is an inline SVG on a 160x120 paper panel. Strokes in ink, fills in garden colours.

INK = "#1D2E21"
SOIL = "#8A6646"
SOIL_LIGHT = "#B48B62"


def _wrap(inner):
    return f'<svg viewBox="0 0 160 120" role="img" aria-hidden="true" focusable="false"><rect width="160" height="120" fill="#EDE5CF"/>{inner}</svg>'


def _soil():
    return (f'<path d="M0 62 Q40 56 80 61 T160 60 V120 H0Z" fill="{SOIL}"/>'
            f'<path d="M0 62 Q40 56 80 61 T160 60" fill="none" stroke="{INK}" stroke-width="2"/>'
            f'<g fill="{SOIL_LIGHT}"><circle cx="22" cy="84" r="2"/><circle cx="118" cy="100" r="2.5"/><circle cx="140" cy="76" r="1.8"/><circle cx="36" cy="108" r="2"/></g>')


def _clove(rot):
    # pointy end up by default; rot=180 flips it
    return (f'<g transform="rotate({rot} 80 70)">'
            f'<path d="M80 38 C92 52 98 74 92 96 Q80 101 68 96 C62 74 68 52 80 38Z" fill="#F6F0E2" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<path d="M80 44 C84 60 85 80 82 95" fill="none" stroke="#C9B9A0" stroke-width="2"/>'
            f'<path d="M69 96 Q80 92 91 96" fill="none" stroke="#C4A27A" stroke-width="3"/></g>')


def garlic(up):
    return _wrap(_soil() + _clove(0 if up else 180))


def courgette(cm):
    # ruler 0 to 40cm across x 16..144 (3.2px per cm)
    x0, k = 16, 3.2
    ticks = "".join(
        f'<line x1="{x0 + i * k:.1f}" y1="92" x2="{x0 + i * k:.1f}" y2="{84 if i % 10 == 0 else (87 if i % 5 == 0 else 89)}" stroke="{INK}" stroke-width="1"/>'
        for i in range(0, 41))
    nums = "".join(f'<text x="{x0 + n * k:.1f}" y="104" font-size="8" text-anchor="middle" fill="{INK}" font-family="Work Sans,Arial,sans-serif">{n}</text>' for n in (0, 10, 20, 30, 40))
    ruler = f'<rect x="8" y="80" width="144" height="28" rx="3" fill="#E7C977" stroke="{INK}" stroke-width="1.5"/>{ticks}{nums}'
    L = cm * k
    h = 8 + cm * 0.45  # thicker as it grows
    cy = 60
    body = (f'<path d="M{x0} {cy} C{x0} {cy - h / 2} {x0 + L - 6} {cy - h / 2} {x0 + L} {cy - h / 2 + 2} '
            f'Q{x0 + L + 4} {cy} {x0 + L} {cy + h / 2 - 2} C{x0 + L - 6} {cy + h / 2} {x0} {cy + h / 2} {x0} {cy}Z" '
            f'fill="#3F6B3A" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>')
    shine = f'<path d="M{x0 + 4} {cy - h / 4} Q{x0 + L / 2} {cy - h / 2 + 1} {x0 + L - 6} {cy - h / 4}" fill="none" stroke="#7FA36E" stroke-width="1.6" stroke-linecap="round"/>'
    stalk = f'<path d="M{x0} {cy} l-7 -3 v6z" fill="#6E8B4E" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>'
    return _wrap(body + shine + stalk + ruler)


def _flower(cx, cy):
    petals = "".join(
        f'<ellipse cx="{cx}" cy="{cy - 15}" rx="8" ry="15" fill="#F3B526" stroke="{INK}" stroke-width="1.8" transform="rotate({a} {cx} {cy})"/>'
        for a in (0, 72, 144, 216, 288))
    return petals + f'<circle cx="{cx}" cy="{cy}" r="6" fill="#E08A1E" stroke="{INK}" stroke-width="1.5"/>'


def flower(male):
    cx, cy = 116, 54
    if male:
        stem = f'<path d="M14 96 C50 92 80 80 {cx - 18} {cy + 6}" fill="none" stroke="#6E8B4E" stroke-width="3.5" stroke-linecap="round"/>'
        stem += f'<path d="M14 96 C50 92 80 80 {cx - 18} {cy + 6}" fill="none" stroke="{INK}" stroke-width="1" stroke-linecap="round" opacity=".5"/>'
        base = f'<path d="M{cx - 22} {cy + 8} q8 -10 16 -6" fill="#6E8B4E" stroke="{INK}" stroke-width="1.5"/>'
    else:
        stem = f'<path d="M14 96 C26 94 32 90 40 86" fill="none" stroke="#6E8B4E" stroke-width="4" stroke-linecap="round"/>'
        # baby courgette between stalk and flower
        base = (f'<path d="M38 86 C50 74 80 62 {cx - 16} {cy + 4} Q{cx - 10} {cy + 12} {cx - 18} {cy + 16} C86 76 56 92 42 94 Q34 92 38 86Z" '
                f'fill="#3F6B3A" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
                f'<path d="M48 84 Q76 72 {cx - 22} {cy + 8}" fill="none" stroke="#7FA36E" stroke-width="1.5" stroke-linecap="round"/>')
    return _wrap(stem + base + _flower(cx, cy))


SVGS = {
    "garlic_up": garlic(True), "garlic_down": garlic(False),
    "courgette_5": courgette(5), "courgette_11": courgette(11), "courgette_25": courgette(25), "courgette_40": courgette(40),
    "flower_male": flower(True), "flower_female": flower(False),
}
