#!/usr/bin/env python3
"""Draw furniture at true scale on a photo of a room wall.

Given the pixel positions of a wall's four corners and the wall's real size,
this computes a perspective mapping (homography) from the wall plane in
centimetres to image pixels, then draws each requested item as a translucent,
labelled box. The result is a "placement guide" image that can be handed to an
image-editing model together with the original photo, so the model knows
exactly where and how big each new piece should be.

Usage:
  python scale_overlay.py --image living.jpg \
      --corners "112,80 1460,64 1478,905 98,930" \
      --wall-width 420 --wall-height 260 \
      --item "A:sofa:60:230:85" --item "B:lamp:310:40:160" \
      --out guide.png

  --corners  top-left, top-right, bottom-right, bottom-left of the wall, in
             pixels (x,y). "Bottom" is where the wall meets the floor.
  --item     LABEL:NAME:OFFSET_CM:WIDTH_CM:HEIGHT_CM[:ELEVATION_CM]
             OFFSET is the distance from the wall's left edge to the item's
             left edge. ELEVATION lifts the item off the floor (shelves, art,
             TV). Use a short ASCII label (A, B, 1...) for the drawing; NAME
             goes into the printed legend only.

Prints a JSON summary (pixel boxes, share of wall width, warnings) to stdout.
"""
import argparse
import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

COLORS = [
    (230, 57, 70), (29, 114, 243), (42, 157, 92), (244, 162, 97),
    (131, 56, 236), (0, 150, 160), (200, 120, 0), (90, 90, 90),
]


def homography(src, dst):
    """Solve the 3x3 matrix H mapping src points to dst points (4 pairs)."""
    rows = []
    for (x, y), (u, v) in zip(src, dst):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    _, _, vt = np.linalg.svd(np.asarray(rows, dtype=float))
    h = vt[-1].reshape(3, 3)
    return h / h[2, 2]


def project(h, x, y):
    p = h @ np.array([x, y, 1.0])
    return float(p[0] / p[2]), float(p[1] / p[2])


def parse_corners(text):
    pts = [tuple(float(v) for v in p.split(",")) for p in text.split()]
    if len(pts) != 4 or any(len(p) != 2 for p in pts):
        sys.exit("--corners needs exactly four x,y pairs")
    return pts


def parse_item(text):
    parts = text.split(":")
    if len(parts) not in (5, 6):
        sys.exit(f"bad --item '{text}', expected LABEL:NAME:OFFSET:WIDTH:HEIGHT[:ELEVATION]")
    label, name = parts[0], parts[1]
    nums = [float(v) for v in parts[2:]]
    offset, width, height = nums[:3]
    elevation = nums[3] if len(nums) == 4 else 0.0
    return {"label": label, "name": name, "offset_cm": offset, "width_cm": width,
            "height_cm": height, "elevation_cm": elevation}


def load_font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/Library/Fonts/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--image", required=True)
    ap.add_argument("--corners", required=True)
    ap.add_argument("--wall-width", type=float, required=True, help="cm")
    ap.add_argument("--wall-height", type=float, required=True, help="cm, floor to ceiling")
    ap.add_argument("--item", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-grid", action="store_true", help="skip the 50 cm reference grid")
    args = ap.parse_args()

    img = Image.open(args.image).convert("RGBA")
    W, H = args.wall_width, args.wall_height
    tl, tr, br, bl = parse_corners(args.corners)
    # Wall plane: x to the right from the left edge, y up from the floor.
    h = homography([(0, H), (W, H), (W, 0), (0, 0)], [tl, tr, br, bl])

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(max(14, img.width // 45))
    small = load_font(max(11, img.width // 70))

    if not args.no_grid:
        step = 50
        for x in np.arange(0, W + 0.1, step):
            draw.line([project(h, x, 0), project(h, x, H)], fill=(255, 255, 255, 70), width=1)
        for y in np.arange(0, H + 0.1, step):
            draw.line([project(h, 0, y), project(h, W, y)], fill=(255, 255, 255, 70), width=1)
    draw.line([tl, tr, br, bl, tl], fill=(255, 255, 0, 200), width=3)

    summary = {"wall_cm": [W, H], "items": [], "warnings": []}
    for i, raw in enumerate(args.item):
        it = parse_item(raw)
        x0, x1 = it["offset_cm"], it["offset_cm"] + it["width_cm"]
        y0, y1 = it["elevation_cm"], it["elevation_cm"] + it["height_cm"]
        if x0 < 0 or x1 > W:
            summary["warnings"].append(f"{it['label']} ({it['name']}) runs past the wall edge: {x0:.0f}-{x1:.0f} cm on a {W:.0f} cm wall")
        if y1 > H:
            summary["warnings"].append(f"{it['label']} ({it['name']}) is taller than the ceiling: top at {y1:.0f} cm")
        for other in summary["items"]:
            ox0, ox1 = other["offset_cm"], other["offset_cm"] + other["width_cm"]
            oy0, oy1 = other["elevation_cm"], other["elevation_cm"] + other["height_cm"]
            if x0 < ox1 and ox0 < x1 and y0 < oy1 and oy0 < y1:
                summary["warnings"].append(f"{it['label']} overlaps {other['label']} on the wall plane")

        poly = [project(h, x0, y0), project(h, x1, y0), project(h, x1, y1), project(h, x0, y1)]
        color = COLORS[i % len(COLORS)]
        draw.polygon(poly, fill=color + (90,), outline=color + (255,))
        draw.line(poly + [poly[0]], fill=color + (255,), width=4)
        cx = sum(p[0] for p in poly) / 4
        cy = sum(p[1] for p in poly) / 4
        text = it["label"]
        dims = f"{it['width_cm']:.0f}x{it['height_cm']:.0f}"
        for t, f, dy in ((text, font, -font.size * 0.6), (dims, small, font.size * 0.5)):
            bbox = draw.textbbox((0, 0), t, font=f)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            pos = (cx - tw / 2, cy + dy - th / 2)
            draw.rectangle([pos[0] - 4, pos[1] - 3, pos[0] + tw + 4, pos[1] + th + 6], fill=(0, 0, 0, 160))
            draw.text(pos, t, font=f, fill=(255, 255, 255, 255))

        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        summary["items"].append({
            **it,
            "share_of_wall_width": round(it["width_cm"] / W, 3),
            "pixel_bbox": [round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))],
            "pixel_polygon": [[round(x), round(y)] for x, y in poly],
        })

    out = Image.alpha_composite(img, overlay).convert("RGB")
    out.save(args.out)
    summary["image_size"] = list(img.size)
    summary["out"] = args.out
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
