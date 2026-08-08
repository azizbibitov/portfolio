#!/usr/bin/env python3
"""Geometry diff between two resume PDFs, to check a rebuild against the old one.

Compares every text line's position and width. Lines you deliberately added or
removed show up as TEXT DIFF, and everything after them legitimately shifts;
what matters is that the untouched lines stay within a point or so.

Usage: compare.py <old.pdf> <new.pdf>   (needs pdftotext from poppler)
"""
import re
import subprocess
import sys

TOLERANCE_PT = 1.0


def lines(pdf):
    xml = subprocess.run(
        ["pdftotext", "-bbox-layout", pdf, "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    out = []
    for pno, page in enumerate(re.findall(r"<page .*?</page>", xml, re.S), 1):
        for m in re.finditer(
            r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>',
            page, re.S,
        ):
            text = " ".join(re.findall(r"<word[^>]*>(.*?)</word>", m.group(5)))
            out.append((pno, float(m.group(1)), float(m.group(2)), float(m.group(3)), text))
    return out


old, new = lines(sys.argv[1]), lines(sys.argv[2])
print(f"{sys.argv[1]}: {len(old)} lines\n{sys.argv[2]}: {len(new)} lines\n")

drift = []
for (po, xo, yo, xo2, to), (pn, xn, yn, xn2, tn) in zip(old, new):
    if to != tn:
        print(f"TEXT DIFF\n  old p{po}: {to[:76]}\n  new p{pn}: {tn[:76]}\n")
        continue
    dx, dy, dw = xn - xo, yn - yo, (xn2 - xn) - (xo2 - xo)
    if po != pn:
        print(f"PAGE DIFF p{po} -> p{pn}: {to[:60]}")
    elif max(abs(dx), abs(dy), abs(dw)) > TOLERANCE_PT:
        drift.append((max(abs(dx), abs(dy), abs(dw)), po, dx, dy, dw, to))

if len(old) != len(new):
    print(f"line count differs by {len(new) - len(old):+d}")

drift.sort(reverse=True)
print(f"\n{len(drift)} lines off by more than {TOLERANCE_PT}pt (of {min(len(old), len(new))}):")
for _, p, dx, dy, dw, t in drift[:20]:
    print(f"  p{p} dx={dx:+6.2f} dy={dy:+6.2f} dwidth={dw:+6.2f} | {t[:56]}")
