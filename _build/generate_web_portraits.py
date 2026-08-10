#!/usr/bin/env python3
"""Generate lightweight, web-ready JPEGs from the full-resolution portraits2 art.

images/portraits2/*.png are 1024x1024 lossless RGBA PNGs (~2MB each,
~550MB total) generated for print/archival quality. Nothing inline on the
site displays a portrait larger than 140px (see css/style.css), so serving
these directly wastes ~1600x the pixels actually shown. This script resizes
each one down, burns in the copyright caption (via _build/portrait_compose.py,
shared with the Facebook/Instagram poster so the caption treatment can't
drift between the two — the brand stamp that pipeline also adds is
deliberately skipped here, website images carry the caption only), and
re-encodes as JPEG into images/portraits2-web/ — leaving the originals in
images/portraits2/ untouched for other uses.

Two sizes are generated per person:
- <id>.jpg (500x500, ~90KB): the inline thumbnail used everywhere on the
  site (person header, home spotlight, explore cards) — ~3.5x the biggest
  inline display size (140px), enough headroom for retina.
- <id>-full.jpg (1024x1024, matching the source's native resolution — no
  point upscaling past it): only linked from a person's own detail page,
  where clicking the portrait opens this larger captioned version.

Re-run whenever images/portraits2/ gains new portraits (see
images/portraits2/STAINED_GLASS_QUEUE.md) before rebuilding the static site.
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from portrait_compose import add_copyright_caption  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "images" / "portraits2"
OUTPUT_DIR = ROOT / "images" / "portraits2-web"

THUMB_SIZE = 500
THUMB_QUALITY = 82
FULL_SIZE = 1024
FULL_QUALITY = 85


def _captioned_jpeg(source: Image.Image, size: int) -> Image.Image:
    portrait = source.resize((size, size), Image.Resampling.LANCZOS)
    portrait = add_copyright_caption(portrait)
    return portrait.convert("RGB")


def generate_web_portrait(source_path: Path) -> tuple[Path, Path]:
    source = Image.open(source_path).convert("RGBA")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    thumb_path = OUTPUT_DIR / f"{source_path.stem}.jpg"
    _captioned_jpeg(source, THUMB_SIZE).save(
        thumb_path, "JPEG", quality=THUMB_QUALITY, optimize=True
    )

    full_path = OUTPUT_DIR / f"{source_path.stem}-full.jpg"
    _captioned_jpeg(source, FULL_SIZE).save(
        full_path, "JPEG", quality=FULL_QUALITY, optimize=True
    )

    return thumb_path, full_path


def main():
    sources = sorted(SOURCE_DIR.glob("*.png"))
    if not sources:
        print(f"No PNGs found in {SOURCE_DIR}")
        return

    total_in = total_out = 0
    for source_path in sources:
        thumb_path, full_path = generate_web_portrait(source_path)
        in_size = source_path.stat().st_size
        out_size = thumb_path.stat().st_size + full_path.stat().st_size
        total_in += in_size
        total_out += out_size
        print(
            f"{source_path.name}: {in_size / 1024:.0f}KB -> "
            f"{thumb_path.name}: {thumb_path.stat().st_size / 1024:.0f}KB + "
            f"{full_path.name}: {full_path.stat().st_size / 1024:.0f}KB"
        )

    print(
        f"\n{len(sources)} images: {total_in / 1024 / 1024:.1f}MB -> "
        f"{total_out / 1024 / 1024:.1f}MB "
        f"({100 * (1 - total_out / total_in):.0f}% smaller)"
    )


if __name__ == "__main__":
    main()
