# 색인 등록 — 가장 빠른 순서

배포 후 이 순서대로 하면 됩니다. **소요 시간은 도구별로 다릅니다.**

| 경로 | 자동화 | 실제 반영 |
|---|---|---|
| IndexNow (Bing·Naver·Yandex) | ✅ 스크립트 | 수 시간 ~ 1일 |
| 네이버 서치어드바이저 | 수동 등록 후 자동 | 1~7일 |
| 구글 Search Console | 수동 | 1일 ~ 수 주 |

> **주의** — 구글의 `google.com/ping?sitemap=` 엔드포인트는 2023년 폐지됐습니다.
> "핑 한 번으로 즉시 색인"을 내세우는 방법은 지금은 동작하지 않습니다.
> 구글에는 사이트맵 제출 + URL 검사 도구가 유일한 공식 경로입니다.

---

## 사이트가 내보내는 파일

빌드하면 루트에 자동 생성됩니다.

| 파일 | 용도 |
|---|---|
| `sitemap.xml` | 사이트맵 인덱스 (아래 두 개를 묶음) |
| `sitemap-core.xml` | 메인·지역 허브 |
| `sitemap-area.xml` | 시·도 17 + 시·군·구 229 (이미지 확장 포함) |
| `rss.xml` | 248개 항목 RSS 2.0 — **네이버 RSS 제출용** |
| `robots.txt` | Googlebot / Yeti / NaverBot / Daumoa / bingbot 개별 허용 |
| `<INDEXNOW_KEY>.txt` | IndexNow 소유 확인 키 |

`robots.txt` 에 크롤 지연(`Crawl-delay`)을 **일부러 넣지 않았습니다.**
네이버 Yeti 는 지연을 명시하면 그대로 따르는데, 229개 지역 페이지 수집이 며칠씩 늦어집니다.

---

## 1. 구글 Search Console

1. https://search.google.com/search-console → 속성 추가 → **URL 접두어**
   `https://speedseowon.netlify.app/`
2. 소유권 확인 → **HTML 태그** 방식 선택 → `content="..."` 값 복사
3. `_build/site/config.py` 의 `GOOGLE_VERIFY` 에 붙여넣기 → `python3 _build/build.py` → 배포
4. Search Console 에서 **확인** 클릭
5. 좌측 **Sitemaps** → `sitemap.xml` 입력 → 제출
6. 상단 검색창에 URL 입력 → **URL 검사** → **색인 생성 요청**

> 색인 생성 요청은 하루 할당량이 있습니다(대략 10~15건).
> 중요도 순으로 넣으세요: 메인 → `/area/` → 서울·경기·부산 시·도 → 출동 실적 많은 시·군·구.
> 나머지는 사이트맵으로 자연 수집됩니다.

## 2. 네이버 서치어드바이저

1. https://searchadvisor.naver.com → 웹마스터도구 → 사이트 등록
2. 소유확인 → **HTML 태그** → `content` 값을 `config.py` 의 `NAVER_VERIFY` 에 → 빌드 → 배포 → 확인
3. **요청 → 사이트맵 제출** : `sitemap.xml`
4. **요청 → RSS 제출** : `rss.xml` ← 네이버는 RSS를 별도로 받습니다. 꼭 같이 넣으세요.
5. **요청 → 웹페이지 수집** : 메인부터 하나씩 (하루 한도 있음)
6. **검증 → 로봇스룰 검증** 으로 Yeti 가 막히지 않는지 확인

## 3. IndexNow — 자동, 가장 빠름

Bing·Naver·Yandex·Seznam 이 공유하는 규격입니다. 한 번 보내면 함께 전달됩니다.

```bash
python3 tools/indexnow.py                        # 248개 전체
python3 tools/indexnow.py /area/seoul/gangnam/   # 특정 페이지만
```

키 파일 `<INDEXNOW_KEY>.txt` 가 사이트 루트에 실제로 열려야 검증됩니다.
배포 후 브라우저에서 한 번 확인하세요.

응답 코드: `200/202` 접수됨 · `403` 키 검증 실패 · `422` host 불일치

**콘텐츠를 고칠 때마다 이 스크립트를 돌리세요.** 재수집이 가장 빨라집니다.

## 4. 다음(Daum)

https://register.search.daum.net/index.daum 에서 사이트 등록.
`DAUM_VERIFY` 값을 받으면 `config.py` 에 넣습니다.

## 5. Bing Webmaster Tools (선택)

Search Console 계정을 그대로 가져올 수 있습니다.
IndexNow 를 이미 쓰고 있으므로 필수는 아니지만, 색인 현황을 보려면 등록해 두면 편합니다.

---

## 색인이 안 될 때 확인 순서

1. `robots.txt` 가 열리는가 → `https://speedseowon.netlify.app/robots.txt`
2. `sitemap.xml` 이 XML 로 열리는가 (HTML 오류 페이지가 아니어야 합니다)
3. 해당 페이지의 `<link rel="canonical">` 이 자기 자신을 가리키는가
4. `<meta name="robots">` 에 `noindex` 가 없는가
5. Search Console **페이지 → 색인이 생성되지 않음** 사유 확인
   - "검색된 - 현재 색인이 생성되지 않음" = 크롤 대기. 내부링크를 늘리면 빨라집니다.
   - "중복, 사용자가 표준으로 지정하지 않음" = 지역 페이지 내용이 서로 너무 비슷하다는 뜻.
     이 사이트는 229개 본문 중복 0건으로 만들었지만, 새 페이지를 추가할 때 주의하세요.

## 실제로 색인을 앞당기는 것

도구 제출은 시작일 뿐입니다. 아래 세 가지가 훨씬 크게 작용합니다.

- **내부링크** — 고아 페이지는 수집이 늦습니다. 이 사이트는 시·군·구마다
  형제 지역 8개가 상호 링크돼 있어 크롤러가 229개를 순회할 수 있습니다.
- **외부 유입 1건** — 네이버 블로그·플레이스, 구글 비즈니스 프로필에서 링크 하나만 걸려도
  수집 우선순위가 확연히 올라갑니다. 특히 **네이버는 자사 서비스 내 링크에 민감합니다.**
- **콘텐츠 갱신** — 지역 페이지에 실제 시공 사례를 계속 추가하면
  재크롤 주기가 짧아집니다. 갱신 후 `tools/indexnow.py` 를 돌리세요.
