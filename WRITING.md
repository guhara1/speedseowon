# WRITING.md — 매일 글 쓰는 법

블로그(자가진단 가이드)에 새 글을 올리는 전체 과정입니다. **코드는 건드리지 않습니다.**
데이터 파일에 dict 하나를 추가하면 글 페이지·썸네일·목록·RSS·사이트맵·스키마가 전부 자동으로 생성됩니다.

## 한눈에 보는 순서

```bash
# 1. _build/site/data_guides.py 를 열어 GUIDES 목록 "맨 앞"에 새 글 dict 추가 (최신 글이 위로)
# 2. 빌드
python3 _build/build.py
# 3. 커밋·푸시 → Netlify 자동 배포
git add -A
git commit -m "글: <제목>"
git push
```

푸시하면 몇 분 안에 `https://speedseowon.netlify.app/guide/<slug>/` 로 올라갑니다.

---

## 1. 새 글 dict 양식

`_build/site/data_guides.py` 의 `GUIDES` 목록 **맨 앞**에 붙여넣고 내용을 채웁니다.

```python
dict(
    slug="my-new-post",                # URL이 됩니다: /guide/my-new-post/  (영문 소문자와 하이픈만)
    title="글 제목 — 검색하는 사람 말로",
    date="2026-08-02",                 # 오늘 날짜
    cat="막힘",                        # 카테고리 한 단어: 막힘/누수/냄새/긴급/예방/상식/분쟁 등
    minutes=4,                         # 읽는 시간(분)
    summary="목록 카드와 검색결과에 나올 2문장 요약. 이 글이 무엇을 해결해 주는지.",
    body=[
        ("p", "도입 문단. 검색해서 들어온 사람이 처음 읽는 곳 — 결론부터."),
        ("h2", "소제목"),
        ("check", ["지금 바로 확인할 것 1", "확인할 것 2", "확인할 것 3"]),
        ("table", ("표 캡션", ["헤더1", "헤더2", "헤더3"], [
            ["행1-1", "행1-2", "행1-3"],
            ["행2-1", "행2-2", "행2-3"],
        ])),
        ("do",   ["직접 해도 안전한 조치 1", "조치 2"]),
        ("dont", ["하면 안 되는 행동 1", "행동 2"]),
        ("call", "이럴 땐 부르시는 게 빠릅니다 — 업체 호출 기준을 정직하게."),
        ("tip",  "짧은 강조 팁 한 줄."),
    ],
    faq=[
        ("자주 받는 질문 1?", "답변."),
        ("자주 받는 질문 2?", "답변."),
        ("자주 받는 질문 3?", "답변."),        # FAQ는 2~3개. FAQPage 스키마로도 나갑니다.
    ],
    services=["drain-clog", "sink-drain"],   # 관련 서비스 slug (사이드바 링크) — 아래 목록 참고
    price="drain-clog",                      # 관련 비용 페이지 slug (없으면 이 줄 삭제)
),
```

### body 블록 종류 (필요한 것만 골라 씁니다)

| 블록 | 형태 | 화면 표시 |
|---|---|---|
| `("p", "문단")` | 일반 문단 | 본문 텍스트 |
| `("h2", "소제목")` | 섹션 제목 | 큰 소제목 |
| `("check", [..])` | 체크리스트 | ✓ 체크 목록 |
| `("table", (캡션, [헤더], [[행],..]))` | 비교 표 | 캡션 달린 표 |
| `("do", [..])` | 해도 되는 것 | 초록 테두리 박스 |
| `("dont", [..])` | 하면 안 되는 것 | 빨강 테두리 박스 |
| `("call", "문장")` | 호출 기준 | 전화번호 버튼이 붙은 박스 |
| `("tip", "한 줄")` | 팁 | 앰버 강조 박스 |

### 자동으로 되는 것 (직접 할 일 없음)

- **썸네일** — 제목으로 SVG 텍스트 이미지가 자동 생성됩니다. 이미지 준비 불필요.
- `/guide/` 목록 페이지 갱신 (최신 글이 크게 맨 위로)
- `rss.xml` · `sitemap-core.xml` 반영 → 네이버·구글 색인
- `Article` + `FAQPage` 스키마, 브레드크럼, canonical, og 태그
- 사이드바의 관련 서비스·비용 링크, 하단 '함께 읽으면 좋은 글'

### 색인을 더 빨리 태우려면 (선택)

```bash
python3 tools/indexnow.py    # Bing·Naver 에 즉시 통보
```

네이버 서치어드바이저 → 요청 → 웹 페이지 수집에 새 글 URL을 넣으면 가장 빠릅니다.

---

## 2. 글 원칙 — 고객이 읽고 꼭 필요한 내용만

1. **결론부터.** 검색해서 들어온 사람이 3분 안에 '지금 뭘 해야 하는지' 알게 합니다.
2. **자가조치 범위를 정직하게.** 직접 해도 되는 것(`do`)과 하면 안 되는 것(`dont`)을 명확히 가릅니다.
   전부 "업체 부르세요"로 끝나는 글은 신뢰를 잃습니다.
3. **없는 데이터·없는 사례를 지어내지 않습니다.** 실제 현장에서 본 것만 씁니다.
4. **비용 언급은 범위로.** 확정가처럼 쓰지 않고, 자세한 건 `/price/` 페이지로 링크를 보냅니다.
5. **제목은 고객의 검색어로.** "배수 지연 현상의 원인 분석" ✗ → "물이 천천히 내려갈 때" ✓

## 3. 글감 (검색 수요 있는 순)

변기 물 약할 때 / 세탁기 배수구 냄새 / 싱크대 밑 물 고임 / 보일러 분배기 누수 /
옥상 우수관 막힘 / 겨울철 계량기 보온 / 욕실 실리콘 곰팡이와 누수 구분 /
아랫집 누수 연락 받았을 때 / 관리비에 포함되는 수리 범위 / 상가 그리스트랩 관리

## 4. 참고 — 관련 링크에 쓸 slug 목록

**서비스** (`services=[..]` 에 사용): drain-clog, pipe-clog, toilet-clog, sink-drain, basin-clog,
kitchen-drain, drain-open, trap, debris, hydro-jetting, endoscope, inspection,
water-leak, leak-detection, leak-repair, bath-leak, ceiling-leak, kitchen-leak,
faucet, toilet-replace, toilet-parts, basin-replace, water-repair, plumbing,
repipe, apartment, commercial

**비용** (`price=".."` 에 사용): drain-clog, toilet-clog, leak-detection, leak-repair,
faucet, toilet-replace, hydro-jetting, endoscope, how-we-quote, night-surcharge
