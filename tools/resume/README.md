# Resume PDF build

Rebuilds `documents/aziz-bibitow-resume.pdf` from `documents/aziz-bibitow-resume.docx`
without Word, Pages, or LibreOffice - and keeps the existing layout, font, and
margins, so the new PDF is indistinguishable from the old one.

## Use it

Edit the `.docx`, then:

```bash
tools/resume/build.sh
```

It prints a geometry diff against the previous PDF and saves that PDF as
`.pdf.bak` before overwriting. Lines you actually changed show up as
`TEXT DIFF`, and everything below them shifts accordingly; anything else
drifting more than a point or so means something in the pipeline needs a look.

## Requirements

- macOS (`textutil` is built in)
- Google Chrome in `/Applications`
- `pdftotext` for the geometry diff only - optional: `brew install poppler`
- `fonttools` only if you ever re-run `fix_fonts.py`: `pip install fonttools`

## How it works

The resume PDF was originally produced by LibreOffice, which sets its text in
Carlito (the metric-compatible Calibri clone). That font is not installed on
this Mac, so matching the original meant recovering it from the PDF itself.

1. **`fix_fonts.py`** pulls the four embedded Carlito subsets out of a
   reference PDF and makes them usable in a browser. A font lifted from a PDF
   needs two repairs: it has no `OS/2` table (Chrome's OTS sanitizer rejects it
   outright), and its cmap is the PDF's internal code-to-glyph map rather than
   Unicode. The Unicode cmap is rebuilt from the PDF's own ToUnicode CMap.
   Already done - `fonts/` holds the result, so you only re-run this if the
   fonts are lost or the resume switches typeface.
2. **`build_pdf_html.py`** runs `textutil` to convert the .docx to HTML, which
   preserves its real paragraph and run formatting. textutil writes Word points
   as `px`, so those get re-united to `pt`. It then restores what textutil
   drops: the section heading rules, the right-aligned date tab stop, Word's
   list indents, and the hyperlinks. Values like the 451.3pt tab stop and the
   0.75pt rule are read out of the docx's own `word/document.xml`.
3. **Headless Chrome** prints that HTML to a Letter PDF with 0.75in margins.
4. **`compare.py`** diffs every text line's position and width against the
   previous PDF.

## Known difference

The PDF font subsets contain the `ft`/`fi` ligature glyphs but no standalone
bold `f` (LibreOffice only ever drew it inside a ligature). Bold words like
"Swift" therefore render unligated, with the `f` coming from Helvetica-Bold.
It is invisible at reading size but it is a real difference. Installing the
full Carlito font would remove it.

## A caution about the .docx

The `.docx` is the source of truth and is easy to damage. A `textutil`-produced
.docx is **not** equivalent to the original: it drops `styles.xml` and
`numbering.xml`, which turns real lists into paragraphs with literal bullets.
If the file ever shrinks to ~8 entries, it has been clobbered:

```bash
unzip -l documents/aziz-bibitow-resume.docx | tail -2
```

A healthy file has ~22 entries including `word/styles.xml` and
`word/numbering.xml`.
