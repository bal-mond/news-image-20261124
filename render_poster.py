#!/usr/bin/env python3
"""Render the 24 November 2026 world-news poster (1024x1024) with Pillow.

Newspaper layout, all artwork drawn here with PIL primitives: no photos,
no downloaded images, no network. Every story below was checked against
web search results dated Tuesday 24 November 2026 before being written
in. Output: entry.png next to this script (1024x1024, under 1 MiB).
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BG = (247, 243, 234)      # warm paper
INK = (26, 26, 26)
RED = (178, 34, 34)
NAVY = (18, 32, 62)
GREY = (110, 108, 100)
BODY_GREY = (62, 62, 62)
LINE = (200, 192, 175)
WHITE = (255, 255, 255)
ACCENT = {
    "war": (140, 30, 30), "climate": (31, 110, 72), "market": (24, 74, 130),
    "tech": (90, 50, 130), "space": (40, 60, 120), "sport": (176, 96, 0),
    "culture": (150, 60, 110), "health": (20, 120, 110), "us": (24, 74, 130),
    "world": (90, 90, 90),
}

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


F_TITLE = font(SERIF_B, 48)
F_DATE = font(SANS_B, 19)
F_META = font(SANS_B, 13)
F_KICK = font(SANS_B, 10)
F_HEAD = font(SANS_B, 13)
F_BODY = font(SANS, 11)
F_TOP_HEAD = font(SANS_B, 19)
F_TOP_BODY = font(SANS, 12)
F_TICK = font(SANS_B, 12)
F_FOOT = font(SANS, 11)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)


def wrap(text, f, width):
    """Greedy word wrap to pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def glyph(draw, kind, x, y, s, color):
    """Draw a tiny white pictogram inside an s x s box at (x, y)."""
    if kind == "globe":  # circle + meridians
        draw.ellipse([x + 2, y + 2, x + s - 2, y + s - 2], outline=color, width=2)
        draw.ellipse([x + s // 2 - 3, y + 2, x + s // 2 + 3, y + s - 2],
                     outline=color, width=1)
        draw.line([x + 2, y + s // 2, x + s - 2, y + s // 2], fill=color, width=1)
    elif kind == "flame":  # simple flame
        draw.polygon([(x + s // 2, y + 1), (x + s - 2, y + s - 6),
                      (x + s // 2 + 2, y + s - 2), (x + 2, y + s - 6)],
                     fill=color)
    elif kind == "ship":
        draw.polygon([(x + 2, y + s - 6), (x + s - 2, y + s - 6),
                      (x + s - 5, y + s - 1), (x + 5, y + s - 1)], fill=color)
        draw.line([x + s // 2, y + 2, x + s // 2, y + s - 7], fill=color, width=2)
        draw.polygon([(x + s // 2, y + 2), (x + s - 4, y + s - 7),
                      (x + s // 2, y + s - 7)], fill=color)
    elif kind == "chart":  # rising bars
        draw.rectangle([x + 2, y + s - 6, x + 5, y + s - 2], fill=color)
        draw.rectangle([x + 7, y + s - 10, x + 10, y + s - 2], fill=color)
        draw.rectangle([x + 12, y + s - 14, x + 15, y + s - 2], fill=color)
    elif kind == "chip":
        draw.rectangle([x + 4, y + 4, x + s - 4, y + s - 4], outline=color, width=2)
        for px in (x + 6, x + s // 2, x + s - 7):
            draw.line([px, y + 1, px, y + 4], fill=color, width=1)
            draw.line([px, y + s - 4, px, y + s - 1], fill=color, width=1)
    elif kind == "rocket":
        draw.polygon([(x + s // 2, y + 1), (x + s - 3, y + s - 8),
                      (x + s // 2, y + s - 5), (x + 3, y + s - 8)], fill=color)
        draw.polygon([(x + s // 2 - 2, y + s - 5), (x + s // 2 + 2, y + s - 5),
                      (x + s // 2, y + s - 1)], fill=color)
    elif kind == "ball":
        draw.ellipse([x + 2, y + 2, x + s - 2, y + s - 2], outline=color, width=2)
        draw.polygon([(x + s // 2, y + s // 2 - 3), (x + s // 2 + 3, y + s // 2 + 1),
                      (x + s // 2 - 3, y + s // 2 + 1)], fill=color)
    elif kind == "cross":  # health
        draw.rectangle([x + s // 2 - 2, y + 2, x + s // 2 + 2, y + s - 2], fill=color)
        draw.rectangle([x + 2, y + s // 2 - 2, x + s - 2, y + s // 2 + 2], fill=color)
    elif kind == "ballot":  # ballot box + tick
        draw.rectangle([x + 2, y + 4, x + s - 2, y + s - 2], outline=color, width=2)
        draw.line([x + 4, y + s // 2 + 1, x + s // 2, y + s - 4,
                   x + s - 3, y + 3], fill=color, width=2)
    elif kind == "star":
        cx, cy, r = x + s // 2, y + s // 2, s // 2 - 1
        pts = [(cx, cy - r), (cx + 3, cy - 2), (cx + r, cy - 2), (cx + 5, cy + 2),
               (cx + 7, cy + r - 1), (cx, cy + 4), (cx - 7, cy + r - 1),
               (cx - 5, cy + 2), (cx - r, cy - 2), (cx - 3, cy - 2)]
        draw.polygon(pts, fill=color)
    elif kind == "film":  # camera / culture
        draw.rectangle([x + 2, y + 5, x + s - 2, y + s - 3], outline=color, width=2)
        draw.ellipse([x + s // 2 - 3, y + s // 2 - 2, x + s // 2 + 3, y + s // 2 + 4],
                     outline=color, width=2)
    else:  # "dot" fallback
        draw.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], fill=color)


def icon(draw, kind, accent, x, y):
    s = 17
    draw.rounded_rectangle([x, y, x + s, y + s], radius=4, fill=accent)
    glyph(draw, kind, x + 1, y + 1, s - 2, WHITE)


# ---------- data: 30 stories, all dated Tuesday 24 November 2026 ----------
# (kicker, headline, summary, icon kind, accent)
TOP = [
    ("1. PHARMA  •  MARKETS",
     "SANOFI BUYS INSMED FOR $41BN",
     "French drugmaker agrees its biggest deal in 20 years, $175 a share in "
     "cash for the US biotech; the largest pharma takeover of 2026.",
     "chart", "market"),
    ("2. WAR  •  SAUDI ARABIA",
     "HOUTHIS HIT RIYADH'S TALLEST TOWER",
     "Missile strike injures 11 in the Saudi capital; Houthi fighters close "
     "to within 60 km of Aden.",
     "flame", "war"),
    ("3. SPORT  •  AFRICA",
     "SENEGAL CHAMPIONS AGAIN",
     "Sport's top court restores Senegal's Africa Cup title, overturning "
     "the ruling that gave it to Morocco.",
     "ball", "sport"),
]

COLS = [
    ("WAR & DIPLOMACY", "9", [
        ("GAZA",
         "Israeli strikes kill Hamas security chief",
         "Naeem Abu Nahel and six others die in Gaza strikes, medics and police say.",
         "flame", "war"),
        ("UKRAINE",
         "Russian strike on Zaporizhzhia kills 2",
         "Overnight attack on an apartment block wounds 40, including four children.",
         "flame", "war"),
        ("HUNGARY",
         "Hungary's PM meets Zelensky in Ukraine",
         "Péter Magyar visits Uzhhorod, backing Kyiv's EU bid on his first trip since 2015.",
         "star", "world"),
        ("POLAND",
         "Russian drone briefly enters Polish airspace",
         "Drone strays over Poland during a large Russian attack on western Ukraine overnight.",
         "flame", "war"),
        ("RUSSIA",
         "Kremlin sees no role for Europe at talks",
         "Moscow says it sees no added value in Europe joining Ukraine peace talks; no date set.",
         "star", "world"),
        ("KOREA",
         "Russian jets enter Korea's defence zone",
         "Seoul scrambles after aircraft fly near Ulleung Island; a shelter alert is lifted.",
         "flame", "war"),
        ("UKRAINE",
         "Latvia: war may hit a tipping point in 2027",
         "President Rinkevics tells Reuters next year could bring Russia's defeat.",
         "star", "world"),
        ("GERMANY",
         "Germany gets access to Ukraine's Delta system",
         "Berlin is first to join Kyiv's battlefield network; more interceptor missiles agreed.",
         "chip", "tech"),
        ("BRITAIN",
         "UK warns firms of Russian sabotage threat",
         "Defence ministry and MI5 alert companies supplying Ukraine to brace for attacks.",
         "flame", "war"),
    ]),
    ("MARKETS & AMERICAS", "9", [
        ("ENERGY",
         "Equinor signs 18-year gas deal with VNG",
         "Norway to supply Germany 1.4bn cubic metres a year to 2044, its longest gas deal since 1986.",
         "chart", "market"),
        ("MARKETS",
         "Stocks slip as rate worries return",
         "S&P 500 falls 0.95% after a Fed official hints at higher rates; Stoxx 50 down 1.2%.",
         "chart", "market"),
        ("BRITAIN",
         "Britain sanctions the Houthis",
         "London designates the group and four officials after the Riyadh tower strike.",
         "star", "world"),
        ("NORWAY",
         "Norway pledges $7bn more for Ukraine",
         "Oslo to give at least $7bn in 2027 aid, focused on air defence and drones.",
         "chart", "market"),
        ("ENERGY",
         "Europe gas prices climb in cold snap",
         "Prices rise as freezing weather threatens already low reserves.",
         "flame", "world"),
        ("USA",
         "Pentagon holds up 60 Patriot missiles",
         "Hegseth has yet to approve interceptors already pledged to Ukraine, the FT reports.",
         "ballot", "us"),
        ("CANADA",
         "Canada hits back at Pentagon rebuke",
         "Defence minister says Ottawa answers to no one in Washington after Monday's broadside.",
         "ballot", "us"),
        ("USA",
         "Zelensky to seek more US aid if talks fail",
         "Kyiv will turn to the new Congress for arms and tougher sanctions if no deal by year-end.",
         "ballot", "us"),
        ("USA",
         "Trump pardons turkeys Freedom and Feathers",
         "Two West Virginia birds get the annual Thanksgiving reprieve at the White House.",
         "star", "us"),
    ]),
    ("SCIENCE, TECH, SPORT & LIFE", "9", [
        ("CLIMATE",
         "After COP31 collapse, EU seeks new rules",
         "Brussels will push the UN to overhaul climate talks after Antalya ended with no deal.",
         "globe", "climate"),
        ("CHINA",
         "Corruption probe hits Politburo member",
         "Beijing opens an investigation into Chen Jining, a senior Shanghai leader.",
         "star", "world"),
        ("SPACE",
         "China names crew with Pakistani astronaut",
         "Pakistan's first astronaut will board China's space station on the new mission.",
         "rocket", "space"),
        ("SPACE",
         "Earliest quasar ever found",
         "Scientists spot a quasar formed just 630 million years after the Big Bang.",
         "rocket", "space"),
        ("TECH",
         "Nvidia slides as AI rally fades",
         "Shares fall after Monday's record rally as rate worries return; chip stocks follow.",
         "chip", "tech"),
        ("ASIA",
         "Malaysia to return 6,500 Rohingya",
         "Refugees will be sent back to Myanmar, drawing rights groups' alarm.",
         "globe", "world"),
        ("AFRICA",
         "Ebola teams freed after 3 days trapped",
         "WHO evacuates staff from an Ituri hospital after sheltering three days amid fighting.",
         "cross", "health"),
        ("VIETNAM",
         "Hanoi hot-pot blast kills 6",
         "An explosion at an eatery in the capital injures more than a dozen.",
         "flame", "world"),
        ("VATICAN",
         "Pope Francis diary reveals dark visions",
         "Published notes describe a spiritual crisis and visions of the devil.",
         "film", "culture"),
    ]),
]

TICKER = ("TICKER  •  SANOFI BUYS INSMED $41BN  •  HOUTHIS HIT RIYADH  •  "
          "SENEGAL CHAMPIONS AGAIN  •  NORWAY GIVES UKRAINE $7BN")

# ---------- masthead ----------
d.rectangle([0, 0, W, 6], fill=RED)
y = 14
d.text((24, y), "THE WORLD IN ONE DAY", font=F_TITLE, fill=INK)
y += 60
d.text((24, y), "TUESDAY  •  24 NOVEMBER 2026", font=F_DATE, fill=RED)
right = "30 STORIES  •  WORLDWIDE  •  ONE DAY"
d.text((W - 24 - d.textlength(right, font=F_META), y + 3), right, font=F_META, fill=GREY)
y += 28
d.line([24, y, W - 24, y], fill=INK, width=2)
y += 9

# ---------- top stories ----------
col_w = (W - 48 - 2 * 16) // 3
top_y = y
top_h = 0
for i, (kick, head, body, kind, acc) in enumerate(TOP):
    x = 24 + i * (col_w + 16)
    yy = top_y
    d.line([x, yy, x + col_w, yy], fill=RED, width=3)
    yy += 8
    icon(d, kind, ACCENT[acc], x, yy)
    d.text((x + 23, yy + 2), kick, font=F_KICK, fill=RED)
    yy += 21
    for line in wrap(head, F_TOP_HEAD, col_w):
        d.text((x, yy), line, font=F_TOP_HEAD, fill=INK)
        yy += 23
    yy += 1
    for line in wrap(body, F_TOP_BODY, col_w):
        d.text((x, yy), line, font=F_TOP_BODY, fill=INK)
        yy += 15
    yy += 2
    top_h = max(top_h, yy - top_y)
y = top_y + top_h + 6

# ---------- three columns ----------
sec_y = y
col_bottom = sec_y
for ci, (title, count, items) in enumerate(COLS):
    x = 24 + ci * (col_w + 16)
    d.rectangle([x, sec_y, x + col_w, sec_y + 23], fill=NAVY)
    d.text((x + 8, sec_y + 4), title, font=F_KICK, fill=WHITE)
    d.text((x + col_w - 8 - d.textlength(count, font=F_KICK), sec_y + 4),
           count, font=F_KICK, fill=WHITE)
    yy = sec_y + 29
    for kick, head, body, kind, acc in items:
        icon(d, kind, ACCENT[acc], x, yy)
        d.text((x + 23, yy + 2), kick, font=F_KICK, fill=RED)
        yy += 17
        for line in wrap(head, F_HEAD, col_w):
            d.text((x, yy), line, font=F_HEAD, fill=INK)
            yy += 16
        for line in wrap(body, F_BODY, col_w):
            d.text((x, yy), line, font=F_BODY, fill=BODY_GREY)
            yy += 13
        yy += 2
        d.line([x, yy, x + col_w, yy], fill=LINE, width=1)
        yy += 8
    col_bottom = max(col_bottom, yy)
y = col_bottom + 2

# ---------- ticker + footer ----------
d.rectangle([0, y, W, y + 25], fill=NAVY)
d.text((24, y + 6), TICKER, font=F_TICK, fill=WHITE)
y += 25
d.text((24, y + 5),
       "All events of Tuesday 24 November 2026, as reported that day.",
       font=F_FOOT, fill=GREY)

assert y + 20 <= H, "layout overflow: %d" % (y + 20)
img.save("/home/hatch/workspace/make-fun-bounty/build/news-image-20261124/entry.png",
         optimize=True)
print("saved, bottom y =", y)
