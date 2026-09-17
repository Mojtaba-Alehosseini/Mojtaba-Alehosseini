#!/usr/bin/env python3
"""Rebuild the profile banners and the repository count. Standard library only."""

import json
import math
import os
import re
import urllib.request

DATA_URL = ("https://raw.githubusercontent.com/Mojtaba-Alehosseini/"
            "Mojtaba-Alehosseini.github.io/main/repos-data.js")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIGHT_PATH = os.path.join(ROOT, "assets", "banner-light.svg")
DARK_PATH = os.path.join(ROOT, "assets", "banner-dark.svg")
README_PATH = os.path.join(ROOT, "README.md")

FIELD_C = {"ML & Data": "#C0552C", "Simulation & OR": "#B0812F",
           "Systems & Algorithms": "#7E8B45", "Web & Interactive": "#4C8A70",
           "Blockchain": "#43788F", "Profile / Meta": "#6C6E92",
           None: "#8C857A"}
ORDER = ["ML & Data", "Simulation & OR", "Systems & Algorithms",
         "Web & Interactive", "Blockchain", "Profile / Meta", None]


def sizeT(kb):
    t = (math.log(kb + 1) - math.log(2)) / (math.log(770159) - math.log(2))
    return max(0, min(1, t))


def banner(R, theme):
    paper, ink, soft, muted = ("#F7F3EA", "#18181B", "#3F3F46", "#6F6A62") \
        if theme == "light" else ("#0D1117", "#F4EFE3", "#D2CDC0", "#8F8A82")
    W, H = 1200, 320
    cx, cy = 1030, 160
    RR = 108
    reps = [r for d in ORDER
            for r in sorted([x for x in R if x["d"] == d], key=lambda z: -z["s"])]
    n = len(reps)
    dots = []
    gaps = len(ORDER) * 4.0
    usable = 360 - gaps
    cur = 0
    for d in ORDER:
        grp = [r for r in reps if r["d"] == d]
        span = usable * len(grp) / n
        for j, r in enumerate(grp):
            a = cur + 2 + (span - 4) * (j / (len(grp) - 1) if len(grp) > 1 else 0.5)
            rad = math.radians(a)
            dots.append(f'<circle cx="{cx+RR*math.sin(rad):.1f}" cy="{cy-RR*math.cos(rad):.1f}" r="{4+sizeT(r["s"])*4:.1f}" fill="{FIELD_C[d]}"/>')
        cur += span + 4
    font = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
    mono = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Mojtaba Alehosseini, AI engineer and data analyst">
<rect width="{W}" height="{H}" rx="18" fill="{paper}"/>
<text x="72" y="108" font-family="{font}" font-size="44" font-weight="700" fill="{ink}" letter-spacing="-1">Mojtaba Alehosseini</text>
<text x="72" y="150" font-family="{font}" font-size="21" fill="{soft}">AI engineer and data analyst</text>
<text x="72" y="180" font-family="{font}" font-size="18" fill="{muted}">M.Sc. Computer Science (Artificial Intelligence), University of Genoa</text>
<g transform="translate(72,212)"><rect x="0" y="0" width="372" height="42" rx="21" fill="{ink}"/><text x="186" y="27" text-anchor="middle" font-family="{font}" font-size="18" font-weight="600" fill="{paper}">mojtaba-alehosseini.github.io</text></g>
<text x="72" y="284" font-family="{mono}" font-size="13" fill="{muted}" letter-spacing="1.5">CV · INTERACTIVE MAP OF EVERY REPOSITORY · CONTACT</text>
<circle cx="{cx}" cy="{cy}" r="{RR}" fill="none" stroke="{ink}" stroke-opacity="0.12"/>
{''.join(dots)}
<text x="{cx}" y="{cy-4}" text-anchor="middle" font-family="{font}" font-size="30" font-weight="700" fill="{ink}">{n}</text>
<text x="{cx}" y="{cy+20}" text-anchor="middle" font-family="{mono}" font-size="12" fill="{muted}" letter-spacing="2">REPOSITORIES</text>
</svg>'''


def fetch_records():
    """Read the repository array out of the published repos-data.js."""
    request = urllib.request.Request(DATA_URL)
    request.add_header("User-Agent", "profile-banner-sync")
    with urllib.request.urlopen(request, timeout=60) as response:
        text = response.read().decode("utf-8")
    return json.loads(text[text.index("["):text.rindex("]") + 1])


def write_svg(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def update_readme(count):
    """Replace the count in 'these N repositories'. The rest stays as it is."""
    with open(README_PATH, "rb") as handle:
        old = handle.read()
    found = re.search(rb"these (\d+) repositories", old)
    if not found:
        print("README: phrase 'these N repositories' not found")
        return
    new = re.sub(rb"these \d+ repositories",
                 b"these %d repositories" % count, old)
    if new != old:
        with open(README_PATH, "wb") as handle:
            handle.write(new)
    print("README: {} -> {} repositories".format(
        found.group(1).decode(), count))


def main():
    records = fetch_records()
    write_svg(LIGHT_PATH, banner(records, "light"))
    write_svg(DARK_PATH, banner(records, "dark"))
    print("banners rebuilt for {} repositories".format(len(records)))
    update_readme(len(records))


if __name__ == "__main__":
    main()
