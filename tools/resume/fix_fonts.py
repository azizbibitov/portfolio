#!/usr/bin/env python3
"""Make the Carlito faces extracted from the resume PDF usable in a browser.

Two things are wrong with a font lifted out of a PDF:
  1. no OS/2 table - Chrome's OTS sanitizer rejects the font outright;
  2. the cmap is the PDF's internal code->glyph map, not Unicode, so text
     in HTML would map to nothing.

We rebuild the cmap from the PDF's own ToUnicode CMap (code -> unicode) and
synthesize an OS/2 table. Glyph outlines and metrics are untouched, so the
result renders identically to the original PDF.
"""
import re
import sys
import zlib
from pathlib import Path

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.ttLib.tables.O_S_2f_2 import Panose

PDF = Path(sys.argv[1])
HERE = Path(__file__).parent
data = PDF.read_bytes()

objs = {
    int(m.group(1)): m.group(2)
    for m in re.finditer(rb"(\d+)\s+0\s+obj(.*?)endobj", data, re.S)
}


def stream(num):
    body = objs[num]
    raw = body[body.find(b"stream") + 6 : body.rfind(b"endstream")].lstrip(b"\r\n")
    try:
        return zlib.decompress(raw)
    except zlib.error:
        return raw


def utf16be(hexstr):
    """A ToUnicode destination is UTF-16BE and may be multi-char (ligatures)."""
    return bytes.fromhex(hexstr.decode()).decode("utf-16-be", "ignore")


def parse_tounicode(text):
    """code -> unicode string, from the bfchar/bfrange sections of a CMap."""
    out = {}
    for block in re.findall(rb"beginbfchar(.*?)endbfchar", text, re.S):
        for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
            out[int(src, 16)] = utf16be(dst)
    for block in re.findall(rb"beginbfrange(.*?)endbfrange", text, re.S):
        for lo, hi, dst in re.findall(
            rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block
        ):
            lo, hi, base = int(lo, 16), int(hi, 16), utf16be(dst)
            if len(base) != 1:
                continue
            for i in range(hi - lo + 1):
                out[lo + i] = chr(ord(base) + i)
    return out


# Pair each embedded font file with its ToUnicode map, via the font dict.
jobs = []
for body in objs.values():
    base = re.search(rb"/BaseFont\s*/(\S+?)[\s/>\]]", body)
    desc = re.search(rb"/FontDescriptor\s+(\d+)\s+0\s+R", body)
    tou = re.search(rb"/ToUnicode\s+(\d+)\s+0\s+R", body)
    if not (base and desc and tou):
        continue
    ff = re.search(rb"/FontFile2\s+(\d+)\s+0\s+R", objs[int(desc.group(1))])
    if ff:
        name = base.group(1).decode().split("+")[-1]
        jobs.append((name, int(ff.group(1)), parse_tounicode(stream(int(tou.group(1))))))

for name, ff_ref, to_uni in jobs:
    path = HERE / "fonts" / f"{name}.ttf"
    path.write_bytes(stream(ff_ref))
    font = TTFont(path)

    # code -> glyph name, from the PDF's own (1,0) subtable
    code_to_glyph = {}
    for sub in font["cmap"].tables:
        code_to_glyph.update(sub.cmap)

    # Ligature glyphs ("tt", "fi", ...) decode to multi-char strings; mapping
    # them would hijack the plain letter's codepoint, so skip them.
    unicode_map = {}
    for code, text in sorted(to_uni.items()):
        glyph = code_to_glyph.get(code)
        if glyph and len(text) == 1 and ord(text) not in unicode_map:
            unicode_map[ord(text)] = glyph

    # a real Unicode cmap: (3,1) format 4, plus (0,3) for good measure
    new_cmap = newTable("cmap")
    new_cmap.tableVersion = 0
    new_cmap.tables = []
    for platform, encoding in ((3, 1), (0, 3)):
        sub = CmapSubtable.newSubtable(4)
        sub.platformID, sub.platEncID, sub.format = platform, encoding, 4
        sub.language = 0
        sub.cmap = dict(unicode_map)
        new_cmap.tables.append(sub)
    font["cmap"] = new_cmap

    head, hhea = font["head"], font["hhea"]
    bold, italic = "Bold" in name, "Italic" in name
    os2 = newTable("OS/2")
    os2.version = 4
    os2.xAvgCharWidth = 500
    os2.usWeightClass = 700 if bold else 400
    os2.usWidthClass = 5
    os2.fsType = 0
    os2.ySubscriptXSize = os2.ySuperscriptXSize = 650
    os2.ySubscriptYSize = os2.ySuperscriptYSize = 600
    os2.ySubscriptXOffset = os2.ySuperscriptXOffset = 0
    os2.ySubscriptYOffset, os2.ySuperscriptYOffset = 75, 350
    os2.yStrikeoutSize, os2.yStrikeoutPosition = 50, 258
    os2.sFamilyClass = 0
    os2.panose = Panose()
    os2.ulUnicodeRange1 = 0x800000AF
    os2.ulUnicodeRange2 = os2.ulUnicodeRange3 = os2.ulUnicodeRange4 = 0
    os2.achVendID = "NONE"
    os2.fsSelection = (0x01 if italic else 0) | (0x20 if bold else 0)
    if not (bold or italic):
        os2.fsSelection = 0x40
    codes = sorted(unicode_map) or [0x20]
    os2.usFirstCharIndex, os2.usLastCharIndex = min(0xFFFF, codes[0]), min(0xFFFF, codes[-1])
    os2.sTypoAscender, os2.sTypoDescender = hhea.ascent, hhea.descent
    os2.sTypoLineGap = hhea.lineGap
    os2.usWinAscent = max(hhea.ascent, head.yMax)
    os2.usWinDescent = abs(min(hhea.descent, head.yMin))
    os2.ulCodePageRange1, os2.ulCodePageRange2 = 0x00000001, 0
    os2.sxHeight, os2.sCapHeight = 500, 700
    os2.usDefaultChar, os2.usBreakChar, os2.usMaxContext = 0, 32, 2
    font["OS/2"] = os2

    font.save(path)
    print(f"{name}: {len(unicode_map)} unicode glyphs mapped, OS/2 added")
