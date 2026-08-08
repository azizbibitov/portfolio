#!/usr/bin/env python3
"""Turn the resume .docx into a print-exact HTML for Chrome's print-to-PDF.

macOS `textutil` gives us the docx's real paragraph and run formatting (its
px numbers are Word points). We re-unit those to pt, embed the Carlito faces
that the original resume PDF itself used, and restore the things textutil
drops: the section heading rules, the right-aligned date tab stop, Word's
list indents, and the hyperlinks.

Usage: build_pdf_html.py <resume.docx> <out.html>
"""
import base64
import html as htmllib
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCX = Path(sys.argv[1])
OUT = Path(sys.argv[2])

# Values lifted from the docx itself (word/document.xml):
#   pgMar 1080 twips  -> 54pt page margins
#   right tab  9026   -> 451.3pt from the content left edge
#   heading pBdr sz=6 -> 0.75pt rule, w:space=2 -> 2pt below the text
#   numbering ind     -> bullet 8pt from the margin, text at 18pt
PAGE_MARGIN_PT = 54
TAB_STOP_PT = 451.3
LINE_HEIGHT = 1.22

# 1. docx -> html (keeps fonts, sizes, colors, indents, list structure)
page = subprocess.run(
    ["textutil", "-convert", "html", "-stdout", str(DOCX)],
    capture_output=True, text=True, check=True,
).stdout
body = page.split("<body>", 1)[1].split("</body>", 1)[0]
css = page.split('<style type="text/css">', 1)[1].split("</style>", 1)[0]

# 2. textutil's px values are Word points -> re-unit. The `font:` shorthand
#    also resets line-height, so pin Word's single spacing inside it.
css = re.sub(r"(\d+(?:\.\d+)?)px", r"\1pt", css)
css = re.sub(
    r"font: (\d+(?:\.\d+)?pt) Times",
    rf"font: \1/{LINE_HEIGHT} Carlito, sans-serif",
    css,
)

# 3. Dates: the docx puts them on a right tab stop, textutil emits a raw tab
body = re.sub(
    r'<i><span class="Apple-tab-span">\t</span>([^<]*)</i>',
    r'<i class="date">\1</i>',
    body,
)


# 4. Tag paragraphs by role, so the CSS does not depend on textutil's class
#    numbering (p1, p2, ...), which shifts whenever the document changes.
def tag(match):
    open_tag, inner = match.group(1), match.group(2)
    text = re.sub(r"<[^>]+>", "", inner).strip()
    roles = []
    if 'class="date"' in inner:
        roles.append("hasdate")
    if text and re.fullmatch(r"[A-Z &/]+", text):
        roles.append("sec")
    if not roles:
        return match.group(0)
    return open_tag.replace('class="', f'class="{" ".join(roles)} ', 1) + inner + "</p>"


body = re.sub(r"(<p class=\"[^\"]*\">)(.*?)</p>", tag, body, flags=re.S)

# 5. Restore hyperlinks (textutil drops the anchors)
LINKS = {
    "Portfolio": "https://azizbibitov.github.io/portfolio",
    "LinkedIn": "https://www.linkedin.com/in/aziz-bibitov-707753252/",
    "GitHub": "https://github.com/azizbibitov",
    "Upwork": "https://www.upwork.com/freelancers/~016a583c9e00fc71bb",
}
for label, href in LINKS.items():
    if f">{label}<" in body:
        body = body.replace(f">{label}<", f'><a href="{href}">{label}</a><', 1)
    else:
        print(f"  note: link text {label!r} not found, no anchor added")

email = re.search(r"[\w.+-]+@[\w.-]+\.\w+", re.sub(r"<[^>]+>", "", body))
if email:
    addr = htmllib.escape(email.group(0))
    body = body.replace(f">{addr}<", f'><a href="mailto:{addr}">{addr}</a><', 1)

# 6. Embed the Carlito faces (see fix_fonts.py for where they come from)
faces = []
for style, weight, fname in [
    ("normal", "normal", "Carlito-Regular.ttf"),
    ("normal", "bold", "Carlito-Bold.ttf"),
    ("italic", "normal", "Carlito-Italic.ttf"),
    ("italic", "bold", "Carlito-BoldItalic.ttf"),
]:
    ttf = HERE / "fonts" / fname
    if not ttf.exists():
        sys.exit(f"missing {ttf} - run fix_fonts.py against a reference PDF first")
    b64 = base64.b64encode(ttf.read_bytes()).decode()
    faces.append(
        "@font-face{font-family:Carlito;font-style:%s;font-weight:%s;"
        "src:url(data:font/ttf;base64,%s) format('truetype')}" % (style, weight, b64)
    )

PAGE_CSS = f"""
@page {{ size: Letter; margin: {PAGE_MARGIN_PT}pt; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: Carlito, sans-serif; line-height: {LINE_HEIGHT};
        -webkit-font-smoothing: antialiased; }}
p {{ line-height: {LINE_HEIGHT}; orphans: 2; widows: 2; }}
span.Apple-converted-space {{ white-space: pre-wrap; }}
/* section headings carry a 0.75pt rule, 2pt below the text */
p.sec {{ border-bottom: 0.75pt solid #1f3864; padding-bottom: 2pt;
         page-break-after: avoid; }}
/* dates sit on the docx's right tab stop, which stops short of the right
   margin - so right-align to that, not to the page edge */
p.hasdate {{ position: relative; }}
i.date {{ position: absolute; left: 0; top: 0; width: {TAB_STOP_PT}pt;
          text-align: right; font-style: italic; }}
/* Word's list indents: bullet 8pt from the margin, text at 18pt.
   !important because textutil's own ul.ul1{{list-style-type:disc}} is more
   specific, and its native marker would render on top of the ::before one. */
ul {{ margin: 0; padding-left: 18pt; list-style: none !important; }}
li {{ position: relative; }}
li::before {{ content: "\\2022"; position: absolute; left: -10pt;
              font-weight: normal; font-style: normal; }}
a {{ color: inherit; text-decoration: underline; }}
"""

OUT.write_text(
    "<!DOCTYPE html><html><head><meta charset='utf-8'>"
    f"<style>{''.join(faces)}</style>"
    f"<style>{css}</style><style>{PAGE_CSS}</style></head>"
    f"<body>{body}</body></html>",
    encoding="utf-8",
)
print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
