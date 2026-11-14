#!/usr/bin/env python3
"""Recolor the generated github_dark summary cards into the profile theme
(near-black panels, grey text, red accent) and write them to profile-summary-card-output/lynkquk/."""
import pathlib

SRC = pathlib.Path("profile-summary-card-output/github_dark")
DST = pathlib.Path("profile-summary-card-output/lynkquk")
MAP = {
    "#0d1117": "#151b23",  # panel
    "#2e343b": "#30363d",  # border
    "#0366d6": "#f20707",  # titles
    "#40c463": "#f20707",  # bars / graph
    "#77909c": "#9198a1",  # text
    "#586e75": "#6e7681",  # muted
}

DST.mkdir(parents=True, exist_ok=True)
for f in sorted(SRC.glob("*.svg")):
    s = f.read_text()
    for a, b in MAP.items():
        s = s.replace(a, b).replace(a.upper(), b)
    (DST / f.name).write_text(s)
    print("recolored", f.name)
