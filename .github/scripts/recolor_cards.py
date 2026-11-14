#!/usr/bin/env python3
"""Recolor the generated github_dark summary cards into the Noir monochrome theme
and write them to profile-summary-card-output/lynkquk/."""
import pathlib

SRC = pathlib.Path("profile-summary-card-output/github_dark")
DST = pathlib.Path("profile-summary-card-output/lynkquk")
MAP = {
    "#2e343b": "#2c313a",  # border
    "#0366d6": "#f5f5f5",  # titles
    "#40c463": "#f5f5f5",  # bars / graph
    "#77909c": "#8a8f98",  # text
    "#586e75": "#6e7681",  # muted
    "#e34c26": "#c9d1d9",  # language accent
}

DST.mkdir(parents=True, exist_ok=True)
for f in sorted(SRC.glob("*.svg")):
    s = f.read_text()
    for a, b in MAP.items():
        s = s.replace(a, b).replace(a.upper(), b)
    (DST / f.name).write_text(s)
    print("recolored", f.name)
