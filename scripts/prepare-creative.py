#!/usr/bin/env python3
"""
Resize and compress an image to Meta ad specs, ready to publish on
ads.vas-reversal.ca.

    python3 scripts/prepare-creative.py <source> <name> [--ratio 4x5] [--month 2026-07]

Writes assets/<month>/<name>-<ratio>.jpg at the right pixel size, then you run
`npx wrangler deploy`.

Crops to fill rather than squashing, so composition is preserved and nothing
is distorted. Deliberately does not upscale beyond the target.
"""

import argparse
import sys
from datetime import date
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required:  pip3 install --break-system-packages Pillow")

RATIOS = {
    "4x5": (1080, 1350),    # Instagram / Facebook feed, portrait
    "9x16": (1080, 1920),   # Story and Reels
    "1x1": (1080, 1080),    # Square
}

ROOT = Path(__file__).resolve().parent.parent


def prepare(source: Path, name: str, ratio: str, month: str, quality: int) -> Path:
    target_w, target_h = RATIOS[ratio]
    im = Image.open(source).convert("RGB")

    # Crop to the target aspect ratio from the centre, then scale once.
    src_ratio = im.width / im.height
    dst_ratio = target_w / target_h
    if src_ratio > dst_ratio:
        new_w = round(im.height * dst_ratio)
        left = (im.width - new_w) // 2
        im = im.crop((left, 0, left + new_w, im.height))
    elif src_ratio < dst_ratio:
        new_h = round(im.width / dst_ratio)
        top = (im.height - new_h) // 2
        im = im.crop((0, top, im.width, top + new_h))

    im = im.resize((target_w, target_h), Image.LANCZOS)

    out_dir = ROOT / "assets" / month
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{name}-{ratio}.jpg"
    im.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", type=Path, help="source image")
    p.add_argument("name", help="slug, e.g. worth-exploring")
    p.add_argument("--ratio", choices=sorted(RATIOS), default="4x5")
    p.add_argument("--month", default=date.today().strftime("%Y-%m"))
    p.add_argument("--quality", type=int, default=88)
    args = p.parse_args()

    if not args.source.exists():
        sys.exit(f"No such file: {args.source}")

    out = prepare(args.source, args.name, args.ratio, args.month, args.quality)
    kb = out.stat().st_size / 1024
    rel = out.relative_to(ROOT)
    print(f"{rel}  {RATIOS[args.ratio][0]}x{RATIOS[args.ratio][1]}  {kb:.0f} KB")
    print(f"\nNext:  npx wrangler deploy")
    print(f"Then:  https://ads.vas-reversal.ca/{args.month}/{out.name}")


if __name__ == "__main__":
    main()
