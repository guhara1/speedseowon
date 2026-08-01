#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""사이트 이미지 슬롯을 생성합니다.

이 스크립트는 두 가지 일을 합니다.
  1) 실제 사진(raw/)이 있으면  → 리사이즈 + WebP 30KB 이하로 압축해 배치
  2) 없으면                    → 같은 파일명·같은 비율의 브랜드 플레이트를 생성

즉 tools/import-drive-photos.sh 로 원본을 raw/ 에 내려받은 뒤 이 스크립트를
다시 돌리면, HTML 수정 없이 실제 현장 사진으로 전부 교체됩니다.

    python3 tools/make_images.py            # raw/ 있으면 사진, 없으면 플레이트
    python3 tools/make_images.py --force-plate
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "img")
RAW = os.path.join(ROOT, "tools", "raw")
TARGET_KB = 30

INK, INK2, CYAN, AMBER, MIST = (10, 25, 41), (23, 51, 76), (0, 168, 200), (255, 176, 31), (185, 203, 219)

# (파일명, 폭, 높이, 라벨, 아이콘)
SLOTS = [
    ("field-endoscope-inspection.webp", 880, 660, "ENDOSCOPE", "scope"),
    ("hydro-jetting-sewer-line.webp", 640, 480, "HYDRO JET", "jet"),
    ("leak-detection-thermal.webp", 640, 480, "THERMAL", "thermal"),
    ("old-galvanized-pipe-replace.webp", 640, 480, "REPIPE", "pipe"),
    ("toilet-clog-removal.webp", 640, 480, "TOILET", "toilet"),
    ("kitchen-drain-grease.webp", 640, 480, "GREASE", "jet"),
    ("seo-wonbae-portrait.webp", 400, 400, "FIELD LEAD", "person"),
    ("og-speedseowon-1200x630.webp", 1200, 630, "SPEEDSEOWON", "scope"),
]


def _font(size, bold=False):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
              "/usr/share/fonts/truetype/liberation/LiberationSans%s.ttf" % ("-Bold" if bold else "")):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _gradient(w, h):
    """대각 그라데이션 + 시안 글로우."""
    base = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(base)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line([(0, y), (w, y)], fill=tuple(
            int(INK[i] + (INK2[i] - INK[i]) * t) for i in range(3)))
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    r = int(max(w, h) * .62)
    gd.ellipse([w - r, -r // 2, w + r // 2, r], fill=(0, 62, 76))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(w, h) // 7))
    return Image.blend(base, Image.blend(base, glow, .55), .8)


def _grid(img, step=44):
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, img.width, step):
        d.line([(x, 0), (x, img.height)], fill=(255, 255, 255, 12), width=1)
    for y in range(0, img.height, step):
        d.line([(0, y), (img.width, y)], fill=(255, 255, 255, 12), width=1)


def _icon(d, kind, cx, cy, s):
    """장비 라인아트. 두께 있는 선으로 도면 느낌을 냅니다."""
    lw = max(3, s // 22)
    c, a = CYAN, AMBER
    if kind == "scope":
        d.arc([cx - s, cy - s, cx + s, cy + s], 200, 340, fill=c, width=lw)
        d.line([(cx - s * .72, cy + s * .34), (cx - s * .72, cy + s * .9)], fill=c, width=lw)
        d.line([(cx + s * .72, cy + s * .34), (cx + s * .72, cy + s * .9)], fill=c, width=lw)
        d.ellipse([cx - s * .3, cy - s * .3, cx + s * .3, cy + s * .3], outline=a, width=lw)
        d.ellipse([cx - s * .1, cy - s * .1, cx + s * .1, cy + s * .1], fill=a)
    elif kind == "jet":
        d.rounded_rectangle([cx - s, cy - s * .42, cx + s * .1, cy + s * .42],
                            radius=s // 8, outline=c, width=lw)
        for i in range(4):
            y = cy - s * .3 + i * s * .2
            d.line([(cx + s * .2, y), (cx + s * (.55 + .12 * (i % 2)), y)], fill=a, width=lw)
        d.line([(cx + s * .75, cy), (cx + s, cy)], fill=a, width=lw)
    elif kind == "thermal":
        for i, col in enumerate((a, c, MIST)):
            rr = s * (1 - i * .3)
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=col, width=lw)
        d.line([(cx, cy - s * 1.25), (cx, cy - s * 1.05)], fill=a, width=lw)
    elif kind == "pipe":
        d.rounded_rectangle([cx - s, cy - s * .34, cx + s, cy + s * .34],
                            radius=s // 9, outline=c, width=lw)
        for x in (cx - s * .42, cx + s * .42):
            d.line([(x, cy - s * .34), (x, cy + s * .34)], fill=c, width=lw)
        d.line([(cx - s * .18, cy - s * .78), (cx + s * .18, cy - s * .42)], fill=a, width=lw)
    elif kind == "toilet":
        d.rounded_rectangle([cx - s * .78, cy - s, cx + s * .1, cy - s * .34],
                            radius=s // 10, outline=c, width=lw)
        d.ellipse([cx - s * .82, cy - s * .2, cx + s * .55, cy + s * .82], outline=c, width=lw)
        d.ellipse([cx - s * .5, cy + s * .12, cx + s * .22, cy + s * .5], outline=a, width=lw)
    elif kind == "person":
        d.ellipse([cx - s * .38, cy - s * .92, cx + s * .38, cy - s * .16], outline=c, width=lw)
        d.arc([cx - s * .86, cy - s * .1, cx + s * .86, cy + s * 1.3], 180, 360, fill=c, width=lw)
        d.line([(cx - s * .3, cy + s * .62), (cx + s * .3, cy + s * .62)], fill=a, width=lw)


def make_plate(name, w, h, label, kind):
    img = _gradient(w, h)
    _grid(img, step=max(28, w // 22))
    d = ImageDraw.Draw(img, "RGBA")

    s = int(min(w, h) * .17)
    _icon(d, kind, w // 2, int(h * .43), s)

    f_lab = _font(max(11, w // 62), bold=True)
    f_sub = _font(max(10, w // 78))
    tw = d.textlength(label, font=f_lab)
    bx, by = (w - tw) / 2 - 12, h * .43 + s * 1.5
    d.rounded_rectangle([bx, by, bx + tw + 24, by + f_lab.size + 14], radius=5, fill=AMBER)
    d.text((bx + 12, by + 6), label, font=f_lab, fill=INK)

    sub = "SPEEDSEOWON  ·  FIELD RECORD"
    d.text(((w - d.textlength(sub, font=f_sub)) / 2, by + f_lab.size + 26),
           sub, font=f_sub, fill=MIST)

    # 모서리 크롭 마크
    m, ln = int(min(w, h) * .045), int(min(w, h) * .07)
    for (x, y, dx, dy) in ((m, m, 1, 1), (w - m, m, -1, 1), (m, h - m, 1, -1), (w - m, h - m, -1, -1)):
        d.line([(x, y), (x + dx * ln, y)], fill=(255, 255, 255, 70), width=2)
        d.line([(x, y), (x, y + dy * ln)], fill=(255, 255, 255, 70), width=2)
    return img


def from_photo(path, w, h):
    """원본 사진을 슬롯 비율에 맞춰 중앙 크롭 후 리사이즈."""
    im = Image.open(path)
    im = im.convert("RGB")
    try:  # EXIF 회전 반영
        from PIL import ImageOps
        im = ImageOps.exif_transpose(im)
    except Exception:
        pass
    tr, sr = w / h, im.width / im.height
    if sr > tr:
        nw = int(im.height * tr)
        im = im.crop(((im.width - nw) // 2, 0, (im.width + nw) // 2, im.height))
    else:
        nh = int(im.width / tr)
        im = im.crop((0, (im.height - nh) // 2, im.width, (im.height + nh) // 2))
    return im.resize((w, h), Image.LANCZOS)


def save_webp(img, path, target_kb=TARGET_KB):
    """30KB 이하가 될 때까지 품질을 낮추고, 안 되면 살짝 샤프닝 후 재시도."""
    for q in range(88, 24, -4):
        img.save(path, "WEBP", quality=q, method=6)
        if os.path.getsize(path) <= target_kb * 1024:
            return q, os.path.getsize(path)
    soft = img.filter(ImageFilter.GaussianBlur(.4))
    for q in range(50, 14, -4):
        soft.save(path, "WEBP", quality=q, method=6)
        if os.path.getsize(path) <= target_kb * 1024:
            return q, os.path.getsize(path)
    return q, os.path.getsize(path)


def main():
    force_plate = "--force-plate" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    photos = []
    if os.path.isdir(RAW) and not force_plate:
        photos = sorted(f for f in os.listdir(RAW)
                        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))

    print(f"원본 사진 {len(photos)}장 · 슬롯 {len(SLOTS)}개\n")
    for i, (name, w, h, label, kind) in enumerate(SLOTS):
        dst = os.path.join(OUT, name)
        if photos:
            src = os.path.join(RAW, photos[i % len(photos)])
            img, src_label = from_photo(src, w, h), photos[i % len(photos)]
        else:
            img, src_label = make_plate(name, w, h, label, kind), "브랜드 플레이트"
        q, size = save_webp(img, dst)
        flag = "OK " if size <= TARGET_KB * 1024 else "초과"
        print(f"  {flag} {name:<38} {w}x{h}  {size/1024:5.1f}KB  q{q}  ← {src_label}")


if __name__ == "__main__":
    main()
