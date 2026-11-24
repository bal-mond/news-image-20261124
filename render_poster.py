#!/usr/bin/env python3
"""Render the front page of THE WORLD IN ONE DAY for Tuesday 24 November 2026.

A single 1024x1024 newspaper-style poster holding 30 world stories from one
day: three lead stories across the top, then three columns of nine stories
each (war & diplomacy, markets & the Americas, science / tech / sport / life),
a bottom ticker repeating the leads, and a plain footer line.

Everything is drawn with Pillow from scratch: no photographs, no downloaded
images, no network access. All text is set in the DejaVu family, which ships
with most Linux systems. The script writes entry.png next to itself and
prints the file size and a short integrity summary.

Layout (1024x1024, all y coordinates in pixels):
  masthead title ............ y 26-95, centred serif, 54 pt
  date line ................. y 106-135, red, 22 pt
  story-count strap ......... y 150-170
  top-stories teaser line ... y 176-195, one line, centred
  three lead stories ........ y 214 onwards, side by side
  three columns ............. top ~y 250, bottom edge y 884
  ticker band ............... y 896-944, navy, white text
  footer line ............... y 962, centred, 13 pt

Column text is word-wrapped to the column width, so nothing can run past
the page edges, and each column raises an error if it would overflow its
budget instead of drawing outside the poster.
"""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
MARGIN = 36
GUTTER = 20
COL_W = (SIZE - 2 * MARGIN - 2 * GUTTER) // 3

PAPER = (247, 243, 234)
INK = (26, 26, 26)
MUTED = (90, 84, 72)
RED = (176, 32, 32)
NAVY = (31, 58, 95)
RULE = (180, 172, 156)
LIGHT_RULE = (214, 207, 192)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load(name, size):
    """Load a DejaVu font, falling back to Pillow's built-in bitmap font."""
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


SERIF_BOLD = lambda s: load("DejaVuSerif-Bold.ttf", s)
SANS_BOLD = lambda s: load("DejaVuSans-Bold.ttf", s)
SANS = lambda s: load("DejaVuSans.ttf", s)
# No oblique DejaVu Sans ships on this system (only Sans, Sans-Bold,
# Serif and Serif-Bold), so "oblique" text is set in regular Sans rather
# than falling back to Pillow's bitmap font, which lacks glyphs like
# the em dash and bullet used in the teaser line and footer.
SANS_OBLIQUE = lambda s: load("DejaVuSans.ttf", s)


def wrap(draw, text, font, max_width):
    """Greedy word wrap returning a list of lines that fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered(draw, y, text, font, fill=INK):
    """Draw text centred on the page at the given y; return its height."""
    width = draw.textlength(text, font=font)
    draw.text(((SIZE - width) / 2, y), text, font=font, fill=fill)
    return font.getbbox(text)[3]


def rule(draw, y, weight=2, fill=RULE, x0=None, x1=None):
    """Draw a horizontal rule across the content width."""
    x0 = MARGIN if x0 is None else x0
    x1 = SIZE - MARGIN if x1 is None else x1
    draw.line([(x0, y), (x1, y)], fill=fill, width=weight)


# ---------------------------------------------------------------------------
# The thirty stories, written for this poster from the day's reported facts.
# Each entry is (headline, one short summary). Headlines stay short so they
# fit one or two lines at column width; summaries run to at most two lines.
# ---------------------------------------------------------------------------

TOP_STORIES = [
    ("Sanofi seals $41bn Insmed buyout",
     "French drugmaker agrees $175 a share in cash, its biggest deal in over "
     "20 years and the largest pharma takeover of 2026."),
    ("Riyadh's tallest tower hit again",
     "A strike on the PIF Tower wounds 11 people, the second attack on the "
     "landmark in under a week."),
    ("Senegal's crown restored by court",
     "Sport's top court overturns the ruling that handed the Africa Cup to "
     "Morocco; Senegal's 1-0 final win stands."),
]

COLUMNS = [
    ("WAR & DIPLOMACY", [
        ("Gaza strike kills Hamas security chief",
         "Naeem Abu Nahel dies with six others as Israeli strikes hit Gaza."),
        ("Two killed in strike on flats",
         "A Russian strike on an apartment block in Zaporizhzhia kills two "
         "and wounds 40, including four children."),
        ("Hungary's new PM meets Zelensky",
         "Peter Magyar meets Zelensky in Uzhhorod, backing Ukraine's EU bid "
         "on his first visit as PM."),
        ("Russian drone slips into Poland",
         "A Russian drone briefly crosses Polish airspace overnight during a "
         "heavy attack on western Ukraine."),
        ("Kremlin cool on Europe at talks",
         "Moscow says it sees no added value in Europe joining Ukraine peace "
         "talks; no date is set."),
        ("War 'tipping point' seen in 2027",
         "Latvia's president warns the war may reach a tipping point in 2027."),
        ("Germany first into Delta network",
         "Berlin joins Ukraine's Delta battlefield network first and pledges "
         "more interceptor missiles."),
        ("UK warns firms of sabotage risk",
         "The defence ministry and MI5 alert companies supplying Ukraine to "
         "a Russian sabotage threat."),
        ("Britain sanctions the Houthis",
         "London imposes sanctions on the Houthis after the strike on "
         "Riyadh's tower."),
    ]),
    ("MARKETS & AMERICAS", [
        ("Norway seals 18-year gas deal",
         "Equinor signs with VNG to send 1.4bn cubic metres a year to 2044, "
         "Norway's longest gas deal since 1986."),
        ("Stocks slide as rate fears return",
         "The S&P 500 falls 0.95% after a Fed official hints at higher "
         "rates; the Stoxx 50 drops 1.2%."),
        ("Norway pledges $7bn for Ukraine",
         "Oslo promises at least $7bn in 2027 aid, focused on air defence "
         "and drones."),
        ("Cold snap lifts Europe gas prices",
         "Freezing weather pushes gas prices up as already low reserves come "
         "under strain."),
        ("Patriot missiles still unapproved",
         "The Pentagon has yet to approve 60 Patriot interceptors already "
         "promised to Ukraine."),
        ("Canada hits back at Pentagon",
         "Ottawa's defence minister says Canada answers to no one in "
         "Washington after Monday's broadside."),
        ("Kyiv to turn to new Congress",
         "Zelensky says Ukraine will seek arms and tougher sanctions from "
         "the new Congress if no deal comes by year-end."),
        ("Trump pardons two turkeys",
         "Freedom and Feathers are spared at the White House's annual "
         "Thanksgiving ceremony."),
        ("Nvidia slides as AI rally fades",
         "Shares fall after Monday's record rally as worries over interest "
         "rates return."),
    ]),
    ("SCIENCE, TECH, SPORT & LIFE", [
        ("EU seeks climate-talk overhaul",
         "After the Antalya summit ends with no deal, Brussels will push "
         "the UN to rework climate talks."),
        ("Beijing probes senior leader",
         "China opens a corruption inquiry into Politburo member Chen "
         "Jining, a senior Shanghai figure."),
        ("Pakistan's first astronaut named",
         "China names the crew for its next space station mission, "
         "including Pakistan's first astronaut."),
        ("Earliest quasar ever spotted",
         "Astronomers find a quasar that formed just 630 million years "
         "after the Big Bang."),
        ("Malaysia to return 6,500 Rohingya",
         "Kuala Lumpur plans to send 6,500 Rohingya refugees back to "
         "Myanmar, alarming rights groups."),
        ("Ebola teams freed after 3 days",
         "WHO staff are evacuated from an Ituri hospital after sheltering "
         "three days amid fighting."),
        ("Hanoi hot-pot blast kills six",
         "An explosion at an eatery kills six and injures more than "
         "a dozen."),
        ("Pope's diary reveals dark visions",
         "Published notes describe a spiritual crisis and visions of "
         "the devil."),
        ("Chess title defence opens in draw",
         "Gukesh holds Sindarov to a 38-move draw in game one of the world "
         "title match in Geneva."),
    ]),
]

TICKER = ("SANOFI BUYS INSMED FOR $41BN   \u2022   PIF TOWER STRUCK AGAIN, "
          "11 HURT   \u2022   SENEGAL REGAIN AFCON TITLE   \u2022   "
          "S&P 500 SLIDES   \u2022   NORWAY PLEDGES $7BN FOR UKRAINE")

FOOTER = "All events of Tuesday 24 November 2026, as reported that day."
FOOTER_Y = 962  # footer baseline; footer text height is ~17 px, so the
# lowest ink on the page sits near y 979, safely inside the 1024 canvas.


def draw_top_stories(draw, y):
    """Draw the three lead stories side by side; return the next free y."""
    label_font = SANS_BOLD(13)
    head_font = SANS_BOLD(15)
    body_font = SANS(12)
    label = "TOP STORIES"
    draw.text((MARGIN, y), label, font=label_font, fill=RED)
    y += 22
    col_x = [MARGIN + i * (COL_W + GUTTER) for i in range(3)]
    max_y = y
    for i, (headline, summary) in enumerate(TOP_STORIES):
        x = col_x[i]
        draw.text((x, y), "%d." % (i + 1), font=SANS_BOLD(15), fill=RED)
        hx = x + 22
        lines = wrap(draw, headline, head_font, COL_W - 22)
        ty = y
        for line in lines:
            draw.text((hx, ty), line, font=head_font, fill=INK)
            ty += 18
        for line in wrap(draw, summary, body_font, COL_W):
            draw.text((x, ty), line, font=body_font, fill=MUTED)
            ty += 15
        max_y = max(max_y, ty)
    return max_y + 6


def draw_column(draw, x, y, bottom, title, stories, summary_size=11):
    """Draw one column of stories; return the y just below the last item."""
    head_font = SANS_BOLD(13)
    body_font = SANS(summary_size)
    title_font = SANS_BOLD(14)
    # Section header: small coloured bar with white title text.
    draw.rectangle([x, y, x + COL_W, y + 26], fill=NAVY)
    draw.text((x + 8, y + 5), title, font=title_font, fill=(255, 255, 255))
    y += 26 + 8
    for headline, summary in stories:
        head_lines = wrap(draw, headline, head_font, COL_W)
        for line in head_lines:
            draw.text((x, y), line, font=head_font, fill=INK)
            y += 16
        for line in wrap(draw, summary, body_font, COL_W):
            draw.text((x, y), line, font=body_font, fill=MUTED)
            y += 14
        y += 7
        if y > bottom:
            raise ValueError("column %r overflows its budget" % title)
    return y


def build_poster():
    """Compose the poster and return the finished Pillow image."""
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img)

    # --- Masthead -------------------------------------------------------
    y = 26
    draw_centered(draw, y, "THE WORLD IN ONE DAY", SERIF_BOLD(54), INK)
    y = 96
    rule(draw, y, weight=3, fill=INK)
    y = 106
    draw_centered(draw, y, "Tuesday  \u2022  24 November 2026",
                  SANS_BOLD(22), RED)
    y = 140
    rule(draw, y, weight=1, fill=RULE)
    y = 150
    draw_centered(draw, y, "30 STORIES  \u2022  WORLDWIDE  \u2022  ONE DAY",
                  SANS_BOLD(14), NAVY)
    y = 176
    top_line = ("TOP STORIES \u2014 Sanofi's $41bn swoop  \u2022  Riyadh tower "
                "hit again  \u2022  Senegal's crown restored")
    draw_centered(draw, y, top_line, SANS_OBLIQUE(13), MUTED)
    y = 202
    rule(draw, y, weight=2, fill=INK)

    # --- Lead stories ---------------------------------------------------
    y = draw_top_stories(draw, 214)
    rule(draw, y + 2, weight=1, fill=RULE)

    # --- Three columns --------------------------------------------------
    col_top = y + 14
    col_bottom = 884
    for i, (title, stories) in enumerate(COLUMNS):
        x = MARGIN + i * (COL_W + GUTTER)
        draw_column(draw, x, col_top, col_bottom, title, stories)

    # --- Ticker ---------------------------------------------------------
    draw.rectangle([MARGIN, 896, SIZE - MARGIN, 944], fill=NAVY)
    ticker_font = SANS_BOLD(14)
    lines = wrap(draw, TICKER, ticker_font, SIZE - 2 * MARGIN - 24)
    ty = 896 + (48 - 17 * len(lines)) // 2
    for line in lines:
        width = draw.textlength(line, font=ticker_font)
        draw.text(((SIZE - width) / 2, ty), line, font=ticker_font,
                  fill=(255, 255, 255))
        ty += 17

    # --- Footer ---------------------------------------------------------
    # Guard: the footer must sit fully inside the canvas, with a margin.
    if FOOTER_Y + 20 > SIZE:
        raise ValueError("footer at y %d would run off the page" % FOOTER_Y)
    draw_centered(draw, FOOTER_Y, FOOTER, SANS_OBLIQUE(13), MUTED)
    return img


def verify_output(path, img):
    """Sanity-check the saved poster: size, mode, story count, file size.

    Raises ValueError if anything is off, so a bad render fails loudly
    instead of silently producing a broken entry.
    """
    if img.size != (SIZE, SIZE):
        raise ValueError("poster is %s, expected %dx%d"
                         % (img.size, SIZE, SIZE))
    if img.mode != "RGB":
        raise ValueError("poster mode is %s, expected RGB" % img.mode)
    stories = len(TOP_STORIES) + sum(len(s) for _, s in COLUMNS)
    if stories != 30:
        raise ValueError("poster holds %d stories, expected 30" % stories)
    size = os.path.getsize(path)
    if size > 1048576:
        raise ValueError("poster is %d bytes, over the 1 MiB limit" % size)
    return size


def main():
    img = build_poster()
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "entry.png")
    img.save(out_path, format="PNG")
    checked_bytes = verify_output(out_path, img)
    with open(out_path, "rb") as fh:
        data = fh.read()
    assert len(data) == checked_bytes, "file changed between checks"
    digest = hashlib.sha256(data).hexdigest()
    stories = len(TOP_STORIES) + sum(len(s) for _, s in COLUMNS)
    print("poster: %s" % out_path)
    print("size: %dx%d" % img.size)
    print("stories: %d" % stories)
    print("bytes: %d" % len(data))
    print("sha256: %s" % digest)


if __name__ == "__main__":
    main()
