"""
Builds the README and Store screenshots (docs/images/store-<n>.png) from the sandbox captures in
docs/images/captures/ (pwsh scripts/capture-screenshots.ps1) and the pictures in docs/images/assets/.

Cards and windows come from the real captures; the captions, callouts, the pasted notes, the picture menu and the
taskbar are drawn here. Needs Pillow:  python scripts/compose-store-images.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
repo = str(Path(__file__).resolve().parent.parent)
out = repo + '/docs/images'
assets = repo + '/docs/images/assets'
F = 'C:/Windows/Fonts/'
def font(n, s): return ImageFont.truetype(F + n, s)
BG = (220, 230, 242)
ACCENT = (0, 103, 192)

class Grid:
    def __init__(self, xs, ys, card, dark):
        self.xs, self.ys, self.card, self.dark = xs, ys, card, dark
        self.k = card / 75
    def box(self, c0, r0, c1=None, r1=None):
        c1 = c0 if c1 is None else c1; r1 = r0 if r1 is None else r1
        return (self.xs[c0], self.ys[r0], self.xs[c1] + self.card, self.ys[r1] + self.card)

LIGHT = Grid([763, 844, 924, 1005, 1085], [221, 302, 383, 463], 75, False)
DARK = Grid([663, 738, 813, 888, 963], [234, 309, 383, 458], 67, True)

def text_block(im, title, body, clear=700):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, clear, 768], fill=BG)
    tf, bf = font('seguisb.ttf', 37), font('segoeui.ttf', 20)
    def wrap(text, f, width):
        lines, line = [], ''
        for w in text.split():
            t = (line + ' ' + w).strip()
            if d.textlength(t, font=f) > width: lines.append(line); line = w
            else: line = t
        return lines + [line]
    tl, bl = wrap(title, tf, 520), wrap(body, bf, 520)
    y = (768 - (len(tl) * 48 + 18 + len(bl) * 30)) // 2
    for l in tl: d.text((72, y), l, font=tf, fill=(27, 27, 31)); y += 48
    y += 18
    for l in bl: d.text((72, y), l, font=bf, fill=(74, 79, 90)); y += 30

def chip(im, label, at, to, vertical=False):
    d = ImageDraw.Draw(im)
    f = font('seguisb.ttf', 15)
    w = d.textlength(label, font=f) + 24
    x, y = at
    start = (x + w / 2, y + (28 if to[1] > y else 0)) if vertical else (x + (w if to[0] > x else 0), y + 14)
    d.line([to, start], fill=ACCENT, width=2)
    d.ellipse([to[0] - 4, to[1] - 4, to[0] + 4, to[1] + 4], fill=ACCENT)
    d.rounded_rectangle([x, y, x + w, y + 28], 14, fill=ACCENT)
    d.text((x + 12, y + 4), label, font=f, fill='white')

def card_bg(src, g, c, r):
    return src.getpixel((g.xs[c] + 4, g.ys[r] + g.card - 6))

def relabel(im, src, g, c, r, label, bg_cell=None):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = g.box(c, r)
    bg = card_bg(src, g, *(bg_cell or (c, r)))
    d.rectangle([x0 + 3, y0 + int(48 * g.k), x1 - 3, y1 - 4], fill=bg)
    f = font('segoeui.ttf', max(11, round(12 * g.k)))
    tw = d.textlength(label, font=f)
    d.text(((x0 + x1 - tw) / 2, y0 + int(50 * g.k)), label, font=f, fill=(240, 240, 240) if g.dark else (26, 26, 26))

def site_tile(im, src, g, cell, frm_bg, domain):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = g.box(*cell)
    im.paste(src.crop(g.box(*frm_bg)), (x0, y0))
    bg = card_bg(src, g, *frm_bg)
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 4], fill=bg)
    size = round(34 * g.k)
    icon = Image.open(f'{assets}/fav-{domain}.png').convert('RGBA').resize((size, size), Image.LANCZOS)
    m = Image.new('L', icon.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, size, size], round(6 * g.k), fill=255)
    a = Image.composite(icon, Image.new('RGBA', icon.size, (0, 0, 0, 0)), m)
    im.paste(a, ((x0 + x1 - size) // 2, y0 + round(10 * g.k)), a)
    relabel(im, src, g, cell[0], cell[1], domain, bg_cell=frm_bg)

def photo_card(im, box, fill, name='photo-fjord.jpg'):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, 6, fill=fill)
    p = ImageOps.fit(Image.open(f'{assets}/{name}').convert('RGB'), (x1 - x0 - 8, y1 - y0 - 8))
    m = Image.new('L', p.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, *p.size], 4, fill=255)
    im.paste(p, (x0 + 4, y0 + 4), m)

def note_card(im, g, box, lines, size=14):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, 6, fill=(67, 53, 25) if g.dark else (255, 244, 206))
    f = font('segoeui.ttf', round(size * g.k))
    for i, line in enumerate(lines):
        d.text((x0 + 10, y0 + 10 + i * round(20 * g.k)), line, font=f, fill=(240, 240, 240) if g.dark else (26, 26, 26))

def menu(im, at, items):
    x, y = at
    w, row = 170, 34
    h = sum(8 if it is None else row for it in items) + 8
    shadow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([x, y + 6, x + w, y + h + 6], 8, fill=(0, 0, 0, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    base = im.convert('RGBA'); base.alpha_composite(shadow); im.paste(base.convert('RGB'))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x, y, x + w, y + h], 8, fill=(249, 249, 249), outline=(222, 222, 222))
    gf, tf = font('SegoeIcons.ttf', 16), font('segoeui.ttf', 15)
    cy = y + 4
    for it in items:
        if it is None:
            d.line([x + 1, cy + 4, x + w - 1, cy + 4], fill=(230, 230, 230)); cy += 8; continue
        glyph, text, sub = it
        d.text((x + 14, cy + 8), glyph, font=gf, fill=(26, 26, 26))
        d.text((x + 44, cy + 6), text, font=tf, fill=(26, 26, 26))
        if sub: d.text((x + w - 24, cy + 10), '\ue76c', font=font('SegoeIcons.ttf', 12), fill=(90, 90, 90))
        cy += row

def hero(src, g, card_fill):
    im = src.copy(); d = ImageDraw.Draw(im)
    x0, y0, _, _ = g.box(0, 0); _, _, x1, y1 = g.box(4, 3)
    grid_bg = src.getpixel((g.xs[0] - 3, g.ys[1] + 30))
    keep = {c: src.crop(g.box(*c)) for c in [(0, 0), (2, 2), (3, 2), (1, 1), (0, 1)]}
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], fill=grid_bg)
    for to, frm in [((0, 0), (0, 0)), ((1, 0), (2, 2)), ((2, 0), (3, 2)), ((3, 0), (1, 1)), ((4, 0), (0, 1))]:
        im.paste(keep[frm], g.box(*to)[:2])
    relabel(im, src, g, 4, 0, 'Documents', bg_cell=(0, 0))
    for c, domain in enumerate(['imdb.com', 'wikipedia.org', 'booking.com', 'weather.com', 'nytimes.com']):
        site_tile(im, src, g, (c, 3), (0, 0), domain)
    photo_card(im, g.box(0, 1, 2, 2), card_fill)
    note_card(im, g, g.box(3, 1, 4, 2), ['Call Sam back:', 'invoice is €240 off', '', 'Parcel 4417-2291', 'collect by Fri 18:00'])
    return im


EDGE_ICON = LIGHT.box(0, 0)
def taskbar(im, dark=False):
    """A Windows 11 style taskbar along the bottom, so the widget reads as sitting on the desktop."""
    W, H = im.size
    top = H - 48
    bar = (32, 32, 32) if dark else (238, 242, 248)
    line = (60, 60, 60) if dark else (210, 216, 226)
    fg = (240, 240, 240) if dark else (26, 26, 26)
    d = ImageDraw.Draw(im)
    d.rectangle([0, top, W, H], fill=bar)
    d.line([0, top, W, top], fill=line)
    cx = W // 2 - 130
    # Start button.
    for dx in (0, 11):
        for dy in (0, 11):
            d.rectangle([cx + dx, top + 14 + dy, cx + dx + 9, top + 23 + dy], fill=(0, 120, 212))
    # Search box.
    sx = cx + 38
    d.rounded_rectangle([sx, top + 9, sx + 150, top + 39], 15, fill=(60, 60, 60) if dark else (255, 255, 255), outline=line)
    d.text((sx + 12, top + 14), '', font=font('SegoeIcons.ttf', 15), fill=fg)
    d.text((sx + 36, top + 12), 'Search', font=font('segoeui.ttf', 15), fill=(160, 160, 160) if dark else (110, 110, 110))
    # Pinned apps, cut from the widget's own card icons.
    src = Image.open(repo + '/docs/images/captures/showcase-1.png').convert('RGB')
    x = sx + 168
    for c, r in [(0, 0), (2, 2), (1, 1)]:
        bx0, by0, _, _ = LIGHT.box(c, r)
        icon = src.crop((bx0 + 20, by0 + 8, bx0 + 56, by0 + 44)).convert('RGBA')
        px = icon.load()
        for yy in range(icon.size[1]):
            for xx in range(icon.size[0]):
                rr, gg, bb, _ = px[xx, yy]
                if rr > 245 and gg > 245 and bb > 245: px[xx, yy] = (0, 0, 0, 0)
        icon = icon.resize((26, 26), Image.LANCZOS)
        im.paste(icon, (x, top + 11), icon)
        x += 44
    # Clock.
    f = font('segoeui.ttf', 12)
    for i, t in enumerate(['10:30', '18/11/2026']):
        tw = d.textlength(t, font=f)
        d.text((W - 16 - tw, top + 7 + i * 17), t, font=f, fill=fg)
    d.text((W - 150, top + 15), '      ', font=font('SegoeIcons.ttf', 14), fill=fg)

# 1. Everything together, with the photo's menu open.
src = Image.open(repo + '/docs/images/captures/showcase-1.png').convert('RGB')
im = hero(src, LIGHT, (255, 255, 255))
text_block(im, 'Everything you love, one click away',
           'Your apps, favourite websites, notes and photos, together on your desktop.')
chip(im, 'Apps', (650, LIGHT.ys[0] + 22), (LIGHT.xs[0], LIGHT.ys[0] + 37))
chip(im, 'Photos', (640, LIGHT.ys[1] + 66), (LIGHT.xs[0], LIGHT.ys[1] + 80))
chip(im, 'Websites', (636, LIGHT.ys[3] + 22), (LIGHT.xs[0], LIGHT.ys[3] + 37))
chip(im, 'Notes', (1190, LIGHT.ys[1] + 30), (LIGHT.xs[4] + 75, LIGHT.ys[1] + 44))
taskbar(im)
im.save(out + '/store-1.png')

# 2. Copy anything, Ctrl+V, saved.
def highlight(im, box, label):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], 9, outline=ACCENT, width=3)
    f = font('seguisb.ttf', 12)
    w = d.textlength(label, font=f) + 14
    cx = (x0 + x1) / 2
    d.rounded_rectangle([cx - w / 2, y0 - 13, cx + w / 2, y0 + 7], 10, fill=ACCENT)
    d.text((cx - w / 2 + 7, y0 - 11), label, font=f, fill='white')

def keycap(d, x, y, text, w):
    d.rounded_rectangle([x, y + 4, x + w, y + 64], 10, fill=(170, 182, 200))
    d.rounded_rectangle([x, y, x + w, y + 58], 10, fill=(255, 255, 255), outline=(190, 200, 215), width=2)
    f = font('seguisb.ttf', 26)
    tw = d.textlength(text, font=f)
    d.text((x + (w - tw) / 2, y + 12), text, font=f, fill=(27, 27, 31))

src = Image.open(repo + '/docs/images/captures/showcase-1.png').convert('RGB')
im = src.copy(); d = ImageDraw.Draw(im)
g = LIGHT
keep = {c: src.crop(g.box(*c)) for c in [(0, 0), (3, 2), (2, 2)]}
x0, y0, _, _ = g.box(0, 0); _, _, x1, y1 = g.box(4, 3)
d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], fill=src.getpixel((g.xs[0] - 3, g.ys[1] + 30)))
photo_card(im, g.box(0, 0, 2, 1), (255, 255, 255), 'photo-valley.jpg')
note_card(im, g, g.box(3, 0, 4, 1), ['Kind regards,', 'Alex Morgan', 'Northwind Studio', '+44 20 7946 0958'])
photo_card(im, g.box(0, 2, 2, 3), (255, 255, 255))
for to, frm in [((3, 2), (0, 0)), ((4, 2), (3, 2)), ((3, 3), (2, 2))]:
    im.paste(keep[frm], g.box(*to)[:2])
site_tile(im, src, g, (4, 3), (0, 0), 'imdb.com')
highlight(im, g.box(0, 0, 2, 1), 'Ctrl+V')
highlight(im, g.box(3, 0, 4, 1), 'Ctrl+V')
highlight(im, g.box(4, 3), 'Ctrl+V')
menu(im, (840, 430), [('', 'Copy image', False), ('', 'Edit in Paint', False), None,
                      ('', 'Move to', True), ('', 'Delete', False)])

d = ImageDraw.Draw(im)
d.rectangle([0, 0, 700, 768], fill=BG)
tf, bf = font('seguisb.ttf', 40), font('segoeui.ttf', 20)
d.text((72, 200), 'Copy it. Ctrl+V.', font=tf, fill=(27, 27, 31))
d.text((72, 250), 'Saved in a second.', font=tf, fill=ACCENT)
for i, line in enumerate(['A picture, some text or a web link: copy it,',
                          'press Ctrl+V on the widget and it is there.',
                          'Right-click a picture to copy it again or',
                          'edit it in Paint.']):
    d.text((72, 320 + i * 30), line, font=bf, fill=(74, 79, 90))
keycap(d, 72, 470, 'Ctrl', 96)
d.text((184, 482), '+', font=font('seguisb.ttf', 30), fill=(74, 79, 90))
keycap(d, 214, 470, 'V', 64)
f = font('segoeui.ttf', 18)
for i, (glyph, label) in enumerate([('', 'Picture'), ('', 'Text'), ('', 'Link')]):
    x = 310 + i * 100
    d.text((x, 484), glyph, font=font('SegoeIcons.ttf', 20), fill=ACCENT)
    d.text((x + 28, 480), label, font=f, fill=(27, 27, 31))

chip(im, 'Picture', (640, g.ys[0] + 62), (g.xs[0] - 3, g.ys[0] + 76))
chip(im, 'Text', (1190, g.ys[0] + 62), (g.xs[4] + 78, g.ys[0] + 76))
chip(im, 'Link', (1190, g.ys[3] + 22), (g.xs[4] + 78, g.ys[3] + 36))
chip(im, 'Right-click', (630, g.ys[2] + 62), (g.xs[0] - 3, g.ys[2] + 76))
taskbar(im)
im.save(out + '/store-2.png')

# 3. Always at hand: the compact icon next to the open widget (dark).
src = Image.open(repo + '/docs/images/captures/showcase-5.png').convert('RGB')
im = hero(src, DARK, (44, 44, 44))
text_block(im, 'Always at hand, always on top',
           'Tuck the widget into a small icon on your desktop and open everything with one click.', clear=600)
# The compact icon moves to the top right; an arrow shows the widget opening out of it.
icon = src.crop((1199, 343, 1278, 422))
ImageDraw.Draw(im).rectangle([1140, 300, 1366, 500], fill=BG)
shadow = Image.new('RGBA', im.size, (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle([1200, 58, 1279, 137], 6, fill=(0, 0, 0, 90))
shadow = shadow.filter(ImageFilter.GaussianBlur(8))
base = im.convert('RGBA'); base.alpha_composite(shadow); im.paste(base.convert('RGB'))
im.paste(icon, (1200, 52))
d = ImageDraw.Draw(im)
start, end = (1198, 132), (1062, 196)
d.line([start, end], fill=ACCENT, width=4)
import math
ang = math.atan2(end[1] - start[1], end[0] - start[0])
head = [end, (end[0] - 18 * math.cos(ang - 0.45), end[1] - 18 * math.sin(ang - 0.45)),
        (end[0] - 18 * math.cos(ang + 0.45), end[1] - 18 * math.sin(ang + 0.45))]
d.polygon(head, fill=ACCENT)
label = 'Click to expand'
lf = font('seguisb.ttf', 18)
txt = Image.new('RGBA', (int(d.textlength(label, font=lf)) + 8, 30), (0, 0, 0, 0))
ImageDraw.Draw(txt).text((4, 2), label, font=lf, fill=ACCENT)
txt = txt.rotate(-math.degrees(ang) + 180, expand=True, resample=Image.BICUBIC)
mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
im.paste(txt, (int(mx - txt.size[0] / 2) + 6, int(my - txt.size[1] / 2) - 22), txt)
taskbar(im, dark=True)
im.save(out + '/store-3.png')
print('Wrote', out + '/store-1.png … store-3.png')
