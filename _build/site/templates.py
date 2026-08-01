# -*- coding: utf-8 -*-
"""공통 HTML 셸 (head / 헤더 / 푸터 / 스크립트)."""
import json

from config import (SITE, BRAND, OWNER, PHONE, PHONE_TEL, PHONE_E164, EMAIL,
                    BIZ_NO, LICENSE_NO, ADDRESS, IMAGES, REVIEWED,
                    STAT_TOTAL_CASES, STAT_SIGUNGU, RSS_TITLE,
                    GOOGLE_VERIFY, NAVER_VERIFY, BING_VERIFY, DAUM_VERIFY)


def verify_tags():
    """소유권 확인 메타태그 — 값이 있을 때만 출력합니다."""
    pairs = [("google-site-verification", GOOGLE_VERIFY),
             ("naver-site-verification", NAVER_VERIFY),
             ("msvalidate.01", BING_VERIFY),
             ("daum-site-verification", DAUM_VERIFY)]
    return "".join(f'<meta name="{k}" content="{v}">\n' for k, v in pairs if v)


def img_tag(key, cls="", sizes=None, priority=False, alt=None):
    f, w, h, a = IMAGES[key]
    return (f'<img src="/img/{f}" width="{w}" height="{h}" alt="{alt or a}"'
            f'{" class=" + chr(34) + cls + chr(34) if cls else ""}'
            f'{" fetchpriority=" + chr(34) + "high" + chr(34) if priority else ""}'
            f' loading="{"eager" if priority else "lazy"}" decoding="async">')


def ld(obj):
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def business_ld(rating=None):
    """rating: {'aggregateRating':…, 'review':[…]} 를 넘기면 같은 노드에 합칩니다.
    (@id 가 같은 노드를 두 번 내보내면 파서가 어느 쪽을 쓸지 모호해집니다)"""
    node = {
        "@context": "https://schema.org", "@type": "Plumber",
        "@id": f"{SITE}/#business", "name": BRAND,
        "url": SITE + "/", "logo": f"{SITE}/img/{IMAGES['author'][0]}",
        "image": [f"{SITE}/img/{IMAGES['og'][0]}"]
                 + [f"{SITE}/img/{IMAGES[k][0]}" for k in ("hero1", "hero2", "case1")],
        "description": "전국 24시간 배관공사·하수구막힘·누수탐지 전문. 내시경 관로조사 기반 원인 진단과 고압세척 시공.",
        "telephone": PHONE_E164, "priceRange": "₩₩", "foundingDate": "2011-04-01",
        "address": {"@type": "PostalAddress", "streetAddress": "○○로 00, 3층",
                    "addressLocality": "수원시 팔달구", "addressRegion": "경기도",
                    "postalCode": "16000", "addressCountry": "KR"},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59"}],
        "founder": {"@type": "Person", "name": OWNER, "jobTitle": "대표 / 배관기능사"},
        "email": EMAIL,
    }
    if rating:
        node.update(rating)
    return node


def head(title, desc, canonical, extra_ld=None, og_image=None, robots=None):
    ogimg = og_image or f"{SITE}/img/{IMAGES['og'][0]}"
    blocks = "".join(ld(o) for o in (extra_ld or []))
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="{robots or 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1'}">
<meta name="googlebot" content="{robots or 'index,follow,max-image-preview:large,max-snippet:-1'}">
<meta name="NaverBot" content="All">
<meta name="Yeti" content="All">
<meta name="author" content="{OWNER} · {BRAND} 대표 / 배관기능사">
<meta name="theme-color" content="#0A1929">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
{verify_tags()}<link rel="alternate" type="application/rss+xml" title="{RSS_TITLE}" href="{SITE}/rss.xml">
<link rel="sitemap" type="application/xml" href="{SITE}/sitemap.xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{ogimg}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/assets/css/site.css">
{blocks}
</head>
<body>
<a class="skip" href="#main">본문 바로가기</a>
"""


HEADER = f"""
<div class="utilbar">
  <div class="wrap">
    <span class="status"><span class="pulse" aria-hidden="true"></span>지금 접수 가능 · 전국 24시간 야간·주말 출동</span>
    <nav aria-label="보조 메뉴">
      <a href="/about/">회사소개</a>
      <a href="/about/editorial/">콘텐츠 작성 원칙</a>
      <a href="/review/">고객후기</a>
      <a href="/contact/">견적문의</a>
    </nav>
  </div>
</div>

<header class="header">
  <div class="wrap">
    <a href="/" class="logo" aria-label="{BRAND} 홈">스피드<b>서원</b><span>SINCE 2011</span></a>
    <button class="burger" id="burger" aria-label="전체 메뉴 열기" aria-expanded="false" aria-controls="gnb">
      <i></i><i></i><i></i>
    </button>
    <ul class="gnb" id="gnb">
      <li>
        <a href="/service/" aria-haspopup="true">서비스</a>
        <div class="drop mega">
          <div class="mega-grid">
            <div>
              <h4>막힘 · 관통</h4>
              <a href="/service/drain-clog/">하수구막힘</a>
              <a href="/service/pipe-clog/">배관막힘</a>
              <a href="/service/toilet-clog/">변기막힘</a>
              <a href="/service/sink-drain/">싱크대하수구막힘</a>
              <a href="/service/basin-clog/">세면대막힘</a>
              <a href="/service/kitchen-drain/">주방배수구막힘</a>
              <a href="/service/drain-open/">배수구뚫음</a>
              <a href="/service/backflow/">하수구 역류</a>
            </div>
            <div>
              <h4>누수 · 물샘</h4>
              <a href="/service/leak-detection/">누수탐지</a>
              <a href="/service/leak-repair/">누수공사</a>
              <a href="/service/bath-leak/">욕실배관누수</a>
              <a href="/service/kitchen-leak/">주방배관누수</a>
              <a href="/service/water-leak/">수도누수</a>
              <a href="/service/water-repair/">수도수리</a>
              <a href="/service/ceiling-leak/">천장 물샘</a>
            </div>
            <div>
              <h4>교체 · 설치</h4>
              <a href="/service/faucet/">수전교체</a>
              <a href="/service/toilet-replace/">화장실변기교체</a>
              <a href="/service/toilet-parts/">변기부속품수리</a>
              <a href="/service/basin-replace/">세면대교체</a>
              <a href="/service/trap/">배수 트랩 교체</a>
            </div>
            <div>
              <h4>공사 · 진단</h4>
              <a href="/service/plumbing/">배관설비 공사</a>
              <a href="/service/repipe/">노후 배관 교체</a>
              <a href="/service/hydro-jetting/">고압세척</a>
              <a href="/service/endoscope/">내시경 관로조사</a>
              <a href="/service/debris/">이물질 제거</a>
              <a href="/service/commercial/">상가·식당 배관</a>
              <a href="/service/apartment/">아파트 공용배관</a>
            </div>
          </div>
          <div class="mega-foot">
            <span>증상을 모르겠다면 전화 한 통이면 됩니다. 물 빠짐 속도와 소리만으로 구간을 좁혀 드립니다.</span>
            <a href="/service/">서비스 전체 보기 →</a>
          </div>
        </div>
      </li>
      <li>
        <a href="/area/" aria-haspopup="true">지역별 출장</a>
        <div class="drop mega">
          <div class="mega-grid">
            <div>
              <h4>수도권</h4>
              <a href="/area/seoul/">서울특별시 25개 구</a>
              <a href="/area/gyeonggi/">경기도 31개 시·군</a>
              <a href="/area/incheon/">인천광역시 11개 군·구</a>
            </div>
            <div>
              <h4>영남권</h4>
              <a href="/area/busan/">부산광역시</a>
              <a href="/area/daegu/">대구광역시</a>
              <a href="/area/ulsan/">울산광역시</a>
              <a href="/area/gyeongbuk/">경상북도</a>
              <a href="/area/gyeongnam/">경상남도</a>
            </div>
            <div>
              <h4>충청 · 호남</h4>
              <a href="/area/daejeon/">대전광역시</a>
              <a href="/area/sejong/">세종특별자치시</a>
              <a href="/area/chungbuk/">충청북도</a>
              <a href="/area/chungnam/">충청남도</a>
              <a href="/area/jeonbuk/">전북특별자치도</a>
              <a href="/area/jeonnam-gwangju/">전남광주통합특별시</a>
            </div>
            <div>
              <h4>강원 · 제주</h4>
              <a href="/area/gangwon/">강원특별자치도</a>
              <a href="/area/jeju/">제주특별자치도</a>
            </div>
          </div>
          <div class="mega-foot">
            <span>시·도를 누르면 관할 구·군이, 구·군을 누르면 출동 가능한 행정동이 모두 나옵니다.</span>
            <a href="/area/">전국 {STAT_SIGUNGU}개 시·군·구 보기 →</a>
          </div>
        </div>
      </li>
      <li>
        <a href="/price/" aria-haspopup="true">비용·견적</a>
        <div class="drop">
          <div class="grp">가격표</div>
          <a href="/price/drain-clog/">하수구막힘 비용</a>
          <a href="/price/toilet-clog/">변기막힘 비용</a>
          <a href="/price/leak-detection/">누수탐지 비용</a>
          <a href="/price/leak-repair/">누수공사 비용</a>
          <a href="/price/hydro-jetting/">고압세척 비용</a>
          <hr>
          <div class="grp">견적 안내</div>
          <a href="/price/how-we-quote/">견적 산정 기준 공개</a>
          <a href="/price/night-surcharge/">야간·공휴일 할증 안내</a>
          <a href="/contact/">무료 견적 신청</a>
        </div>
      </li>
      <li>
        <a href="/case/" aria-haspopup="true">시공사례</a>
        <div class="drop">
          <div class="grp">유형별</div>
          <a href="/case/drain-clog/">하수구막힘 사례</a>
          <a href="/case/leak/">누수 사례</a>
          <a href="/case/toilet/">변기 사례</a>
          <a href="/case/repipe/">노후배관 교체 사례</a>
          <hr>
          <div class="grp">건물별</div>
          <a href="/case/apartment/">아파트</a>
          <a href="/case/villa/">빌라·다세대</a>
          <a href="/case/restaurant/">식당·상가</a>
        </div>
      </li>
      <li>
        <a href="/guide/" aria-haspopup="true">자가진단</a>
        <div class="drop">
          <div class="grp">증상으로 찾기</div>
          <a href="/guide/slow-drain/">물이 천천히 내려갈 때</a>
          <a href="/guide/sewer-smell/">하수구 냄새가 올라올 때</a>
          <a href="/guide/backflow/">역류가 발생했을 때</a>
          <a href="/guide/water-meter/">계량기가 계속 돌 때</a>
          <a href="/guide/wall-damp/">벽지가 젖었을 때</a>
          <hr>
          <div class="grp">알아두기</div>
          <a href="/guide/winter-freeze/">겨울 동파 대처</a>
          <a href="/guide/tenant-landlord/">전세·월세 수리비 부담</a>
        </div>
      </li>
      <li>
        <a href="/about/" aria-haspopup="true">회사소개</a>
        <div class="drop">
          <a href="/about/">{BRAND} 소개</a>
          <a href="/about/equipment/">보유 장비</a>
          <a href="/about/warranty/">6개월 보증 정책</a>
          <a href="/about/editorial/">콘텐츠 작성·검수 원칙</a>
          <hr>
          <a href="/contact/">오시는 길 · 문의</a>
        </div>
      </li>
    </ul>
    <a href="tel:{PHONE_TEL}" class="hd-call">
      <span><small>24시간 접수</small><b>{PHONE}</b></span>
    </a>
  </div>
</header>
"""


FOOTER = f"""
<footer class="footer">
  <div class="wrap">
    <div class="ft-grid">
      <div class="ft-brand">
        <div class="logo">스피드<b>서원</b></div>
        <p>전국 배관공사·하수구막힘 전문<br>내시경 진단 · 고압세척 · 누수탐지</p>
        <a href="tel:{PHONE_TEL}" class="ft-call">{PHONE}</a>
        <p>연중무휴 24시간 접수</p>
      </div>
      <div>
        <h4>막힘</h4>
        <ul>
          <li><a href="/service/drain-clog/">하수구막힘</a></li>
          <li><a href="/service/pipe-clog/">배관막힘</a></li>
          <li><a href="/service/toilet-clog/">변기막힘</a></li>
          <li><a href="/service/sink-drain/">싱크대하수구막힘</a></li>
          <li><a href="/service/kitchen-drain/">주방배수구막힘</a></li>
          <li><a href="/service/hydro-jetting/">고압세척</a></li>
        </ul>
      </div>
      <div>
        <h4>누수</h4>
        <ul>
          <li><a href="/service/leak-detection/">누수탐지</a></li>
          <li><a href="/service/leak-repair/">누수공사</a></li>
          <li><a href="/service/bath-leak/">욕실배관누수</a></li>
          <li><a href="/service/water-leak/">수도누수</a></li>
          <li><a href="/service/ceiling-leak/">천장 물샘</a></li>
          <li><a href="/service/endoscope/">내시경 관로조사</a></li>
        </ul>
      </div>
      <div>
        <h4>교체·공사</h4>
        <ul>
          <li><a href="/service/faucet/">수전교체</a></li>
          <li><a href="/service/toilet-replace/">화장실변기교체</a></li>
          <li><a href="/service/basin-replace/">세면대교체</a></li>
          <li><a href="/service/plumbing/">배관설비 공사</a></li>
          <li><a href="/service/repipe/">노후 배관 교체</a></li>
          <li><a href="/service/apartment/">아파트 공용배관</a></li>
        </ul>
      </div>
      <div>
        <h4>지역</h4>
        <ul>
          <li><a href="/area/seoul/">서울</a></li>
          <li><a href="/area/gyeonggi/">경기</a></li>
          <li><a href="/area/incheon/">인천</a></li>
          <li><a href="/area/busan/">부산</a></li>
          <li><a href="/area/daegu/">대구</a></li>
          <li><a href="/area/">전국 {STAT_SIGUNGU}곳 전체</a></li>
        </ul>
      </div>
    </div>
    <div class="ft-legal">
      <div class="biz">
        <span>상호: {BRAND}</span><span>대표: {OWNER}</span>
        <span>사업자등록번호: {BIZ_NO}</span><span>기계설비공사업 등록번호: {LICENSE_NO}</span>
        <span>주소: {ADDRESS}</span><span>이메일: {EMAIL}</span>
      </div>
      <a href="/privacy/">개인정보처리방침</a> ·
      <a href="/terms/">이용약관</a> ·
      <a href="/about/editorial/">콘텐츠 작성 원칙</a> ·
      <a href="/sitemap.xml">사이트맵</a><br>
      © 2026 {BRAND}. 본 사이트의 비용 자료와 시공 기록은 자사 현장 데이터이며 무단 전재를 금합니다.
      누적 시공 {STAT_TOTAL_CASES:,}건 · 최종 검수 {REVIEWED}
    </div>
  </div>
</footer>

<a class="fab-call" href="tel:{PHONE_TEL}" aria-label="{PHONE} 전화 상담 연결">
  <span class="fab-ring" aria-hidden="true"></span>
  <span class="fab-ring d2" aria-hidden="true"></span>
  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.24 11.4 11.4 0 0 0 3.6.58 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11.4 11.4 0 0 0 .57 3.6 1 1 0 0 1-.25 1l-2.22 2.2z"/>
  </svg>
</a>

<div class="mobile-cta">
  <a href="/contact/" class="c1">견적 문의</a>
  <a href="tel:{PHONE_TEL}" class="c2">지금 전화 {PHONE}</a>
</div>

<script>
(function(){{
  var b=document.getElementById('burger'),g=document.getElementById('gnb');
  if(b&&g){{
    b.addEventListener('click',function(){{
      var open=g.classList.toggle('open');
      b.setAttribute('aria-expanded',open);
      b.setAttribute('aria-label',open?'전체 메뉴 닫기':'전체 메뉴 열기');
      document.body.style.overflow=open?'hidden':'';
    }});
    g.querySelectorAll(':scope > li > a').forEach(function(a){{
      a.addEventListener('click',function(e){{
        if(window.innerWidth>880)return;
        var li=a.parentElement;
        if(!li.querySelector('.drop'))return;
        e.preventDefault();
        var was=li.classList.contains('on');
        g.querySelectorAll('li.on').forEach(function(x){{x.classList.remove('on')}});
        if(!was)li.classList.add('on');
      }});
    }});
    document.addEventListener('keydown',function(e){{
      if(e.key==='Escape'){{
        g.classList.remove('open');b.setAttribute('aria-expanded','false');
        document.body.style.overflow='';
      }}
    }});
  }}
  // 지역 아코디언: 하나만 열리게 (INP 부담 없는 최소 스크립트)
  var regions=document.querySelectorAll('details.region');
  regions.forEach(function(d){{
    d.addEventListener('toggle',function(){{
      if(!d.open)return;
      regions.forEach(function(o){{ if(o!==d&&o.open&&o.parentElement===d.parentElement)o.open=false }});
    }});
  }});
}})();
</script>
</body>
</html>
"""
