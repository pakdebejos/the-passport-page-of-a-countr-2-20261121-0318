#!/usr/bin/env python3
"""Entry for make.fun the-passport-page-of-a-countr-2-20261121-0318: Sultanate of Qamar.

Pure standard library (struct, zlib, os). Draws a 1024x1024 invented
passport spread — data page with portrait and machine-readable strip,
arrival and departure stamps from neighbouring countries, and one detail
of paperwork that reveals the place — and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png). Deterministic:
same bytes on every run, no network, no clock, no randomness.
"""

import os

import struct, zlib

W, H = 1024, 1024

def g(*rows):
    return [int(r.replace('#', '1').replace('.', '0'), 2) for r in rows]

FONT = {
 'A': g('01110','10001','10001','11111','10001','10001','10001'),
 'B': g('11110','10001','10001','11110','10001','10001','11110'),
 'C': g('01110','10001','10000','10000','10000','10001','01110'),
 'D': g('11110','10001','10001','10001','10001','10001','11110'),
 'E': g('11111','10000','10000','11110','10000','10000','11111'),
 'F': g('11111','10000','10000','11110','10000','10000','10000'),
 'G': g('01110','10001','10000','10111','10001','10001','01111'),
 'H': g('10001','10001','10001','11111','10001','10001','10001'),
 'I': g('01110','00100','00100','00100','00100','00100','01110'),
 'J': g('00111','00010','00010','00010','00010','10010','01100'),
 'K': g('10001','10010','10100','11000','10100','10010','10001'),
 'L': g('10000','10000','10000','10000','10000','10000','11111'),
 'M': g('10001','11011','10101','10101','10001','10001','10001'),
 'N': g('10001','11001','10101','10011','10001','10001','10001'),
 'O': g('01110','10001','10001','10001','10001','10001','01110'),
 'P': g('11110','10001','10001','11110','10000','10000','10000'),
 'Q': g('01110','10001','10001','10001','10101','10010','01101'),
 'R': g('11110','10001','10001','11110','10100','10010','10001'),
 'S': g('01111','10000','10000','01110','00001','00001','11110'),
 'T': g('11111','00100','00100','00100','00100','00100','00100'),
 'U': g('10001','10001','10001','10001','10001','10001','01110'),
 'V': g('10001','10001','10001','10001','10001','01010','00100'),
 'W': g('10001','10001','10001','10101','10101','11011','10001'),
 'X': g('10001','10001','01010','00100','01010','10001','10001'),
 'Y': g('10001','10001','01010','00100','00100','00100','00100'),
 'Z': g('11111','00001','00010','00100','01000','10000','11111'),
 '0': g('01110','10001','10011','10101','11001','10001','01110'),
 '1': g('00100','01100','00100','00100','00100','00100','01110'),
 '2': g('01110','10001','00001','00110','01000','10000','11111'),
 '3': g('11111','00010','00100','00010','00001','10001','01110'),
 '4': g('00010','00110','01010','10010','11111','00010','00010'),
 '5': g('11111','10000','11110','00001','00001','10001','01110'),
 '6': g('00110','01000','10000','11110','10001','10001','01110'),
 '7': g('11111','00001','00010','00100','01000','01000','01000'),
 '8': g('01110','10001','10001','01110','10001','10001','01110'),
 '9': g('01110','10001','10001','01111','00001','00010','01100'),
 ' ': g('00000','00000','00000','00000','00000','00000','00000'),
 '.': g('00000','00000','00000','00000','00000','01100','01100'),
 ',': g('00000','00000','00000','00000','01100','00100','01000'),
 ':': g('00000','01100','01100','00000','01100','01100','00000'),
 ';': g('00000','01100','01100','00000','01100','00100','01000'),
 '!': g('00100','00100','00100','00100','00100','00000','00100'),
 '?': g('01110','10001','00001','00110','00100','00000','00100'),
 "'": g('00100','00100','01000','00000','00000','00000','00000'),
 '-': g('00000','00000','00000','01110','00000','00000','00000'),
 '/': g('00001','00010','00010','00100','01000','01000','10000'),
 '(': g('00010','00100','01000','01000','01000','00100','00010'),
 ')': g('01000','00100','00010','00010','00010','00100','01000'),
 '&': g('01100','10010','10100','01000','10101','10010','01101'),
 '%': g('11001','11010','00010','00100','01000','01011','10011'),
 '+': g('00000','00100','00100','01110','00100','00100','00000'),
 '=': g('00000','00000','11111','00000','11111','00000','00000'),
 '*': g('00000','00100','10101','01110','10101','00100','00000'),
 '>': g('10000','01000','00100','00010','00100','01000','10000'),
 '<': g('00001','00010','00100','01000','00100','00010','00001'),
}

def text_width(s, scale):
    return sum(6 for _ in s) * scale - scale

def wrap(text, scale, max_w):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if text_width(t, scale) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

class Canvas:
    def __init__(self, w=W, h=H, bg=(247, 243, 234)):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))
    def _set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i+3] = bytes(c)
    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self._set(xx, yy, c)
    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)
    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)
    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self._set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy; x0 += sx
            if e2 < dx:
                err += dx; y0 += sy
    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d <= r * r:
                    self._set(xx, yy, c)
                elif not fill and abs(d - r * r) <= r:
                    self._set(xx, yy, c)
    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) ** 2) / (rx * rx) + ((yy - cy) ** 2) / (ry * ry) <= 1:
                    self._set(xx, yy, c)
    def text(self, x, y, s, color, scale, align='left'):
        s = s.upper()
        w = text_width(s, scale)
        if align == 'center':
            x -= w // 2
        elif align == 'right':
            x -= w
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale, scale, scale, color)
            cx += 6 * scale
        return y + 7 * scale
    def para(self, x, y, s, color, scale, max_w, leading=None):
        lines = wrap(s, scale, max_w)
        lh = leading if leading else 9 * scale
        for ln in lines:
            self.text(x, y, ln, color, scale)
            y += lh
        return y
    def png(self):
        raw = bytearray()
        stride = self.w * 3
        for yy in range(self.h):
            raw.append(0)
            raw += self.px[yy * stride:(yy + 1) * stride]
        def chunk(tag, data):
            c = struct.pack('>I', len(data)) + tag + data
            return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        ihdr = struct.pack('>IIBBBBB', self.w, self.h, 8, 2, 0, 0, 0)
        return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
                + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
                + chunk(b'IEND', b''))

# --- passport helpers ------------------------------------------------------
def portrait(c, x, y, w, h, skin, hair, shirt, jacket, style='male'):
    """Stylised passport photo: head, hair, shoulders. style: male/female/beard."""
    c.rect(x, y, w, h, (198, 210, 220))
    cx = x + w // 2
    hy = y + int(h * 0.40)
    # shoulders / jacket
    c.rect(x + 8, y + h - 46, w - 16, 46, jacket)
    c.rect(cx - 26, y + h - 46, 52, 46, shirt)
    c.line(cx - 26, y + h - 46, cx, y + h - 20, jacket, 3)
    c.line(cx + 26, y + h - 46, cx, y + h - 20, jacket, 3)
    # neck
    c.rect(cx - 13, hy + 34, 26, 22, skin)
    # head
    c.ellipse(cx, hy, 36, 46, skin)
    # ears
    c.rect(cx - 40, hy - 6, 6, 16, skin)
    c.rect(cx + 34, hy - 6, 6, 16, skin)
    if style == 'female':
        # long hair framing the face
        c.ellipse(cx, hy - 14, 42, 34, hair)
        c.rect(cx - 42, hy - 10, 12, 78, hair)
        c.rect(cx + 30, hy - 10, 12, 78, hair)
        c.ellipse(cx, hy - 26, 36, 18, hair)
        c.ellipse(cx, hy + 6, 37, 40, skin)
    elif style == 'beard':
        c.ellipse(cx, hy - 16, 39, 30, hair)
        c.ellipse(cx, hy - 28, 36, 16, hair)
        # beard over lower face
        c.ellipse(cx, hy + 26, 34, 26, hair)
        c.ellipse(cx, hy + 8, 36, 30, skin)
        # white headcloth band
        c.rect(cx - 38, hy - 44, 76, 10, (245, 245, 240))
    else:
        c.ellipse(cx, hy - 16, 39, 30, hair)
        c.ellipse(cx, hy - 28, 36, 16, hair)
        c.ellipse(cx, hy + 4, 37, 40, skin)
    # brows, eyes, nose, mouth
    c.rect(cx - 20, hy - 8, 14, 3, hair)
    c.rect(cx + 6, hy - 8, 14, 3, hair)
    c.rect(cx - 17, hy - 2, 9, 4, (30, 30, 30))
    c.rect(cx + 8, hy - 2, 9, 4, (30, 30, 30))
    c.line(cx, hy + 2, cx - 2, hy + 16, (150, 110, 90), 2)
    c.line(cx - 9, hy + 26, cx + 9, hy + 26, (140, 70, 60), 2)

def stamp_rect(c, x, y, w, h, color, lines, scale=1):
    c.rect(x, y, w, 2, color)
    c.rect(x, y + h - 2, w, 2, color)
    c.rect(x, y, 2, h, color)
    c.rect(x + w - 2, y, 2, h, color)
    c.rect(x + 5, y + 5, w - 10, 1, color)
    c.rect(x + 5, y + h - 6, w - 10, 1, color)
    c.rect(x + 5, y + 5, 1, h - 10, color)
    c.rect(x + w - 6, y + 5, 1, h - 10, color)
    yy = y + 12
    for ln in lines:
        c.text(x + w // 2, yy, ln, color, scale, 'center')
        yy += 7 * scale + 4

def stamp_circle(c, cx, cy, r, color, lines, scale=1):
    c.circle(cx, cy, r, color, fill=False)
    c.circle(cx, cy, r - 5, color, fill=False)
    yy = cy - (len(lines) * (7 * scale + 3)) // 2
    for ln in lines:
        c.text(cx, yy, ln, color, scale, 'center')
        yy += 7 * scale + 3

def field(c, x, y, label, value, ink, grey, vscale=2):
    c.text(x, y, label, grey, 1)
    c.text(x, y + 11, value, ink, vscale)
    return y + 11 + 7 * vscale + 10

def frame(c, ink, accent):
    c.rect(6, 6, 1012, 3, ink)
    c.rect(6, 1015, 1012, 3, ink)
    c.rect(6, 6, 3, 1012, ink)
    c.rect(1015, 6, 3, 1012, ink)
    c.rect(16, 16, 992, 1, accent)
    c.rect(16, 1007, 992, 1, accent)
    c.rect(16, 16, 1, 992, accent)
    c.rect(1007, 16, 1, 992, accent)

# --- palette ---------------------------------------------------------------
INK    = (28, 20, 20)
PAPER  = (250, 244, 230)
BURG   = (122, 28, 44)
GOLD   = (201, 162, 39)
GREY   = (112, 105, 95)
GREEN  = (40, 110, 70)
BLUE   = (40, 80, 140)
CREAM  = (255, 248, 220)
RED    = (178, 34, 34)

def emblem_crescent(c, cx, cy, r, col):
    c.circle(cx, cy, r, col, fill=False)
    c.circle(cx, cy, r - 4, col, fill=False)
    c.circle(cx - 4, cy, r - 12, col)
    c.circle(cx + 6, cy - 2, r - 12, PAPER)
    c.circle(cx + 16, cy - 16, 4, col)
    for dx, dy in ((0, -9), (7, -6), (9, 0), (7, 6), (0, 9),
                   (-7, 6), (-9, 0), (-7, -6)):
        c.line(cx + 16, cy - 16, cx + 16 + dx, cy - 16 + dy, col, 2)

def draw_image():
    c = Canvas()
    frame(c, INK, GOLD)
    # ornate corners
    for cx, cy in ((40, 40), (984, 40), (40, 984), (984, 984)):
        c.rect(cx - 8, cy - 2, 16, 4, GOLD)
        c.rect(cx - 2, cy - 8, 4, 16, GOLD)
    # header: burgundy rules, gold rules
    emblem_crescent(c, 72, 66, 36, BURG)
    c.text(512, 30, 'SULTANATE OF QAMAR', BURG, 5, 'center')
    c.text(512, 78, 'PASSPORT', GOLD, 3, 'center')
    c.text(512, 104, 'GATE OF THE WELLS', GREY, 1, 'center')
    c.hline(32, 122, 960, BURG, 3)
    c.hline(32, 127, 960, GOLD, 1)
    c.vline(512, 134, 770, INK, 1)
    # ---- left page: data page ----
    c.text(36, 146, 'DATA PAGE', BURG, 2)
    c.rect(36, 172, 168, 208, INK)
    portrait(c, 40, 176, 160, 200, (214, 176, 140), (30, 24, 20),
             (245, 245, 240), BURG, 'beard')
    c.text(36, 388, 'PHOTO 35 X 45 MM', GREY, 1)
    y = 146
    y = field(c, 224, y, 'SURNAME', 'AL-QAMARI', INK, GREY)
    y = field(c, 224, y, 'GIVEN NAMES', 'YUSUF IBRAHIM', INK, GREY)
    y = field(c, 224, y, 'NATIONALITY', 'QAMARI', INK, GREY)
    y = field(c, 224, y, 'DATE OF BIRTH', '17 AUG 1990', INK, GREY)
    y = field(c, 224, y, 'PLACE OF BIRTH', 'QAMAR CITY', INK, GREY)
    y = field(c, 224, y, 'DATE OF ISSUE', '20 MAY 2024', INK, GREY)
    y = field(c, 224, y, 'DATE OF EXPIRY', '19 MAY 2034', INK, GREY)
    y = field(c, 224, y, 'ISSUING AUTHORITY', 'MINISTRY OF THE WELLS', INK, GREY)
    c.text(36, 470, "HOLDER'S SIGNATURE", GREY, 1)
    c.line(36, 500, 90, 484, INK, 2)
    c.line(90, 484, 130, 502, INK, 2)
    c.line(130, 502, 180, 486, INK, 2)
    c.line(180, 486, 230, 500, INK, 2)
    c.hline(36, 508, 220, INK, 1)
    # document number box, cream panel under the signature
    c.rect(36, 540, 452, 64, CREAM)
    c.rect(36, 540, 452, 1, GOLD)
    c.rect(36, 603, 452, 1, GOLD)
    c.text(52, 556, 'DOCUMENT NO.', GREY, 1)
    c.text(52, 572, 'Q 24681357', INK, 3)
    c.text(330, 556, 'SEX', GREY, 1)
    c.text(330, 572, 'M', INK, 3)
    c.text(400, 556, 'HEIGHT', GREY, 1)
    c.text(400, 572, '178 CM', INK, 2)
    c.text(36, 640, 'OBSERVATIONS', BURG, 2)
    c.para(36, 668, 'HOLDER IS A WELL-KEEPER OF THE THIRD DISTRICT. WATER IS MEASURED IN SKINS, NOT LITRES.',
           INK, 1, 452, leading=12)
    c.text(36, 730, 'THIS PASSPORT REMAINS THE PROPERTY OF', GREY, 1)
    c.text(36, 746, 'THE SULTANATE OF QAMAR.', GREY, 1)
    # ---- right page: visas and stamps, stacked ----
    c.text(528, 146, 'VISAS AND STAMPS', BURG, 2)
    stamp_rect(c, 528, 172, 216, 104, GREEN,
               ['ARRIVAL', 'ZANZARA', '05 DEC 2025', '* * *'], 2)
    stamp_rect(c, 760, 172, 216, 104, RED,
               ['DEPARTURE', 'ZANZARA', '19 DEC 2025', '* * *'], 2)
    stamp_circle(c, 636, 360, 72, BURG,
                 ['KESH', 'ARRIVAL', '11 APR', '2026'], 1)
    c.rect(736, 292, 240, 136, CREAM)
    c.rect(736, 292, 240, 2, BURG)
    c.rect(736, 426, 240, 2, BURG)
    c.text(856, 304, 'VISA', BURG, 3, 'center')
    c.text(856, 330, 'PILGRIM ROUTE', INK, 1, 'center')
    c.text(856, 348, 'ZANZARA', INK, 2, 'center')
    c.text(856, 372, 'VALID TO 19 DEC 2026', INK, 1, 'center')
    c.text(856, 390, 'ONE CAMEL, NO MORE', INK, 1, 'center')
    # telling detail: the water-tax fee stamp
    c.rect(528, 470, 448, 150, CREAM)
    c.rect(528, 470, 448, 3, GOLD)
    c.text(544, 486, 'WATER TAX - PAID', BURG, 2)
    c.para(544, 516, 'TWO DINARS PER CAMEL, PAID AT THE GATE OF THE WELLS. PILGRIMS TRAVEL FREE ON THE FIRST FRIDAY.',
           INK, 2, 416, leading=20)
    stamp_circle(c, 640, 720, 66, BLUE,
                 ['QAMAR', 'EXIT', 'GATE OF', 'WELLS'], 1)
    c.text(736, 690, 'NEXT OF KIN:', GREY, 1)
    c.text(736, 708, 'LAYLA AL-QAMARI', INK, 2)
    c.text(736, 732, 'QAMAR CITY', INK, 2)
    c.text(736, 756, 'TEL +962 44 71 08', INK, 1)
    # MRZ band across the whole spread
    c.rect(16, 920, 992, 88, BURG)
    c.text(512, 932, 'P<QMRAL-QAMARI<<YUSUF<IBRAHIM<<<<<<<<<<<<', (245, 238, 225), 2, 'center')
    c.text(512, 962, 'Q24681357<2QMR9008173M3405194<<<<<<<<<<<<<<04', (245, 238, 225), 2, 'center')
    return c.png()

def main():
    data = draw_image()
    out = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'entry.png'), 'wb') as f:
        f.write(data)

if __name__ == '__main__':
    main()
