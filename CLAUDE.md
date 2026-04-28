# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a static single-page portfolio website for Aziz Bibitov (iOS developer), deployed via GitHub Pages at `azizbibitov.github.io`. There is no build step - editing files and pushing to `main` is all it takes to publish.

## Development

Open `index.html` directly in a browser to preview, or use any static file server:

```bash
python3 -m http.server 8080
```

No package manager, no bundler, no build process.

## Architecture

All content lives in a single file: `index.html`. The page is structured as full-page scrollable sections with a fixed sidebar nav:

- `#header` - hero with typed.js cycling text (configured via `.typed-text` content, comma-separated values)
- `#about` - bio, skill progress bars (animated via Waypoints when scrolled into view)
- `#education`, `#experience` - timeline cards
- `#service` - service offerings
- `#portfolio` - filterable image grid using Isotope, with Lightbox for full-size previews; each item carries a `data-filter` attribute matching the filter buttons in `#portfolio-flters`
- `#review` - testimonial slider via Slick
- `#contact` - contact form and info

**Supporting files:**
- `css/style.css` - all custom styles
- `js/main.js` - initializes all JS plugins (Typed, Isotope, Slick, Waypoints, smooth scroll, back-to-top)
- `lib/` - vendored JS libraries: easing, isotope, lightbox, slick, typed, waypoints
- `img/` - portfolio images follow the naming pattern `portfolio-N.jpg` (thumbnail) and `portfolio-N-2.jpg` (lightbox full-size)
- `documents/` - PDFs linked from the page (resume, per-project descriptions)

**CDN dependencies** (loaded in `<head>`): Bootstrap 4.4.1, Font Awesome 5.10, Google Fonts (Open Sans).

## Common edits

- **Typed hero text**: change the comma-separated string inside `<div class="typed-text">` in `#header`
- **Adding a portfolio item**: copy an existing `.portfolio-item` block, update `data-filter`, image `src` attributes, and the lightbox `href`
- **Skill bars**: set `aria-valuenow` on `.progress-bar` to the desired percentage (0-100)
- **Resume PDF**: replace `documents/aziz-bibitow-resume.pdf` and keep the filename the same, or update the `href` in the large-btn section
