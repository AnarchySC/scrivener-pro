import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.varLib.instancer import instantiateVariableFont

def load(path, axes=None):
    f = TTFont(path)
    if axes: f = instantiateVariableFont(f, axes)
    return f

CODEX = load(os.path.expanduser("~/.local/share/fonts/Codex-yYVPV.ttf"))
BRIC  = load("Bricolage.ttf", {"wght": 800, "opsz": 48, "wdth": 100})
MONO  = load("JetBrainsMono.ttf", {"wght": 600})

def text_path(font, text, size, x, y, track=0.0):
    """Return (svg path d, advance width, (xmin,ymin,xmax,ymax)) for text, baseline at y."""
    gs = font.getGlyphSet(); cmap = font.getBestCmap(); upm = font["head"].unitsPerEm
    s = size / upm; ds = []; cx = x; bx = [1e9, 1e9, -1e9, -1e9]
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None: continue
        pen = SVGPathPen(gs); gs[g].draw(pen); d = pen.getCommands()
        bp = BoundsPen(gs); gs[g].draw(bp)
        if d:
            ds.append(f'<path transform="translate({cx:.2f} {y:.2f}) scale({s:.5f} {-s:.5f})" d="{d}"/>')
            if bp.bounds:
                x0, y0, x1, y1 = bp.bounds
                bx = [min(bx[0], cx + x0*s), min(bx[1], y - y1*s), max(bx[2], cx + x1*s), max(bx[3], y - y0*s)]
        cx += gs[g].width * s + track * size
    return "".join(ds), cx - x - track*size, bx

AMBER, CREAM, GREY, BG = "#F2A541", "#ECE7DC", "#A9A497", "#0E1013"

def svg(w, h, body, bg=None):
    r = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">{r}{body}</svg>\n'

# --- mark: STP in Codex
m, mw, mb = text_path(CODEX, "STP", 200, 0, 0)
pad = 24; W = mb[2]-mb[0] + 2*pad; H = mb[3]-mb[1] + 2*pad
tx, ty = pad - mb[0], pad - mb[1]
mark = f'<g fill="{AMBER}" transform="translate({tx:.2f} {ty:.2f})">{m}</g>'
open("stp-mark.svg","w").write(svg(W, H, mark))
open("stp-mark-dark.svg","w").write(svg(W, H, mark, BG))

# square icon (favicon / avatar)
side = max(mb[2]-mb[0], mb[3]-mb[1]) * 1.35
ix, iy = (side-(mb[2]-mb[0]))/2 - mb[0], (side-(mb[3]-mb[1]))/2 - mb[1]
icon = f'<rect width="{side:.0f}" height="{side:.0f}" rx="{side*0.18:.0f}" fill="{BG}"/><g fill="{AMBER}" transform="translate({ix:.2f} {iy:.2f})">{m}</g>'
open("stp-icon.svg","w").write(svg(side, side, icon))

# --- horizontal lockup
mh = mb[3]-mb[1]
name, nw, nb = text_path(BRIC, "SCRIVENER", 92, 0, 0, track=0.06)
sub, sw, sb = text_path(MONO, "TECHNOLOGY PROFESSIONALS", 33.5, 0, 0, track=0.06)
gap = 44; rule = 3
lx = pad; mark_w = mb[2]-mb[0]
tx0 = lx + mark_w + gap + rule + gap
# vertically: name cap top aligns with mark top, sub baseline aligns with mark bottom
top = pad; bottom = pad + mh
name_y = top - nb[1]
sub_y = bottom - sb[3]
textw = max(nb[2], sb[2])
W2 = tx0 + textw + pad; H2 = mh + 2*pad
body = (f'<g fill="{AMBER}" transform="translate({lx - mb[0]:.2f} {top - mb[1]:.2f})">{m}</g>'
        f'<rect x="{lx + mark_w + gap:.2f}" y="{top:.2f}" width="{rule}" height="{mh:.2f}" fill="#4A4F58"/>'
        f'<g fill="{CREAM}" transform="translate({tx0:.2f} {name_y:.2f})">{name}</g>'
        f'<g fill="{GREY}" transform="translate({tx0:.2f} {sub_y:.2f})">{sub}</g>')
open("stp-lockup-dark.svg","w").write(svg(W2, H2, body, BG))
# light-background variant
bodyl = body.replace(CREAM, "#14110B").replace(GREY, "#5A564C").replace('fill="#4A4F58"', 'fill="#C9C3B6"').replace(AMBER, "#D98A1E")
open("stp-lockup-light.svg","w").write(svg(W2, H2, bodyl, "#F7F3EA"))
print("ok", round(W2), round(H2))
