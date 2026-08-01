#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""고객 제공 현장사진 → 사이트 이미지 슬롯.

  1) tools/raw/ 에 원본이 있으면  → 슬롯 비율로 크롭 + WebP 30KB 이하로 압축해 배치
  2) 없으면                       → 같은 파일명·비율의 브랜드 플레이트를 생성

슬롯은 config.py 의 IMAGES 에서 읽습니다. 원본 21장 ↔ 슬롯 21개가 1:1로 맞습니다.
원본이 더 적으면 순환 배치하고, 더 많으면 파일명 순으로 앞에서부터 씁니다.

    python3 tools/make_images.py
    python3 tools/make_images.py --force-plate
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_build", "site"))
from config import IMAGES  # noqa: E402

OUT = os.path.join(ROOT, "img")
RAW = os.path.join(ROOT, "tools", "raw")
TARGET_KB = 30

INK, INK2 = (10, 25, 41), (23, 51, 76)
CYAN, AMBER, MIST = (0, 168, 200), (255, 176, 31), (185, 203, 219)

# 슬롯 순서 = 사진이 배치되는 순서. 원본 파일명 정렬 순과 1:1로 대응합니다.
SLOT_ORDER = (["hero1", "hero2", "hero3", "hero4"]
              + [f"work{i:02d}" for i in range(1, 13)]
              + ["case1", "case2", "case3", "author", "og"])

PLATE_ICON = {"hero1": "scope", "hero2": "jet", "hero3": "pipe", "hero4": "thermal",
              "case1": "jet", "case2": "thermal", "case3": "jet",
              "author": "person", "og": "scope"}


def _font(size, bold=False):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
              "/usr/share/fonts/truetype/liberation/LiberationSans%s.ttf" % ("-Bold" if bold else "")):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _gradient(w, h):
    base = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(base)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line([(0, y), (w, y)], fill=tuple(int(INK[i] + (INK2[i] - INK[i]) * t) for i in range(3)))
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    r = int(max(w, h) * .62)
    gd.ellipse([w - r, -r // 2, w + r // 2, r], fill=(0, 62, 76))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(w, h) // 7))
    return Image.blend(base, Image.blend(base, glow, .55), .8)


def _icon(d, kind, cx, cy, s):
    lw = max(3, s // 22)
    c, a = CYAN, AMBER
    if kind == "scope":
        d.arc([cx - s, cy - s, cx + s, cy + s], 200, 340, fill=c, width=lw)
        d.line([(cx - s * .72, cy + s * .34), (cx - s * .72, cy + s * .9)], fill=c, width=lw)
        d.line([(cx + s * .72, cy + s * .34), (cx + s * .72, cy + s * .9)], fill=c, width=lw)
        d.ellipse([cx - s * .3, cy - s * .3, cx + s * .3, cy + s * .3], outline=a, width=lw)
        d.ellipse([cx - s * .1, cy - s * .1, cx + s * .1, cy + s * .1], fill=a)
    elif kind == "jet":
        d.rounded_rectangle([cx - s, cy - s * .42, cx + s * .1, cy + s * .42], radius=s // 8,
                            outline=c, width=lw)
        for i in range(4):
            y = cy - s * .3 + i * s * .2
            d.line([(cx + s * .2, y), (cx + s * (.55 + .12 * (i % 2)), y)], fill=a, width=lw)
    elif kind == "thermal":
        for i, col in enumerate((a, c, MIST)):
            rr = s * (1 - i * .3)
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=col, width=lw)
    elif kind == "pipe":
        d.rounded_rectangle([cx - s, cy - s * .34, cx + s, cy + s * .34], radius=s // 9,
                            outline=c, width=lw)
        for x in (cx - s * .42, cx + s * .42):
            d.line([(x, cy - s * .34), (x, cy + s * .34)], fill=c, width=lw)
    elif kind == "person":
        d.ellipse([cx - s * .38, cy - s * .92, cx + s * .38, cy - s * .16], outline=c, width=lw)
        d.arc([cx - s * .86, cy - s * .1, cx + s * .86, cy + s * 1.3], 180, 360, fill=c, width=lw)


def make_plate(w, h, label, kind):
    img = _gradient(w, h)
    d = ImageDraw.Draw(img, "RGBA")
    step = max(28, w // 22)
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=(255, 255, 255, 12))
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=(255, 255, 255, 12))

    s = int(min(w, h) * .17)
    _icon(d, kind, w // 2, int(h * .43), s)

    f_lab, f_sub = _font(max(11, w // 62), True), _font(max(10, w // 78))
    tw = d.textlength(label, font=f_lab)
    bx, by = (w - tw) / 2 - 12, h * .43 + s * 1.5
    d.rounded_rectangle([bx, by, bx + tw + 24, by + f_lab.size + 14], radius=5, fill=AMBER)
    d.text((bx + 12, by + 6), label, font=f_lab, fill=INK)
    sub = "SPEEDSEOWON  ·  FIELD RECORD"
    d.text(((w - d.textlength(sub, font=f_sub)) / 2, by + f_lab.size + 26), sub, font=f_sub, fill=MIST)

    m, ln = int(min(w, h) * .045), int(min(w, h) * .07)
    for (x, y, dx, dy) in ((m, m, 1, 1), (w - m, m, -1, 1), (m, h - m, 1, -1), (w - m, h - m, -1, -1)):
        d.line([(x, y), (x + dx * ln, y)], fill=(255, 255, 255, 70), width=2)
        d.line([(x, y), (x, y + dy * ln)], fill=(255, 255, 255, 70), width=2)
    return img


def from_photo(path, w, h):
    """EXIF 회전 반영 → 슬롯 비율로 중앙 크롭 → 리사이즈."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    tr, sr = w / h, im.width / im.height
    if sr > tr:
        nw = int(im.height * tr)
        im = im.crop(((im.width - nw) // 2, 0, (im.width + nw) // 2, im.height))
    else:
        nh = int(im.width / tr)
        # 현장 사진은 위쪽에 작업 대상이 오는 경우가 많아 살짝 위를 남깁니다.
        top = int((im.height - nh) * 0.38)
        im = im.crop((0, top, im.width, top + nh))
    return im.resize((w, h), Image.LANCZOS)


def save_webp(img, path, target_kb=TARGET_KB):
    """30KB 이하가 될 때까지 품질을 낮추고, 그래도 넘으면 살짝 뭉갠 뒤 재시도."""
    q = 88
    for q in range(88, 24, -4):
        img.save(path, "WEBP", quality=q, method=6)
        if os.path.getsize(path) <= target_kb * 1024:
            return q, os.path.getsize(path)
    soft = img.filter(ImageFilter.GaussianBlur(.5))
    for q in range(52, 12, -4):
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
                        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".heic")))

    mode = f"현장사진 {len(photos)}장" if photos else "브랜드 플레이트(원본 없음)"
    print(f"슬롯 {len(SLOT_ORDER)}개 · 소스: {mode}\n")

    over = 0
    for i, key in enumerate(SLOT_ORDER):
        name, w, h, alt = IMAGES[key]
        dst = os.path.join(OUT, name)
        if photos:
            src = photos[i % len(photos)]
            img, label = from_photo(os.path.join(RAW, src), w, h), src
        else:
            img, label = make_plate(w, h, key.upper(), PLATE_ICON.get(key, "jet")), "플레이트"
        q, size = save_webp(img, dst)
        if size > TARGET_KB * 1024:
            over += 1
        print(f"  {'OK ' if size <= TARGET_KB*1024 else '초과'} {name:<40} {w}x{h} "
              f"{size/1024:5.1f}KB q{q:<3} ← {label}")

    print(f"\n완료. 30KB 초과 {over}개")


if __name__ == "__main__":
    main()
