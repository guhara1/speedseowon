#!/usr/bin/env bash
# ============================================================================
# Netlify 빌드 스크립트
#
#   Netlify 빌드 환경은 인터넷이 열려 있어 구글드라이브 원본을 직접 받습니다.
#   개발 샌드박스에서 drive.google.com 이 막혀 있어도 배포본에는 실제 현장사진이
#   들어가게 하려고 이 단계를 둡니다.
#
#   순서
#     1. 드라이브 폴더 → tools/raw/ 다운로드   (실패해도 빌드는 계속)
#     2. tools/make_images.py                  → img/*.webp (30KB 이하)
#     3. _build/build.py                       → 248개 HTML + sitemap + rss + robots
# ============================================================================
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

FOLDER_ID="${DRIVE_FOLDER_ID:-11dJNqXRX1jePsz_Z9G4oGOYXqrDsYhQe}"
RAW="$ROOT/tools/raw"

echo "▶ 1/3  파이썬 의존성"
python3 -m pip install --quiet --disable-pip-version-check pillow gdown || {
  echo "  ! pip 실패 — 커밋된 이미지를 그대로 씁니다"; }

echo "▶ 2/3  구글드라이브 현장사진 내려받기 (폴더 $FOLDER_ID)"
mkdir -p "$RAW"
if python3 -m gdown --folder "https://drive.google.com/drive/folders/${FOLDER_ID}" \
      -O "$RAW" --remaining-ok --quiet; then
  # gdown 이 하위 폴더를 만들면 평탄화
  find "$RAW" -mindepth 2 -type f -exec mv -n {} "$RAW"/ \; 2>/dev/null || true
  find "$RAW" -mindepth 1 -type d -empty -delete 2>/dev/null || true
  COUNT=$(find "$RAW" -maxdepth 1 -type f \
          \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) | wc -l | tr -d ' ')
  echo "  → 원본 ${COUNT}장 확보"
else
  COUNT=0
  echo "  ! 다운로드 실패 (폴더 공개 설정 확인 필요) — 커밋된 이미지를 그대로 씁니다"
fi

echo "▶ 3/3  이미지 변환 + 사이트 생성"
if [ "${COUNT:-0}" -gt 0 ]; then
  python3 tools/make_images.py || echo "  ! 이미지 변환 실패 — 커밋본 유지"
else
  echo "  · 원본이 없어 이미지 변환을 건너뜁니다"
fi

python3 _build/build.py

echo "✔ 빌드 완료"
