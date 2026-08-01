#!/usr/bin/env bash
# ============================================================================
# 구글드라이브 실제 작업사진 → 사이트 이미지로 교체
#
#   구글드라이브가 차단되지 않은 PC에서 한 번만 돌리면 됩니다.
#   HTML은 손댈 필요 없습니다. 파일명이 같아 그대로 교체됩니다.
#
#   사용법
#     bash tools/import-drive-photos.sh
#     python3 tools/make_images.py     # ← 스크립트가 자동으로 실행합니다
# ============================================================================
set -euo pipefail

FOLDER_ID="11dJNqXRX1jePsz_Z9G4oGOYXqrDsYhQe"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW="$ROOT/tools/raw"

mkdir -p "$RAW"

if ! command -v gdown >/dev/null 2>&1; then
  echo "gdown 설치 중..."
  pip install --quiet gdown
fi

echo "구글드라이브 폴더에서 원본 사진을 내려받습니다..."
gdown --folder "https://drive.google.com/drive/folders/${FOLDER_ID}" -O "$RAW"

# gdown 이 하위 폴더를 만들면 평탄화합니다
find "$RAW" -mindepth 2 -type f -exec mv -n {} "$RAW"/ \; 2>/dev/null || true
find "$RAW" -mindepth 1 -type d -empty -delete 2>/dev/null || true

COUNT=$(find "$RAW" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) | wc -l | tr -d ' ')
echo "원본 ${COUNT}장 확보 → WebP 30KB 이하로 변환합니다."

python3 "$ROOT/tools/make_images.py"

echo
echo "완료. img/ 아래 파일이 실제 현장 사진으로 교체됐습니다."
echo "슬롯보다 사진이 많으면 tools/make_images.py 의 SLOTS 순서를 조정해"
echo "원하는 사진이 원하는 자리에 오도록 맞추실 수 있습니다."
