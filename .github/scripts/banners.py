#!/usr/bin/env python3
"""Generates the profile banners (same grid system as art/header-dark.svg).

Edit the text in .github/banners.json, commit, and the workflow rebuilds everything.
The Activity banner is drawn from your real GitHub contribution calendar.
"""
import datetime
import json
import os
import pathlib
import random
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / ".github/banners.json").read_text())
FONTS = json.loads((ROOT / ".github/scripts/fonts.json").read_text())
OUT = ROOT / "art"

W, H = 1660, 380
BG = "#0d1117"
RAMP = ["#151b23", "#2d333b", "#545d68", "#9198a1", "#f0f6fc"]
TITLE, SUB, PILL_BG, PILL_STROKE = "#f0f6fc", "#9198a1", "#151b23", "#30363d"
X0, Y0, PITCH, CELL = 611, 13, 28, 18
COLS, ROWS = 37, 13

G = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "11111 00100 00100 00100 00100 00100 11111", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 11011 10001", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00110 01000 10000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    "+": "00000 00100 00100 11111 00100 00100 00000", "!": "00100 00100 00100 00100 00100 00000 00100",
    ".": "00000 00000 00000 00000 00000 01100 01100", "-": "00000 00000 00000 11111 00000 00000 00000",
    " ": "00000 00000 00000 00000 00000 00000 00000",
}
GLYPH = {k: v.split() for k, v in G.items()}


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def style():
    css = (
        "@font-face{font-family:'Saira';font-weight:700;src:url(data:font/woff2;base64,@A@) format('woff2');}"
        "@font-face{font-family:'Saira';font-weight:400;src:url(data:font/woff2;base64,@B@) format('woff2');}"
        "@font-face{font-family:'Fira Code';font-weight:500;src:url(data:font/woff2;base64,@C@) format('woff2');}"
        "text{white-space:pre}"
        ".wave{animation:wave 4.8s linear infinite}"
        "@keyframes wave{from{transform:translateX(542.6px) skewX(-18deg)}to{transform:translateX(2040px) skewX(-18deg)}}"
        ".tw{animation:tw 4s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.04}50%{opacity:1}}"
        ".bl{animation:bl 1.05s steps(1) infinite}@keyframes bl{0%,49%{opacity:1}50%,100%{opacity:0}}"
        ".pu{animation:pu 3.2s ease-in-out infinite}@keyframes pu{0%,100%{opacity:.25}50%{opacity:1}}"
        ".repaint{animation:repaint .25s steps(2) 12}@keyframes repaint{50%{opacity:.004}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}.motion-only{display:none}}"
    )
    return css.replace("@A@", FONTS["saira700"]).replace("@B@", FONTS["saira400"]).replace("@C@", FONTS["fira500"])


STYLE = style()
SAIRA = "font-family=\"'Saira', system-ui, sans-serif\""
FIRA = "font-family=\"'Fira Code', ui-monospace, monospace\""
WAVE_DEF = (
    '<linearGradient id="wave" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f0f6fc" stop-opacity="0"/>'
    '<stop offset=".5" stop-color="#ffffff" stop-opacity="0.55"/><stop offset="1" stop-color="#f0f6fc" stop-opacity="0"/></linearGradient>'
)


def cellpath(cells):
    return "".join(f"M{x} {y}h{CELL}v{CELL}h-{CELL}z" for x, y in cells)


def noise(rnd, clear=None, lit=None, keep_legend=True, density=1.0):
    """Heatmap-like background levels. clear: callable(col,row)->bool to quiet an area."""
    lit = lit or set()
    levels = {i: [] for i in range(5)}
    for col in range(COLS):
        for row in range(ROWS):
            if keep_legend and col >= 25 and row >= 11:
                continue
            if (col, row) in lit:
                lv = 4
            else:
                g = (0.35 + 0.65 * (col / (COLS - 1))) * density
                v = rnd.random() * g + rnd.random() * 0.25
                lv = 0 if v < 0.42 else 1 if v < 0.62 else 2 if v < 0.82 else 3
                if clear and clear(col, row):
                    lv = min(lv, 1 if rnd.random() < 0.8 else 0)
                else:
                    lv = min(lv, 3 if rnd.random() < 0.25 else 2)
            levels[lv].append((X0 + col * PITCH, Y0 + row * PITCH))
    return levels


def twinkles(rnd, levels, n=18):
    pool = levels[1] + levels[2] + levels[3]
    rnd.shuffle(pool)
    out = ""
    for x, y in pool[:n]:
        out += (
            f'<rect class="tw motion-only" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{RAMP[3]}" '
            f'style="animation-duration:{rnd.uniform(2.6, 6):.2f}s;animation-delay:-{rnd.uniform(0, 6):.2f}s"/>'
        )
    return out


def frame(name, title, sub, pill, levels, over="", extra_defs="", rnd=None):
    paths = "".join(
        f'<path id="lv{i}" d="{cellpath(levels[i])}" fill="{RAMP[i]}" stroke="{RAMP[i]}" stroke-width="4" stroke-linejoin="round"/>'
        for i in range(5)
    )
    allc = cellpath([p for i in range(5) for p in levels[i]])
    pill_w = 18 * len(pill) + 38
    leg = "".join(f'<rect x="{1381.2 + i * 28}" y="328" width="22" height="22" rx="4" fill="{c}"/>' for i, c in enumerate(RAMP))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}: {esc(sub)}">'
        f"<title>{esc(title)}: {esc(sub)}</title><style>{STYLE}</style>"
        f'<defs><g id="cells">{paths}</g><clipPath id="cellclip"><path d="{allc}"/></clipPath>{WAVE_DEF}{extra_defs}</defs>'
        f'<rect width="{W}" height="{H}" fill="{BG}"/><use href="#cells"/>'
        f'{twinkles(rnd, levels) if rnd else ""}'
        f'<g clip-path="url(#cellclip)" class="motion-only"><rect class="wave" x="-260" y="-60" width="260" height="500" fill="url(#wave)" transform="skewX(-18)"/></g>'
        f"{over}"
        f'<text x="72" y="149.6" {SAIRA} font-size="96" font-weight="700" fill="{TITLE}">{esc(title)}</text>'
        f'<text x="72" y="217.1" {SAIRA} font-size="40" font-weight="400" fill="{SUB}">{esc(sub)}</text>'
        f'<rect x="72" y="259.2" width="{pill_w}" height="53" rx="26.5" fill="{PILL_BG}" stroke="{PILL_STROKE}" stroke-width="2"/>'
        f'<text x="91" y="296.5" {FIRA} font-size="30" font-weight="500" fill="{TITLE}">{esc(pill)}</text>'
        f'<text x="1314.4" y="346.9" {FIRA} font-size="22" font-weight="500" fill="{SUB}">Less</text>{leg}'
        f'<text x="1529.2" y="346.9" {FIRA} font-size="22" font-weight="500" fill="{SUB}">More</text>'
        f'<rect class="motion-only repaint" width="{W}" height="{H}" fill="#808080" opacity=".002" pointer-events="none"/></svg>'
    )
    (OUT / name).write_text(svg)
    print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ word banner
def word_banner(name, c, seed):
    word = c["word"].upper()[:6]
    wcols = len(word) * 6 - 1
    c0 = (COLS - wcols) // 2
    r0 = (ROWS - 7) // 2
    lit = set()
    for i, ch in enumerate(word):
        for r, row in enumerate(GLYPH.get(ch, GLYPH[" "])):
            for cc, v in enumerate(row):
                if v == "1":
                    lit.add((c0 + i * 6 + cc, r0 + r))
    rnd = random.Random(seed)
    zone = lambda col, row: c0 - 1 <= col <= c0 + wcols and r0 - 1 <= row <= r0 + 7
    levels = noise(rnd, clear=zone, lit=lit)
    frame(name, c["title"], c["sub"], c["pill"], levels, rnd=rnd)


# ------------------------------------------------------------------ now banner (typed lines)
def now_banner(name, c, seed):
    rnd = random.Random(seed)
    zone = lambda col, row: 3 <= row <= 9
    levels = noise(rnd, clear=lambda col, row: False)
    # fully quiet band behind the text
    for lv in range(1, 5):
        levels[lv] = [p for p in levels[lv] if not (Y0 + 3 * PITCH <= p[1] <= Y0 + 9 * PITCH)]
    for r in range(3, 10):
        for col in range(COLS):
            if col >= 25 and r >= 11:
                continue
            levels[0].append((X0 + col * PITCH, Y0 + r * PITCH))
    lines = c["lines"][:4]
    kw = max(len(k) for k, _ in lines)
    fs, cw = 34, 34 * 0.6
    step = 66
    base0 = 190 - (len(lines) - 1) * step / 2 + 12
    clips, over = "", ""
    last_end = 0
    for i, (k, v) in enumerate(lines):
        y = base0 + i * step
        text = f"> {k.ljust(kw)}  {v}"
        n = len(text)
        tw = n * cw + 8
        t0 = 0.5 + i * 1.7
        vals = ";".join(f"{j * cw:.1f}" for j in range(n + 1))
        kts = ";".join(f"{j / n:.4f}" for j in range(n + 1))
        clips += (
            f'<clipPath id="ln{i}"><rect x="{X0 + 20}" y="{y - 36:.1f}" width="0" height="52">'
            f'<animate attributeName="width" values="{vals}" keyTimes="{kts}" calcMode="discrete" dur="{n * 0.035:.2f}s" begin="{t0:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        over += (
            f'<g clip-path="url(#ln{i})"><text x="{X0 + 20}" y="{y:.1f}" {FIRA} font-size="{fs}" font-weight="500">'
            f'<tspan fill="{RAMP[3]}">&gt; </tspan><tspan fill="{TITLE}">{esc(k.ljust(kw))}</tspan><tspan fill="{RAMP[3]}">  {esc(v)}</tspan></text></g>'
        )
        last_end = X0 + 20 + n * cw + 6
        last_y = y
    over += f'<rect class="bl" x="{last_end:.0f}" y="{last_y - 30:.0f}" width="16" height="36" fill="{TITLE}"/>'
    frame(name, c["title"], c["sub"], c["pill"], levels, over=over, extra_defs=clips, rnd=rnd)


# ------------------------------------------------------------------ activity banner (real data)
def fetch_calendar(user):
    q = ("query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions "
         "weeks{contributionDays{contributionCount date weekday}}}}}}")
    r = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}", "-F", f"login={user}"],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:200])
    return json.loads(r.stdout)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def activity_banner(name, c, user, seed):
    try:
        weeks = fetch_calendar(user)[-COLS:]
    except Exception as e:  # keep the previous banner if we cannot fetch
        print("activity: could not fetch calendar:", e)
        if (OUT / name).exists():
            return
        weeks = []
    rnd = random.Random(seed)
    counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
    total = sum(counts)
    nz = sorted(x for x in counts if x > 0)

    def level(n):
        if n <= 0 or not nz:
            return 0
        q = [nz[int(len(nz) * f)] for f in (0.25, 0.5, 0.75)] if len(nz) >= 4 else [1, 2, 3]
        return 1 if n <= q[0] else 2 if n <= q[1] else 3 if n <= q[2] else 4

    levels = {i: [] for i in range(5)}
    r0 = 3
    off = COLS - len(weeks)
    for col in range(COLS):
        for row in range(ROWS):
            if col >= 25 and row >= 11:
                continue
            x, y = X0 + col * PITCH, Y0 + row * PITCH
            lv = 0
            wi = col - off
            if r0 <= row < r0 + 7 and 0 <= wi < len(weeks):
                days = weeks[wi]["contributionDays"]
                di = row - r0
                if di < len(days):
                    lv = level(days[di]["contributionCount"])
            elif not (r0 <= row < r0 + 7) and rnd.random() < 0.10:
                lv = 1
            levels[lv].append((x, y))
    # month labels above the grid
    over, last = "", -9
    prev = None
    for wi, w in enumerate(weeks):
        d = datetime.date.fromisoformat(w["contributionDays"][0]["date"])
        if d.month != prev and wi - last >= 3:
            over += f'<text x="{X0 + (wi + off) * PITCH}" y="{Y0 + 2 * PITCH + 4}" {FIRA} font-size="20" font-weight="500" fill="{RAMP[3]}">{d.strftime("%b")}</text>'
            last = wi
        prev = d.month
    pill = f"{total} contributions" if weeks else "syncing..."
    frame(name, c["title"], c["sub"], pill, levels, over=over, rnd=rnd)


# ------------------------------------------------------------------ tools strip
def tools_strip(name, tools):
    fs = 44
    cw = fs * 0.6
    h, ph, gap = 330, 84, 26
    rows = [tools[: (len(tools) + 1) // 2], tools[(len(tools) + 1) // 2:]]
    ys = [(h - (2 * ph + gap)) / 2 + i * (ph + gap) for i in range(2)]
    pills, clip = "", ""
    idx = 0
    for ri, row in enumerate(rows):
        widths = [len(t) * cw + 40 + 46 for t in row]
        total = sum(widths) + gap * (len(row) - 1)
        x = (W - total) / 2
        for t, wd in zip(row, widths):
            y = ys[ri]
            pills += (
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{wd:.1f}" height="{ph}" rx="{ph / 2}" fill="{PILL_BG}" stroke="{PILL_STROKE}" stroke-width="2"/>'
                f'<circle class="pu" cx="{x + 38:.1f}" cy="{y + ph / 2:.1f}" r="8" fill="{TITLE}" style="animation-delay:{idx * 0.45:.2f}s"/>'
                f'<text x="{x + 64:.1f}" y="{y + ph / 2 + 15:.1f}" {FIRA} font-size="{fs}" font-weight="500" fill="{TITLE}">{esc(t)}</text>'
            )
            clip += f'<rect x="{x:.1f}" y="{y:.1f}" width="{wd:.1f}" height="{ph}" rx="{ph / 2}"/>'
            x += wd + gap
            idx += 1
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="Tools: {esc(", ".join(tools))}">'
        f"<title>Tools: {esc(', '.join(tools))}</title><style>{STYLE}</style>"
        f"<defs><clipPath id=\"pc\">{clip}</clipPath>{WAVE_DEF.replace('0.55', '0.16')}</defs>"
        f'<rect width="{W}" height="{h}" fill="{BG}"/>{pills}'
        f'<g clip-path="url(#pc)" class="motion-only"><rect class="wave" x="-260" y="-60" width="260" height="{h + 120}" fill="url(#wave)" transform="skewX(-18)" style="animation-duration:6s"/></g>'
        f"</svg>"
    )
    (OUT / name).write_text(svg)
    print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ footer strip
def footer_strip(name, c, seed):
    rnd = random.Random(seed)
    h = 164
    cols = 59
    rows = 5
    text = c["text"]
    tw = len(text) * (30 * 0.6 + 3)
    cx0 = (W - tw) / 2 - 80
    cx1 = (W + tw) / 2 + 60
    levels = {i: [] for i in range(5)}
    for col in range(cols):
        for row in range(rows):
            x, y = 14 + col * PITCH, 13 + row * PITCH
            if cx0 <= x <= cx1 and 40 <= y <= 110:
                continue
            edge = min(col, cols - 1 - col) / (cols / 2)  # stronger toward the middle
            v = rnd.random() * (0.25 + 0.9 * edge) + rnd.random() * 0.1
            lv = 0 if v < 0.4 else 1 if v < 0.6 else 2 if v < 0.8 else 3
            levels[lv].append((x, y))
    paths = "".join(
        f'<path d="{cellpath(levels[i])}" fill="{RAMP[i]}" stroke="{RAMP[i]}" stroke-width="4" stroke-linejoin="round"/>' for i in range(4)
    )
    allc = cellpath([p for i in range(4) for p in levels[i]])
    pool = levels[1] + levels[2] + levels[3]
    rnd.shuffle(pool)
    tws = "".join(
        f'<rect class="tw motion-only" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{RAMP[3]}" '
        f'style="animation-duration:{rnd.uniform(2.6, 6):.2f}s;animation-delay:-{rnd.uniform(0, 6):.2f}s"/>'
        for x, y in pool[:16]
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{esc(text)}">'
        f"<title>{esc(text)}</title><style>{STYLE}</style>"
        f'<defs><clipPath id="cellclip"><path d="{allc}"/></clipPath>{WAVE_DEF}</defs>'
        f'<rect width="{W}" height="{h}" fill="{BG}"/>{paths}{tws}'
        f'<g clip-path="url(#cellclip)" class="motion-only"><rect class="wave" x="-260" y="-60" width="260" height="{h + 120}" fill="url(#wave)" transform="skewX(-18)" style="animation-duration:7s"/></g>'
        f'<text x="{W / 2}" y="{h / 2 + 11}" text-anchor="middle" {FIRA} font-size="30" font-weight="500" fill="{SUB}" letter-spacing="3">{esc(text)}</text>'
        f"</svg>"
    )
    (OUT / name).write_text(svg)
    print("wrote", name, len(svg) // 1024, "KB")


def main():
    OUT.mkdir(exist_ok=True)
    user = os.environ.get("GITHUB_REPOSITORY_OWNER") or CFG.get("user", "LynkqUK")
    word_banner("about.svg", CFG["about"], 21)
    now_banner("now.svg", CFG["now"], 8)
    word_banner("stack.svg", CFG["stack"], 34)
    tools_strip("tools.svg", CFG["tools"])
    activity_banner("activity.svg", CFG["activity"], user, 13)
    word_banner("contact.svg", CFG["contact"], 55)
    footer_strip("footer.svg", CFG["footer"], 89)


if __name__ == "__main__":
    main()
