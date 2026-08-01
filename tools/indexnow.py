#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IndexNow 색인 통보.

IndexNow 는 Bing·Naver·Yandex·Seznam 이 함께 쓰는 규격입니다.
한 곳에 보내면 참여 검색엔진에 공유되므로, 네이버 색인을 앞당기는 가장 빠른 자동 경로입니다.

  ※ 구글은 IndexNow 에 참여하지 않습니다. 구글은 Search Console 에서
    사이트맵 제출 + URL 검사 도구로 요청해야 합니다 (INDEXING.md 참고).
  ※ 구글의 sitemap ping 엔드포인트는 2023년에 폐지됐습니다. 쓰지 마세요.

    python3 tools/indexnow.py            # sitemap 전체(248개) 통보
    python3 tools/indexnow.py /area/seoul/gangnam/ /price/   # 일부만
"""
import json
import re
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_build", "site"))
from config import SITE, INDEXNOW_KEY  # noqa: E402

ENDPOINT = "https://api.indexnow.org/IndexNow"
HOST = SITE.split("://", 1)[1].rstrip("/")
BATCH = 10000   # 규격상 1회 최대 10,000 URL


def urls_from_sitemaps():
    out = []
    for name in ("sitemap-core.xml", "sitemap-area.xml"):
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            out += re.findall(r"<loc>(.*?)</loc>", open(p, encoding="utf-8").read())
    return out


def submit(urls):
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{SITE}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode(errors="replace")[:300]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    urls = ([SITE + a if a.startswith("/") else a for a in args]
            if args else urls_from_sitemaps())
    if not urls:
        print("보낼 URL이 없습니다. 먼저 python3 _build/build.py 를 실행하세요.")
        return 1

    print(f"IndexNow 통보  host={HOST}  URL {len(urls)}개")
    print(f"키 파일: {SITE}/{INDEXNOW_KEY}.txt  (배포본에 반드시 존재해야 합니다)\n")

    for i in range(0, len(urls), BATCH):
        chunk = urls[i:i + BATCH]
        try:
            status, body = submit(chunk)
        except Exception as e:
            print(f"  실패 {i}~{i+len(chunk)}: {e}")
            continue
        # 200/202 = 접수됨, 403 = 키 검증 실패, 422 = URL 이 host 와 불일치
        note = {200: "접수됨", 202: "접수됨(키 검증 대기)",
                400: "요청 형식 오류", 403: "키 검증 실패 — 키 파일 확인",
                422: "URL 이 host 와 불일치", 429: "요청 과다"}.get(status, "")
        print(f"  {i+1}~{i+len(chunk)}  HTTP {status}  {note}  {body}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
