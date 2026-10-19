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
  --item     LABEL:NAME:OFFSET_CM:WIDTH_CM:HEIGHT_CM[:ELEVATION_CM[:DEPTH_CM]]
             OFFSET is the distance from the wall's left edge to the item's
             left edge. ELEVATION lifts the item off the floor (shelves, art,
             TV). Use a short ASCII label (A, B, 1...) for the drawing; NAME
             goes into the printed legend only.

Depth (optional). To draw items as boxes that stick out from the wall, give
the direction "straight out of the wall" and one known distance along it:
  --depth-lines "x,y x,y x,y x,y"  two image segments that run perpendicular
             to the wall in reality (e.g. a side wall's floor line and ceiling
             line, or floor-tile grout lines); their crossing is the vanishing
             point of the depth direction.
  --depth-ref "x,y x,y CM"  a point on the wall's floor line (usually the
             inner corner) and the image of the point CM straight out from it
             (e.g. the front end of a side wall whose length is known).
Then give DEPTH_CM on each item.

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
    if len(parts) not in (5, 6, 7):
        sys.exit(f"bad --item '{text}', expected LABEL:NAME:OFFSET:WIDTH:HEIGHT[:ELEVATION[:DEPTH]]")
    label, name = parts[0], parts[1]
    nums = [float(v) for v in parts[2:]]
    offset, width, height = nums[:3]
    elevation = nums[3] if len(nums) >= 4 else 0.0
    depth = nums[4] if len(nums) == 5 else 0.0
    return {"label": label, "name": name, "offset_cm": offset, "width_cm": width,
            "height_cm": height, "elevation_cm": elevation, "depth_cm": depth}


def line_through(p, q):
    return np.cross([p[0], p[1], 1.0], [q[0], q[1], 1.0])


def depth_mapper(h, lines_text, ref_text):
    """Return f(wall_x, wall_y, depth_cm) -> pixel for points in front of the wall.

    Planes parallel to the wall, shifted by d along the depth direction, map to
    the wall's image by the homology I + d*beta*v*l^T, where v is the depth
    vanishing point and l the wall's vanishing line. beta comes from --depth-ref.
    """
    pts = parse_corners(lines_text)
    v = np.cross(line_through(pts[0], pts[1]), line_through(pts[2], pts[3]))
    if abs(v[2]) < 1e-9:
        sys.exit("--depth-lines are parallel in the image; pick lines that converge")
    v = v / v[2]
    l = np.cross(h[:, 0], h[:, 1])  # wall's vanishing line: through its x and y vanishing points
    parts = ref_text.split()
    if len(parts) != 3:
        sys.exit("--depth-ref needs 'x,y x,y CM'")
    (x0, y0), (x1, y1) = (tuple(float(c) for c in p.split(",")) for p in parts[:2])
    dist = float(parts[2])
    # x1 = (x0 + t*v) / (1 + t); solve t on the better-conditioned axis
    tx = (x1 - x0) / (v[0] - x1) if abs(v[0] - x1) > 1e-6 else None
    ty = (y1 - y0) / (v[1] - y1) if abs(v[1] - y1) > 1e-6 else None
    t = tx if ty is None or (tx is not None and abs(v[0] - x1) > abs(v[1] - y1)) else ty
    beta = t / (dist * float(l @ np.array([x0, y0, 1.0])))

    def f(wx, wy, d):
        p = h @ np.array([wx, wy, 1.0])
        q = p + d * beta * v * float(l @ p)
        return float(q[0] / q[2]), float(q[1] / q[2])
    return f, (float(v[0]), float(v[1]))


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
    ap.add_argument("--depth-lines", help="two image segments running straight out of the wall")
    ap.add_argument("--depth-ref", help="'x,y x,y CM': wall floor point and its image CM out from the wall")
    ap.add_argument("--no-grid", action="store_true", help="skip the 50 cm reference grid")
    args = ap.parse_args()

    img = Image.open(args.image).convert("RGBA")
    W, H = args.wall_width, args.wall_height
    tl, tr, br, bl = parse_corners(args.corners)
    # Wall plane: x to the right from the left edge, y up from the floor.
    h = homography([(0, H), (W, H), (W, 0), (0, 0)], [tl, tr, br, bl])

    depth_at = None
    if args.depth_lines or args.depth_ref:
        if not (args.depth_lines and args.depth_ref):
            sys.exit("--depth-lines and --depth-ref go together")
        depth_at, vp = depth_mapper(h, args.depth_lines, args.depth_ref)

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
        d = it["depth_cm"]
        if d and depth_at is None:
            summary["warnings"].append(f"{it['label']} has a depth but no --depth-lines/--depth-ref; drawn flat on the wall")
        if d and depth_at is not None:
            back = poly
            front = [depth_at(x0, y0, d), depth_at(x1, y0, d), depth_at(x1, y1, d), depth_at(x0, y1, d)]
            faces = [
                [back[0], back[1], front[1], front[0]],  # bottom (floor footprint)
                [back[3], back[2], front[2], front[3]],  # top
                [back[0], back[3], front[3], front[0]],  # left side
                [back[1], back[2], front[2], front[1]],  # right side
            ]
            for face in faces:
                draw.polygon(face, fill=color + (45,))
                draw.line(face + [face[0]], fill=color + (200,), width=2)
            poly = front
            draw.polygon(poly, fill=color + (80,))
        else:
            draw.polygon(poly, fill=color + (90,), outline=color + (255,))
        draw.line(poly + [poly[0]], fill=color + (255,), width=4)
        cx = sum(p[0] for p in poly) / 4
        cy = sum(p[1] for p in poly) / 4
        text = it["label"]
        dims = f"{it['width_cm']:.0f}x{it['height_cm']:.0f}" + (f"x{it['depth_cm']:.0f}" if it["depth_cm"] else "")
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
    if depth_at is not None:
        summary["depth_vanishing_point"] = [round(c) for c in vp]
    summary["image_size"] = list(img.size)
    summary["out"] = args.out
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
