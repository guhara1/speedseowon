#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""파비콘 세트 생성.

마크: 잉크색 라운드 사각형 + 앰버 물방울 + 시안 배관 라인.
16px 에서도 형태가 뭉개지지 않도록 요소를 셋으로 제한하고 4배 슈퍼샘플링합니다.

    python3 tools/make_favicon.py
"""
import math
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INK = (10, 25, 41)
AMBER = (255, 176, 31)
CYAN = (0, 168, 200)
SS = 8          # 슈퍼샘플 배율


def drop_polygon(cx, cy, r, apex_y):
    """원 + 접선 두 개로 만든 물방울 윤곽."""
    d = cy - apex_y
    if d <= r:
        d = r * 1.6
        apex_y = cy - d
    th = math.acos(r / d)
    pts = [(cx, apex_y)]
    # 오른쪽 접점 → 아래를 돌아 왼쪽 접점까지
    start = -math.pi / 2 + th
    end = start + (2 * math.pi - 2 * th)
    steps = 72
    for i in range(steps + 1):
        a = start + (end - start) * i / steps
        pts.append((cx + r * math.sin(a + math.pi / 2 - math.pi / 2) * 0 + r * math.cos(a),
                    cy + r * math.sin(a)))
    return pts


def draw_mark(size, pad_ratio=0.0, rounded=True, bg=INK):
    """size: 최종 픽셀. pad_ratio: 마스커블 아이콘용 여백 비율."""
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    pad = int(S * pad_ratio)
    box = [pad, pad, S - pad - 1, S - pad - 1]
    inner = box[2] - box[0]

    if rounded:
        d.rounded_rectangle(box, radius=int(inner * 0.22), fill=bg)
    else:
        d.rectangle(box, fill=bg)

    cx = box[0] + inner / 2
    # 물방울
    r = inner * 0.195
    cy = box[1] + inner * 0.485
    apex = box[1] + inner * 0.155
    d.polygon(drop_polygon(cx, cy, r, apex), fill=AMBER)

    # 물방울 안쪽 하이라이트 (잉크색으로 파내 형태를 또렷하게)
    hl_r = r * 0.42
    d.ellipse([cx - r * 0.62 - hl_r * 0, cy - r * 0.1,
               cx - r * 0.62 + hl_r * 1.5, cy - r * 0.1 + hl_r * 1.5],
              outline=INK, width=max(2, int(inner * 0.022)))

    # 시안 배관 라인
    bar_h = max(3, int(inner * 0.075))
    by = box[1] + inner * 0.775
    d.rounded_rectangle([cx - inner * 0.26, by, cx + inner * 0.26, by + bar_h],
                        radius=bar_h // 2, fill=CYAN)
    # 배관 이음부 두 곳
    for sx in (-0.155, 0.155):
        d.rounded_rectangle([cx + inner * sx - bar_h * 0.42, by - bar_h * 0.5,
                             cx + inner * sx + bar_h * 0.42, by + bar_h * 1.5],
                            radius=bar_h // 3, fill=INK)

    return img.resize((size, size), Image.LANCZOS)


SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="스피드서원">
  <rect width="64" height="64" rx="14" fill="rgb{INK}"/>
  <path d="M32 10.5c0 0 12.5 14.2 12.5 21.5a12.5 12.5 0 0 1-25 0C19.5 24.7 32 10.5 32 10.5z"
        fill="rgb{AMBER}"/>
  <path d="M25.5 33.5a6.5 6.5 0 0 0 6.5 6.5" fill="none" stroke="rgb{INK}"
        stroke-width="2.6" stroke-linecap="round" opacity=".6"/>
  <rect x="15.5" y="49" width="33" height="5" rx="2.5" fill="rgb{CYAN}"/>
  <rect x="23" y="47.6" width="4" height="7.8" rx="1.4" fill="rgb{INK}"/>
  <rect x="37" y="47.6" width="4" height="7.8" rx="1.4" fill="rgb{INK}"/>
</svg>
"""

MANIFEST = """{
  "name": "스피드서원 — 전국 배관공사·하수구막힘",
  "short_name": "스피드서원",
  "description": "전국 229개 시·군·구 24시간 배관 출장. 하수구막힘·누수탐지·배관공사.",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "background_color": "#0A1929",
  "theme_color": "#0A1929",
  "lang": "ko",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" },
    { "src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml" }
  ]
}
"""


def main():
    out = []

    with open(os.path.join(ROOT, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(SVG)
    out.append("favicon.svg")

    # 브라우저 탭용 — 16/32/48 을 한 ico 에 담습니다
    ico = draw_mark(64)
    ico.save(os.path.join(ROOT, "favicon.ico"), format="ICO",
             sizes=[(16, 16), (32, 32), (48, 48)])
    out.append("favicon.ico")

    for size, name in ((180, "apple-touch-icon.png"),
                       (192, "icon-192.png"),
                       (512, "icon-512.png")):
        draw_mark(size).save(os.path.join(ROOT, name), optimize=True)
        out.append(name)

    # 마스커블 — 안드로이드가 원형으로 잘라도 마크가 살아남도록 여백 확보
    m = Image.new("RGBA", (512, 512), INK + (255,))
    m.paste(draw_mark(512, pad_ratio=0.16, rounded=False), (0, 0),
            draw_mark(512, pad_ratio=0.16, rounded=False))
    m.save(os.path.join(ROOT, "icon-maskable-512.png"), optimize=True)
    out.append("icon-maskable-512.png")

    with open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8") as f:
        f.write(MANIFEST)
    out.append("site.webmanifest")

    for n in out:
        p = os.path.join(ROOT, n)
        print(f"  {n:<28} {os.path.getsize(p)/1024:6.1f}KB")


if __name__ == "__main__":
    main()
