#!/usr/bin/env python3
"""Generates the profile banners (same grid system as art/header-dark.svg).

Edit the text in .github/banners.json, commit, and the workflow rebuilds everything.
The Activity banner is drawn from your real GitHub contribution calendar.
"""
import math, datetime
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
        ".lp{animation:lp 8s linear infinite}@keyframes lp{0%{opacity:.25}6%{opacity:1}26%{opacity:.25}100%{opacity:.25}}"
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


# ------------------------------------------------------------------ typed-lines banner
def lines_banner(name, c, seed, lines=None, pill=None):
    rnd = random.Random(seed)
    levels = noise(rnd)
    for lv in range(1, 5):
        levels[lv] = [p for p in levels[lv] if not (Y0 + 3 * PITCH <= p[1] <= Y0 + 9 * PITCH)]
    for r in range(3, 10):
        for col in range(COLS):
            if col >= 25 and r >= 11:
                continue
            levels[0].append((X0 + col * PITCH, Y0 + r * PITCH))
    lines = [tuple(x) for x in (lines if lines is not None else c["lines"])][:5]
    n_l = len(lines)
    fs = 34 if n_l <= 3 else 30 if n_l == 4 else 27
    step = 66 if n_l <= 3 else 52 if n_l == 4 else 44
    cw = fs * 0.6
    kw = max(len(k) for k, _ in lines)
    maxn = int(980 / cw)
    base0 = 190 - (n_l - 1) * step / 2 + fs * 0.35
    clips, over = "", ""
    last_end, last_y = X0 + 20, base0
    for i, (k, v) in enumerate(lines):
        y = base0 + i * step
        text = f"> {k.ljust(kw)}  {v}"[:maxn]
        n = len(text)
        t0 = 0.5 + i * 1.6
        vals = ";".join(f"{j * cw:.1f}" for j in range(n + 1))
        kts = ";".join(f"{j / n:.4f}" for j in range(n + 1))
        clips += (
            f'<clipPath id="ln{i}"><rect x="{X0 + 20}" y="{y - fs * 1.05:.1f}" width="0" height="{fs * 1.5:.1f}">'
            f'<animate attributeName="width" values="{vals}" keyTimes="{kts}" calcMode="discrete" dur="{n * 0.035:.2f}s" begin="{t0:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        key_part = text[2:2 + kw]
        val_part = text[2 + kw:]
        over += (
            f'<g clip-path="url(#ln{i})"><text x="{X0 + 20}" y="{y:.1f}" {FIRA} font-size="{fs}" font-weight="500">'
            f'<tspan fill="{RAMP[3]}">&gt; </tspan><tspan fill="{TITLE}">{esc(key_part)}</tspan><tspan fill="{RAMP[3]}">{esc(val_part)}</tspan></text></g>'
        )
        last_end, last_y = X0 + 20 + n * cw + 6, y
    over += f'<rect class="bl" x="{last_end:.0f}" y="{last_y - fs * 0.85:.0f}" width="{fs * 0.5:.0f}" height="{fs * 1.05:.0f}" fill="{TITLE}"/>'
    frame(name, c["title"], c["sub"], pill or c["pill"], levels, over=over, extra_defs=clips, rnd=rnd)


# ------------------------------------------------------------------ projects banner (live from your repos)
def projects_banner(name, c, user, seed):
    lines, count = [], None
    try:
        r = subprocess.run(["gh", "api", f"users/{user}/repos?per_page=30&sort=pushed"], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip()[:200])
        repos = [x for x in json.loads(r.stdout) if not x["fork"] and not x["archived"] and x["name"].lower() != user.lower()]
        count = len(repos)
        for x in repos[:5]:
            lines.append((x["name"], x.get("description") or x.get("language") or "no description yet"))
    except Exception as e:
        print("projects: could not fetch repos:", e)
        if (OUT / name).exists():
            return
    if not lines:
        lines = [tuple(x) for x in c["empty"]]
    pill = f"{count} public repos" if count else "coming soon"
    lines_banner(name, c, seed, lines=lines, pill=pill)


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


# ------------------------------------------------------------------ character sheet (bars light up cell by cell)
def sheet_banner(name, c, seed):
    rnd = random.Random(seed)
    levels = noise(rnd)
    for lv in range(1, 5):
        levels[lv] = [q for q in levels[lv] if not (Y0 + 1 * PITCH <= q[1] <= Y0 + 11 * PITCH and q[0] < X0 + 30 * PITCH)]
    for r in range(1, 12):
        for col in range(30):
            levels[0].append((X0 + col * PITCH, Y0 + r * PITCH))
    stats = c["stats"][:5]
    ncell = 12
    bx_col = 7
    over = ""
    for i, (label, val, note) in enumerate(stats):
        row = 1 + i * 2 + (1 if len(stats) <= 4 else 0) if len(stats) > 4 else 2 + i * 2
        y = Y0 + row * PITCH
        over += f'<text x="{X0 + 10}" y="{y + 15}" {FIRA} font-size="22" font-weight="500" fill="{TITLE}">{esc(label)}</text>'
        for k in range(ncell):
            x = X0 + (bx_col + k) * PITCH
            on = k < val
            fill = TITLE if on else RAMP[1]
            if on:
                over += (f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="4" fill="{fill}" opacity="0"><animate attributeName="opacity" '
                         f'from="0" to="1" begin="{0.4 + i * 0.5 + k * 0.09:.2f}s" dur="0.15s" fill="freeze"/></rect>')
            else:
                over += f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="4" fill="{fill}"/>'
        over += f'<text x="{X0 + (bx_col + ncell) * PITCH + 6}" y="{y + 15}" {FIRA} font-size="20" font-weight="500" fill="{SUB}">{esc(note)}</text>'
    frame(name, c["title"], c["sub"], c["pill"], levels, over=over, rnd=rnd)


# ------------------------------------------------------------------ marquee (two scrolling bands)
def marquee_strip(name, c):
    h = 250
    rows = [(c["top"], 88, 38, "fill", 1), (c["bottom"], 56, 30, "outline", -1)]
    body, css = "", ""
    y = 100
    for idx, (phrase, fs, dur, mode, direction) in enumerate(rows):
        unit = phrase + "   ·   "
        pw = round(len(unit) * fs * 0.56)
        while pw < W + 200:
            unit += unit
            pw = round(len(unit) * fs * 0.56)
        attrs = f'fill="{TITLE}"' if mode == "fill" else f'fill="none" stroke="{RAMP[3]}" stroke-width="1.6"'
        texts = "".join(
            f'<text x="{k * pw}" y="{y}" font-family="Saira, system-ui, sans-serif" font-size="{fs}" font-weight="700" {attrs} '
            f'textLength="{pw}" lengthAdjust="spacingAndGlyphs">{esc(unit)}</text>' for k in range(3)
        )
        a, b = (0, -pw) if direction > 0 else (-pw, 0)
        css += f"@keyframes mq{idx}{{from{{transform:translateX({a}px)}}to{{transform:translateX({b}px)}}}}.mq{idx}{{animation:mq{idx} {dur}s linear infinite}}"
        body += f'<g class="mq{idx}">{texts}</g>'
        y += 112
    fade = (
        f'<defs><linearGradient id="fl" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="fr" x1="1" x2="0"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient></defs>'
        f'<rect width="220" height="{h}" fill="url(#fl)"/><rect x="{W - 220}" width="220" height="{h}" fill="url(#fr)"/>'
    )
    line = f'<rect x="72" y="{h - 8}" width="{W - 144}" height="2" fill="{PILL_STROKE}"/>'
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{esc(c["top"])}">'
        f'<title>{esc(c["top"])}</title><style>{STYLE}{css}</style><rect width="{W}" height="{h}" fill="{BG}"/>{body}{fade}{line}</svg>'
    )
    (OUT / name).write_text(svg)
    print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ code window (typed python)
def code_banner(name, c):
    pal = {"k": TITLE, "n": RAMP[3], "s": "#d0d7de", "c": RAMP[2]}
    lines = c["lines"]
    fs, lh = 30, 46
    cw = fs * 0.6
    x0, wx, wy, ww = 190, 110, 24, W - 220
    top = wy + 64
    h = int(top + len(lines) * lh + 60)
    wh = h - wy - 24
    clips, over = "", ""
    cycle = 22
    for i, segs in enumerate(lines):
        y = top + 30 + i * lh
        text = "".join(t for t, _ in segs)
        n = max(1, len(text))
        t0 = 0.5 + i * 0.85
        vals = ";".join(f"{j * cw:.1f}" for j in range(n + 1))
        kts = ";".join(f"{j / n:.4f}" for j in range(n + 1))
        begins = ";".join(f"{t0 + k * cycle:.2f}s" for k in range(30))
        clips += (
            f'<clipPath id="c{i}"><rect x="{x0}" y="{y - 34}" width="0" height="{lh}">'
            f'<animate attributeName="width" values="{vals}" keyTimes="{kts}" calcMode="discrete" dur="{n * 0.03:.2f}s" begin="{begins}" fill="freeze"/></rect></clipPath>'
        )
        tsp = "".join(f'<tspan fill="{pal[col]}">{esc(t)}</tspan>' for t, col in segs)
        over += (f'<text x="{x0 - 40}" y="{y}" {FIRA} font-size="22" fill="{RAMP[2]}" text-anchor="end">{i + 1}</text>'
                 f'<g clip-path="url(#c{i})"><text x="{x0}" y="{y}" {FIRA} font-size="{fs}" font-weight="500">{tsp}</text></g>')
    li = len(lines) - 1
    lx = x0 + len("".join(t for t, _ in lines[li])) * cw + 4
    over += f'<rect class="bl" x="{lx:.0f}" y="{top + 30 + li * lh - 28}" width="{cw:.0f}" height="34" fill="{TITLE}"/>'
    dots = "".join(f'<circle cx="{wx + 36 + k * 30}" cy="{wy + 32}" r="8" fill="{col}"/>' for k, col in enumerate([RAMP[2], RAMP[3], TITLE]))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="me.py: a short python class describing me">'
        f'<title>me.py</title><style>{STYLE}</style><defs>{clips}</defs><rect width="{W}" height="{h}" fill="{BG}"/>'
        f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="22" fill="{PILL_BG}" stroke="{PILL_STROKE}" stroke-width="2"/>'
        f'<rect x="{wx}" y="{wy}" width="{ww}" height="64" rx="22" fill="#1b212a"/><rect x="{wx}" y="{wy + 40}" width="{ww}" height="24" fill="#1b212a"/>'
        f'{dots}<text x="{W / 2}" y="{wy + 41}" text-anchor="middle" {FIRA} font-size="22" font-weight="500" fill="{SUB}">{esc(c["file"])}</text>{over}</svg>'
    )
    (OUT / name).write_text(svg)
    print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ knight's tour (animated chessboard)
def knight_tour(name, c):
    n, sq = 8, 46
    moves = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
    pos, seen, path = (0, 0), {(0, 0)}, [(0, 0)]

    def nxt(p):
        return [(p[0] + a, p[1] + b) for a, b in moves if 0 <= p[0] + a < n and 0 <= p[1] + b < n and (p[0] + a, p[1] + b) not in seen]

    while len(path) < 64:
        opts = nxt(pos)
        if not opts:
            raise SystemExit("tour failed")
        pos = min(opts, key=lambda q: (len(nxt(q)), q))  # Warnsdorff
        seen.add(pos)
        path.append(pos)
    h = 420
    bx, by = (W - n * sq) / 2, (h - n * sq) / 2
    T = 64 * 0.4
    board = "".join(
        f'<rect x="{bx + i * sq}" y="{by + j * sq}" width="{sq}" height="{sq}" fill="{RAMP[1] if (i + j) % 2 else RAMP[0]}"/>' for i in range(n) for j in range(n)
    )
    glow = ""
    for k, p in enumerate(path):
        t = k / 64
        kt = [0, t, t + 0.0001, min(t + 0.06, 0.99), 0.995, 1.0]
        for a in range(1, len(kt)):
            kt[a] = max(kt[a], kt[a - 1] + 0.00001)
        kt[-1] = 1.0
        glow += (f'<rect x="{bx + p[0] * sq}" y="{by + p[1] * sq}" width="{sq}" height="{sq}" fill="{TITLE}" opacity="0">'
                 f'<animate attributeName="opacity" values="0;0;1;.5;.5;0" keyTimes="{";".join(f"{v:.5f}" for v in kt)}" dur="{T}s" repeatCount="indefinite"/></rect>')
    pts = [(bx + p[0] * sq + sq / 2, by + p[1] * sq + sq / 2) for p in path]
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    kp = ";".join(f"{i / 63:.5f}" for i in range(64))
    anim = f'dur="{T}s" repeatCount="indefinite" path="{d}" keyPoints="{kp}" keyTimes="{kp}" calcMode="linear"'
    dot = f'<g class="motion-only"><circle r="15" fill="#fff" opacity=".2"><animateMotion {anim}/></circle><circle r="7" fill="#fff"><animateMotion {anim}/></circle></g>'

    def L(y, t, f, w, col):
        return f'<text x="72" y="{y}" font-family="Saira, system-ui, sans-serif" font-size="{f}" font-weight="{w}" fill="{col}">{esc(t)}</text>'

    left = L(170, c["title"], 76, 700, TITLE) + L(222, c["sub1"], 34, 400, SUB) + L(266, c["sub2"], 34, 400, SUB)
    rx = bx + n * sq + 90
    right = "".join(
        f'<text x="{rx}" y="{150 + i * 56}" {FIRA} font-size="30" font-weight="500" fill="{TITLE if i == 0 else SUB}">&gt; {esc(t)}</text>' for i, t in enumerate(c["right"])
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="A knight visiting every square of a chessboard once">'
        f'<title>Knight tour</title><style>{STYLE}</style><rect width="{W}" height="{h}" fill="{BG}"/>'
        f'<rect x="{bx - 10}" y="{by - 10}" width="{n * sq + 20}" height="{n * sq + 20}" rx="14" fill="none" stroke="{PILL_STROKE}" stroke-width="2"/>{board}{glow}{dot}{left}{right}</svg>'
    )
    (OUT / name).write_text(svg)
    print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ contact buttons
def button_banner(name, c):
    w, h = 760, 150
    cx, cy = 78, h / 2
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(c["label"])}: {esc(c["value"])}">'
        f'<title>{esc(c["label"])}: {esc(c["value"])}</title><style>{STYLE}'
        f'.sw{{animation:sw 4.5s ease-in-out infinite}}@keyframes sw{{from{{transform:translateX(-260px) skewX(-18deg)}}to{{transform:translateX({w + 260}px) skewX(-18deg)}}}}'
        f'.ring{{transform-origin:{cx}px {cy}px;animation:rg 2.4s ease-out infinite}}@keyframes rg{{from{{transform:scale(1);opacity:.55}}to{{transform:scale(2.1);opacity:0}}}}</style>'
        f'<defs><clipPath id="p"><rect x="4" y="4" width="{w - 8}" height="{h - 8}" rx="{(h - 8) / 2}"/></clipPath>'
        f'<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
        f'<rect x="4" y="4" width="{w - 8}" height="{h - 8}" rx="{(h - 8) / 2}" fill="{PILL_BG}" stroke="{RAMP[2]}" stroke-width="2.5"/>'
        f'<g clip-path="url(#p)" class="motion-only"><rect class="sw" x="0" y="0" width="240" height="{h}" fill="url(#g)"/></g>'
        f'<circle class="ring motion-only" cx="{cx}" cy="{cy}" r="16" fill="none" stroke="{TITLE}" stroke-width="2"/>'
        f'<circle cx="{cx}" cy="{cy}" r="16" fill="{TITLE}"/>'
        f'<text x="124" y="{cy - 6}" {FIRA} font-size="22" font-weight="500" fill="{SUB}" letter-spacing="3">{esc(c["label"].upper())}</text>'
        f'<text x="124" y="{cy + 34}" {FIRA} font-size="{c.get("fs", 30)}" font-weight="500" fill="{TITLE}">{esc(c["value"])}</text></svg>'
    )
    (OUT / name).write_text(svg)
    print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ quests (progress bars that fill)
def quests_banner(name, c):
    h = 380
    x1, bw = 560, 860
    cyc = 18
    out = f'<text x="72" y="70" font-family="Saira, system-ui, sans-serif" font-size="46" font-weight="700" fill="{TITLE}">{esc(c["title"])}</text>'
    out += f'<text x="72" y="108" font-family="Saira, system-ui, sans-serif" font-size="26" fill="{SUB}">{esc(c["sub"])}</text>'
    for i, (label, pct) in enumerate(c["quests"][:4]):
        y = 160 + i * 52
        begins = ";".join(f"{0.4 + i * 0.4 + k * cyc:.2f}s" for k in range(40))
        out += (
            f'<text x="72" y="{y + 8}" {FIRA} font-size="26" font-weight="500" fill="{TITLE}">{esc(label)}</text>'
            f'<rect x="{x1}" y="{y - 14}" width="{bw}" height="26" rx="13" fill="{RAMP[1]}"/>'
            f'<rect x="{x1}" y="{y - 14}" width="0" height="26" rx="13" fill="{TITLE}"><animate attributeName="width" values="0;{bw * pct / 100:.0f}" dur="1.6s" begin="{begins}" fill="freeze" calcMode="spline" keySplines=".2 .7 .2 1" keyTimes="0;1"/></rect>'
            f'<text x="{x1 + bw + 24}" y="{y + 8}" {FIRA} font-size="26" font-weight="500" fill="{SUB}">{pct}%</text>'
        )
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="Quests in progress"><title>Quests</title>'
           f'<style>{STYLE}</style><rect width="{W}" height="{h}" fill="{BG}"/>{out}</svg>')
    (OUT / name).write_text(svg); print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ barbell (rep counter)
def lift_banner(name, c):
    h = 380
    cx, fy = 1030, 330
    dur, reps = 2.6, 5
    plates = [(34, 190), (28, 160), (22, 125), (16, 90)]
    g = f'<rect x="{cx - 470}" y="{-4}" width="940" height="8" rx="4" fill="{RAMP[3]}"/>'
    for sgn in (-1, 1):
        x = cx + sgn * 150
        for wdt, ht in plates:
            xx = x if sgn > 0 else x - wdt
            g += f'<rect x="{xx}" y="{-ht / 2}" width="{wdt}" height="{ht}" rx="6" fill="{TITLE if wdt == 34 else RAMP[3] if wdt == 28 else RAMP[2] if wdt == 22 else RAMP[1]}" stroke="{BG}" stroke-width="2"/>'
            x += sgn * (wdt + 3)
        g += f'<rect x="{cx + sgn * 118 - 6}" y="-12" width="12" height="24" rx="3" fill="{RAMP[2]}"/>'
    rise = 70
    ease = 'calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"'
    bar = (f'<g><animateTransform attributeName="transform" type="translate" values="0 {fy - 100};0 {fy - 100 - rise};0 {fy - 100}" dur="{dur}s" repeatCount="indefinite" {ease}/>{g}</g>')
    floor = f'<rect x="{cx - 560}" y="{fy + 20}" width="1120" height="3" fill="{PILL_STROKE}"/>'
    shadow = (f'<ellipse cx="{cx}" cy="{fy + 12}" rx="420" ry="8" fill="#000" opacity=".35"><animate attributeName="rx" values="420;330;420" dur="{dur}s" repeatCount="indefinite" {ease}/></ellipse>')
    counts = ""
    for r in range(reps):
        a, b = r / reps, (r + 1) / reps
        counts += (f'<text x="72" y="300" {FIRA} font-size="60" font-weight="500" fill="{TITLE}" opacity="0">rep {r + 1}/{reps}'
                   f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;{a + 0.001:.4f};{b - 0.001:.4f};{b:.4f};1" calcMode="discrete" dur="{dur * reps}s" repeatCount="indefinite"/></text>')
    title = (f'<text x="72" y="130" font-family="Saira, system-ui, sans-serif" font-size="96" font-weight="700" fill="{TITLE}">{esc(c["title"])}</text>'
             f'<text x="72" y="190" font-family="Saira, system-ui, sans-serif" font-size="38" fill="{SUB}">{esc(c["sub"])}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="An animated barbell doing reps"><title>Lift</title>'
           f'<style>{STYLE}</style><rect width="{W}" height="{h}" fill="{BG}"/>{floor}{shadow}{bar}{title}{counts}</svg>')
    (OUT / name).write_text(svg); print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ focus ring (pomodoro)
def focus_banner(name, c):
    import math
    h = 380
    cx, cy, r = 900, 190, 118
    circ = 2 * math.pi * r
    t = c.get("seconds", 25)
    ring = (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{RAMP[1]}" stroke-width="18"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TITLE}" stroke-width="18" stroke-linecap="round" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" transform="rotate(-90 {cx} {cy})">'
            f'<animate attributeName="stroke-dashoffset" values="{circ:.1f};0;0;{circ:.1f}" keyTimes="0;.82;.94;1" dur="{t}s" repeatCount="indefinite"/></circle>'
            f'<g class="motion-only"><g><animateTransform attributeName="transform" type="rotate" values="-90 {cx} {cy};270 {cx} {cy}" dur="{t * .82:.1f}s" repeatCount="indefinite"/>'
            f'<circle cx="{cx + r}" cy="{cy}" r="7" fill="#fff"/></g></g>')
    inner = (f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" {FIRA} font-size="30" font-weight="500" fill="{TITLE}">{esc(c["inside"])}</text>'
             f'<text x="{cx}" y="{cy + 44}" text-anchor="middle" {FIRA} font-size="22" font-weight="500" fill="{SUB}">{esc(c["inside2"])}</text>')
    title = (f'<text x="72" y="130" font-family="Saira, system-ui, sans-serif" font-size="96" font-weight="700" fill="{TITLE}">{esc(c["title"])}</text>'
             f'<text x="72" y="190" font-family="Saira, system-ui, sans-serif" font-size="38" fill="{SUB}">{esc(c["sub"])}</text>')
    right = "".join(f'<text x="{cx + r + 110}" y="{150 + i * 56}" {FIRA} font-size="30" font-weight="500" fill="{TITLE if i == 0 else SUB}">&gt; {esc(x)}</text>' for i, x in enumerate(c["right"]))
    pill = f'<rect x="72" y="259" width="{18 * len(c["pill"]) + 38}" height="53" rx="26.5" fill="{PILL_BG}" stroke="{PILL_STROKE}" stroke-width="2"/><text x="91" y="296.5" {FIRA} font-size="30" font-weight="500" fill="{TITLE}">{esc(c["pill"])}</text>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="A focus timer ring filling up"><title>Focus</title>'
           f'<style>{STYLE}</style><rect width="{W}" height="{h}" fill="{BG}"/>{title}{pill}{ring}{inner}{right}</svg>')
    (OUT / name).write_text(svg); print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ equalizer
def eq_banner(name, c):
    rnd = random.Random(7)
    h = 300
    n, bw, gap = 34, 16, 12
    x0 = W - 72 - n * (bw + gap)
    css, bars = "", ""
    for i in range(n):
        env = 0.35 + 0.65 * math.sin(math.pi * (i + 1) / (n + 1)) ** 1.2
        mx = int(200 * env * (0.55 + 0.45 * rnd.random()))
        d = 0.7 + rnd.random() * 1.1
        delay = -rnd.random() * 2
        bars += f'<rect class="eb" x="{x0 + i * (bw + gap)}" y="250" width="{bw}" height="{mx}" rx="4" fill="{TITLE if i % 7 == 3 else RAMP[3] if i % 3 else RAMP[2]}" style="animation-duration:{d:.2f}s;animation-delay:{delay:.2f}s"/>'
    css = ".eb{transform-box:fill-box;transform-origin:50% 100%;transform:translateY(-100%);animation:eqb ease-in-out infinite alternate}@keyframes eqb{from{transform:translateY(-100%) scaleY(.12)}to{transform:translateY(-100%) scaleY(1)}}"
    title = (f'<text x="72" y="130" font-family="Saira, system-ui, sans-serif" font-size="96" font-weight="700" fill="{TITLE}">{esc(c["title"])}</text>'
             f'<text x="72" y="190" font-family="Saira, system-ui, sans-serif" font-size="38" fill="{SUB}">{esc(c["sub"])}</text>'
             f'<rect x="72" y="219" width="{18 * len(c["pill"]) + 38}" height="53" rx="26.5" fill="{PILL_BG}" stroke="{PILL_STROKE}" stroke-width="2"/><text x="91" y="256.5" {FIRA} font-size="30" font-weight="500" fill="{TITLE}">{esc(c["pill"])}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="An audio equalizer"><title>Sound</title>'
           f'<style>{STYLE}{css}</style><rect width="{W}" height="{h}" fill="{BG}"/>{title}{bars}</svg>')
    (OUT / name).write_text(svg); print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ cycling typewriter tagline
def cycle_banner(name, c):
    phrases = c["phrases"]
    prefix = c.get("prefix", "i'm ")
    fs = 60
    cw = fs * 0.6
    h = 190
    x0 = 72 + (len(prefix) + 2) * cw + 4
    N = len(phrases)
    slot = 6.0
    D = N * slot
    events, clips, texts = [], "", ""
    for i, ph in enumerate(phrases):
        n = len(ph)
        t = i * slot + 0.3
        ev = [(0.0, 0)]
        for j in range(1, n + 1):
            ev.append((t + j * 0.06, j))
        t_hold = t + n * 0.06 + 1.6
        for j in range(n - 1, -1, -1):
            ev.append((t_hold + (n - j) * 0.03, j))
        events += ev[1:]
        ev.append((D, 0))
        kts = ";".join(f"{min(e[0] / D, 1):.5f}" for e in ev)
        vals = ";".join(f"{e[1] * cw:.1f}" for e in ev)
        clips += (f'<clipPath id="y{i}"><rect x="{x0}" y="30" width="0" height="120"><animate attributeName="width" values="{vals}" keyTimes="{kts}" calcMode="discrete" dur="{D}s" repeatCount="indefinite"/></rect></clipPath>')
        texts += f'<g clip-path="url(#y{i})"><text x="{x0}" y="{h / 2 + fs * 0.35:.1f}" {FIRA} font-size="{fs}" font-weight="500" fill="{TITLE}">{esc(ph)}</text></g>'
    events.sort()
    ev = [(0.0, 0)] + events + [(D, 0)]
    kts = ";".join(f"{min(e[0] / D, 1):.5f}" for e in ev)
    vals = ";".join(f"{x0 + e[1] * cw + 4:.1f}" for e in ev)
    caret = (f'<rect class="bl" x="{x0 + 4}" y="{h / 2 - 34}" width="{cw * 0.55:.0f}" height="68" fill="{TITLE}">'
             f'<animate attributeName="x" values="{vals}" keyTimes="{kts}" calcMode="discrete" dur="{D}s" repeatCount="indefinite"/></rect>')
    pre = f'<text x="72" y="{h / 2 + fs * 0.35:.1f}" {FIRA} font-size="{fs}" font-weight="500" fill="{RAMP[3]}">&gt; {esc(prefix)}</text>'
    pre = pre.replace(f'&gt; {esc(prefix)}', esc("> " + prefix)).replace("<text", "<text", 1)
    line = f'<rect x="72" y="{h - 6}" width="{W - 144}" height="2" fill="{PILL_STROKE}"/>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="Rotating tagline: {esc("; ".join(phrases))}">'
           f'<title>{esc(prefix)}{esc(phrases[0])}</title><style>{STYLE}</style><defs>{clips}</defs><rect width="{W}" height="{h}" fill="{BG}"/>{pre}{texts}{caret}{line}</svg>')
    (OUT / name).write_text(svg); print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ the loop (animated)
def loop_strip(name, c):
    steps = c["steps"][:6]
    caption = c.get("caption", "")
    fs, ph, gap, h = 44, 84, 74, 250
    cw = fs * 0.6
    widths = [len(t) * cw + 40 + 46 for t in steps]
    total = sum(widths) + gap * (len(steps) - 1)
    x, y = (W - total) / 2, 44
    yc = y + ph / 2
    pills, conn, centers = "", "", []
    n = len(steps)
    for i, (t, wd) in enumerate(zip(steps, widths)):
        delay = i * 8 / max(1, n - 1) - 0.5
        pills += (
            f'<rect x="{x:.1f}" y="{y}" width="{wd:.1f}" height="{ph}" rx="{ph / 2}" fill="{PILL_BG}" stroke="{PILL_STROKE}" stroke-width="2"/>'
            f'<circle class="lp" cx="{x + 38:.1f}" cy="{yc}" r="8" fill="{TITLE}" style="animation-delay:{delay:.2f}s"/>'
            f'<text x="{x + 64:.1f}" y="{yc + 15}" {FIRA} font-size="{fs}" font-weight="500" fill="{TITLE}">{esc(t)}</text>'
        )
        centers.append(x + 38)
        if i < n - 1:
            x1, x2 = x + wd + 10, x + wd + gap - 10
            conn += (
                f'<line x1="{x1:.1f}" y1="{yc}" x2="{x2 - 8:.1f}" y2="{yc}" stroke="{RAMP[2]}" stroke-width="3"/>'
                f'<path d="M{x2 - 12:.1f} {yc - 9}L{x2:.1f} {yc}L{x2 - 12:.1f} {yc + 9}" fill="none" stroke="{RAMP[2]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        x += wd + gap
    d = f"M{centers[0]:.1f} {yc}" + "".join(f" L{cx:.1f} {yc}" for cx in centers[1:])
    seg = [centers[i + 1] - centers[i] for i in range(n - 1)]
    tot = sum(seg)
    cum = [0.0]
    for sg in seg:
        cum.append(cum[-1] + sg / tot)
    kp = ";".join(f"{v:.4f}" for v in cum)
    kt = ";".join(f"{i / (n - 1):.4f}" for i in range(n))
    dot = (
        f'<g class="motion-only"><circle r="13" fill="#ffffff" opacity="0.18"><animateMotion dur="8s" repeatCount="indefinite" path="{d}" keyPoints="{kp}" keyTimes="{kt}" calcMode="linear"/></circle>'
        f'<circle r="6" fill="#ffffff"><animateMotion dur="8s" repeatCount="indefinite" path="{d}" keyPoints="{kp}" keyTimes="{kt}" calcMode="linear"/></circle></g>'
    )
    cap = f'<text x="{W / 2}" y="{h - 34}" text-anchor="middle" {FIRA} font-size="26" font-weight="500" fill="{SUB}" letter-spacing="4">{esc(caption)}</text>' if caption else ""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="The loop: {esc(" then ".join(steps))}">'
        f'<title>The loop: {esc(" then ".join(steps))}</title><style>{STYLE}</style>'
        f'<rect width="{W}" height="{h}" fill="{BG}"/>{conn}{pills}{dot}{cap}</svg>'
    )
    (OUT / name).write_text(svg)
    print("wrote", name, len(svg) // 1024, "KB")


# ------------------------------------------------------------------ footer strip
def footer_strip(name, c, seed):
    rnd = random.Random(seed)
    h = 164
    cols = 59
    rows = 5
    text = c["text"] + "  ·  built " + datetime.datetime.utcnow().strftime("%d %b %Y")
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
    cycle_banner("tagline.svg", CFG["tagline"])
    marquee_strip("marquee.svg", CFG["marquee"])
    word_banner("about.svg", CFG["about"], 21)
    lines_banner("now.svg", CFG["now"], 8)
    lift_banner("lift.svg", CFG["lift"])
    eq_banner("sound.svg", CFG["sound"])
    quests_banner("quests.svg", CFG["quests"])
    focus_banner("focus.svg", CFG["focus"])
    code_banner("code.svg", CFG["code"])
    loop_strip("loop.svg", CFG["loop"])
    tools_strip("tools.svg", CFG["tools"])
    sheet_banner("sheet.svg", CFG["sheet"], 63)
    button_banner("btn-discord.svg", CFG["btn_discord"])
    button_banner("btn-email.svg", CFG["btn_email"])
    knight_tour("knight.svg", CFG["knight"])
    lines_banner("games.svg", CFG["games"], 77)
    word_banner("numbers.svg", CFG["numbers"], 99)
    projects_banner("projects.svg", CFG["projects"], user, 5)
    lines_banner("beyond.svg", CFG["beyond"], 41)
    activity_banner("activity.svg", CFG["activity"], user, 13)
    word_banner("contact.svg", CFG["contact"], 55)
    footer_strip("footer.svg", CFG["footer"], 89)


if __name__ == "__main__":
    main()
