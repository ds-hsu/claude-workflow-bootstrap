#!/usr/bin/env python
"""
Render PDF pages to PNG for Claude vision processing.

Usage:
    python render-pdf.py <input.pdf> <output_dir> [dpi]

Default DPI: 200 (good balance for vision reading)
"""
import sys
import os
import pymupdf


def render(input_pdf: str, output_dir: str, dpi: int = 200) -> list[str]:
    """Render each page of the PDF as a PNG file."""
    os.makedirs(output_dir, exist_ok=True)
    doc = pymupdf.open(input_pdf)
    out_paths = []
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=dpi)
        path = os.path.join(output_dir, f"page-{i:02d}.png")
        pix.save(path)
        out_paths.append(path)
        print(f"  page {i}: {pix.width}x{pix.height} -> {path}")
    return out_paths


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.pdf> <output_dir> [dpi]")
        sys.exit(1)
    input_pdf = sys.argv[1]
    output_dir = sys.argv[2]
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    paths = render(input_pdf, output_dir, dpi)
    print(f"Rendered {len(paths)} pages to {output_dir}")
