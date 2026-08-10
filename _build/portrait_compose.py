"""Shared brand-stamp + copyright-caption compositing for portraits2 artwork.

Used by both the Facebook/Instagram poster (_build/fb/image_compose.py,
full-res PNG output) and the website's lightweight JPEG generator
(_build/generate_web_portraits.py, small resized output), so the visual
treatment (stamp size/position, caption text/style) can't drift between the
two — only the resolution and output format differ per caller.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
BRAND_STAMP = REPO_ROOT / "images" / "logo" / "brand-stamp.png"

COPYRIGHT_TEXT = "AI-generated image — no copyright claimed"
COPYRIGHT_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def add_brand_stamp(portrait: Image.Image, stamp_path: Path = BRAND_STAMP) -> Image.Image:
    """Composite the reusable brand stamp subtly in the top-right corner.

    portrait must be RGBA. Returns a new RGBA image.
    """
    width, _height = portrait.size
    stamp = Image.open(stamp_path).convert("RGBA")
    stamp_width = round(width * 0.36)
    stamp_height = round(stamp.height * stamp_width / stamp.width)
    stamp = stamp.resize((stamp_width, stamp_height), Image.Resampling.LANCZOS)
    margin = round(width * 0.03)
    portrait = portrait.copy()
    portrait.alpha_composite(stamp, (width - stamp_width - margin, margin))
    return portrait


def add_copyright_caption(
    portrait: Image.Image, text: str = COPYRIGHT_TEXT, font_path: str = COPYRIGHT_FONT
) -> Image.Image:
    """Composite a small, low-contrast copyright line across the bottom edge.

    portrait must be RGBA. Returns a new RGBA image.
    """
    width, height = portrait.size
    font_size = max(round(height * 0.018), 12)
    font = ImageFont.truetype(font_path, font_size)

    draw = ImageDraw.Draw(portrait)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pad_y = round(font_size * 0.5)
    bottom_margin = round(height * 0.02)

    rect_top = height - bottom_margin - text_h - pad_y - bbox[1]
    rect_bottom = height - bottom_margin + pad_y - bbox[1]
    overlay = Image.new("RGBA", portrait.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle(
        [0, rect_top, width, rect_bottom], fill=(0, 0, 0, 50)
    )
    portrait = Image.alpha_composite(portrait, overlay)

    x = (width - text_w) // 2 - bbox[0]
    y = height - bottom_margin - text_h - bbox[1]
    ImageDraw.Draw(portrait).text(
        (x, y), text, font=font, fill=(200, 200, 200, 100)
    )
    return portrait


def compose_branding(portrait: Image.Image) -> Image.Image:
    """Apply both the brand stamp and the copyright caption. portrait must be RGBA."""
    portrait = add_brand_stamp(portrait)
    portrait = add_copyright_caption(portrait)
    return portrait
