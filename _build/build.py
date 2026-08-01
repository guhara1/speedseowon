#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""스피드서원 정적 사이트 생성기.

    python3 _build/build.py

출력: 저장소 루트에 index.html / area/** / sitemap*.xml / robots.txt
"""
import os
import re
import sys
from urllib.parse import quote
from datetime import date, datetime, timezone
from email.utils import format_datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "site"))

from config import (SITE, BRAND, OWNER, PHONE, PHONE_TEL, REVIEWED, IMAGES,
                    STAT_TOTAL_CASES, STAT_PRICE_BASE, STAT_ARRIVE_MIN,
                    STAT_SIGUNGU, OUTBOUND, RSS_TITLE, RSS_DESC, INDEXNOW_KEY,
                    HEROES, WORKS, CASES)
from templates import head, HEADER, FOOTER, img_tag, business_ld, ld
from regions import SIDO_LIST, ALL_CITIES, CITY_BY_KEY, GROUPS, SIDO_BY_SLUG, siblings
import hashlib

import content
import dongpage
import longtail
import data_reviews

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = date.today().isoformat()
PAGES = []          # (url, priority, changefreq, title) — 사이트맵·RSS용
DESCS = {}          # url → meta description (RSS 항목 설명으로 재사용)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def write_raw(rel, text):
    path = os.path.join(ROOT, rel.lstrip("/"))
    os.makedirs(os.path.dirname(path) or ROOT, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def write(rel, html, prio="0.6", freq="monthly"):
    write_raw(rel, html)
    url = "/" + rel.lstrip("/").replace("index.html", "")
    # title/description 은 이미 head 에 있으므로 다시 넘겨받지 않고 그대로 읽습니다.
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    d = re.search(r'<meta name="description" content="(.*?)">', html, re.S)
    PAGES.append((url, prio, freq, t.group(1) if t else BRAND))
    if d:
        DESCS[url] = d.group(1)


def snip(text, n=170):
    """문장 경계에서 잘라 '다....' 같은 어색한 말줄임을 막습니다."""
    if len(text) <= n:
        return text
    cut = text[:n]
    for mark in ("다. ", "요. ", "니다. "):
        i = cut.rfind(mark)
        if i > n * 0.45:
            return cut[:i + len(mark) - 1]
    return cut.rstrip(" .,·") + "…"


def crumb(items):
    """items: [(label, href|None)] — 마지막은 현재 페이지."""
    lis, ld_items = [], []
    for i, (label, href) in enumerate(items):
        if href:
            lis.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            lis.append(f'<li aria-current="page">{label}</li>')
        ld_items.append({"@type": "ListItem", "position": i + 1, "name": label,
                         "item": SITE + (href or "")})
    html = (f'<nav class="crumb" aria-label="현재 위치"><div class="wrap">'
            f'<ol>{"".join(lis)}</ol></div></nav>')
    return html, {"@context": "https://schema.org", "@type": "BreadcrumbList",
                  "itemListElement": ld_items}


def faq_html_and_ld(items):
    rows = "".join(
        f"<details{' open' if i == 0 else ''}><summary>{q}</summary>"
        f'<div class="a">{a}</div></details>' for i, (q, a) in enumerate(items))
    schema = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in items]}
    return f'<div class="faq">{rows}</div>', schema


def topics_html(groups):
    """롱테일 주제 링크 묶음 — 앵커는 문맥형으로 변형해 반복을 피합니다."""
    out = ""
    for title, desc, links in groups:
        items = "".join(f'<li><a href="{h}">{t}</a></li>' for t, h in links)
        out += (f'<article class="topic"><h3>{title}</h3>'
                f'<p class="t-desc">{desc}</p><ul>{items}</ul></article>')
    return f'<div class="topics">{out}</div>'


def pick(seed, pool, k=1):
    """지역마다 다른 사진이 걸리도록 slug 해시로 고릅니다(같은 지역은 항상 같은 사진)."""
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    n = len(pool)
    out, used = [], set()
    for i in range(k):
        j = (h + i * 7 + (h >> (4 * (i + 1))) % n) % n
        while j in used:
            j = (j + 1) % n
        used.add(j)
        out.append(pool[j])
    return out if k > 1 else out[0]


def gallery(keys, caps):
    """현장사진 3장 그리드. caps: [(태그, 제목, 설명)]"""
    figs = ""
    for key, (tag, title, desc) in zip(keys, caps):
        figs += (f'<figure><span class="tag">{tag}</span>'
                 f'{img_tag(key)}'
                 f'<figcaption><b>{title}</b>{desc}</figcaption></figure>')
    return f'<div class="gallery">{figs}</div>'


def stars(n):
    return "★" * int(n) + ("☆" if n - int(n) >= .5 else "") + "☆" * (5 - int(n) - (1 if n - int(n) >= .5 else 0))


def reviews_block(sido_slug=None, city_slug=None, n=3, heading="받은 평가 그대로"):
    """화면에 실제로 보이는 후기 + 그에 정확히 대응하는 스키마를 함께 만듭니다."""
    avg, total = data_reviews.aggregate()
    picked = data_reviews.for_region(sido_slug, city_slug, n)

    cards = "".join(
        f'<article class="rv" itemscope itemtype="https://schema.org/Review">'
        f'<div class="stars" aria-label="별점 5점 만점에 {r["rating"]}점">{stars(r["rating"])}</div>'
        f'<p>{r["body"]}</p>'
        f'<div class="who">{r["where"]} · {r["service"]} · {r["date"].replace("-", ".")}</div>'
        f'</article>' for r in picked)

    bar = (f'<div class="rating-bar">'
           f'<span class="score">{avg}</span>'
           f'<div><div class="stars" aria-hidden="true">{stars(avg)}</div>'
           f'<div class="meta">실제 수집 후기 <b>{total}건</b> 평균 · 5점 만점 '
           f'· <a href="/review/" style="color:var(--gray-700);text-decoration:underline">전체 보기</a></div></div>'
           f'</div>')

    schema = {
        "aggregateRating": {
            "@type": "AggregateRating", "ratingValue": str(avg),
            "reviewCount": str(total), "bestRating": "5", "worstRating": "1"},
        "review": [{
            "@type": "Review",
            "reviewRating": {"@type": "Rating", "ratingValue": str(r["rating"]),
                             "bestRating": "5", "worstRating": "1"},
            "author": {"@type": "Person", "name": f"{r['where']} 고객"},
            "datePublished": r["date"] + "-01",
            "reviewBody": r["body"],
            "itemReviewed": {"@type": "Service", "name": r["service"],
                             "provider": {"@id": f"{SITE}/#business"}},
        } for r in picked],
    }
    html = (f'<div class="sec-head"><p class="eyebrow">고객 후기</p>'
            f'<h2 class="h-sec">{heading}</h2>'
            f'<p class="lead">네이버·구글 리뷰에서 동의를 받아 옮겼습니다. '
            f'낮은 평점 후기와 저희 답변도 후기 페이지에 함께 두었습니다.</p></div>'
            f'{bar}<div class="grid g3">{cards}</div>')
    return html, schema


def byline(extra=""):
    return (f'<p style="margin-top:32px;font-size:14px;color:var(--gray-600);'
            f'border-top:1px solid var(--gray-200);padding-top:18px">'
            f'작성·검수 <strong>{OWNER}</strong> · {BRAND} 대표 / 배관기능사 · '
            f'검수일 {REVIEWED}{extra}<br>'
            f'본문의 지역 정보는 자사 출동 기록과 공개 통계를 대조해 작성했으며 분기마다 갱신합니다. '
            f'<a href="/about/editorial/" style="color:var(--gray-700);text-decoration:underline">'
            f'콘텐츠 작성·검수 원칙</a></p>')


# ============================================================ 메인 페이지
def build_home():
    faq = [
        ("하수구막힘 뚫는 비용은 보통 얼마인가요?",
         f"세면대·싱크대 단일 배관은 8만~12만원, 공용 오수관까지 내려가는 경우 15만~25만원이 중간값입니다. "
         f"고압세척 장비가 투입되면 관경과 길이에 따라 15만~40만원입니다. 출장 전 증상을 들으면 구간을 좁혀 "
         f"유선으로 범위를 안내하고, 현장에서 범위를 벗어나면 작업 전에 다시 동의를 받습니다. "
         f'→ <a href="/price/drain-clog/">하수구막힘 비용 상세</a>'),
        ("변기가 막혔는데 뚫어뻥을 써도 되나요?",
         "물이 천천히라도 내려가면 압축기로 해결될 확률이 높습니다. 다만 물이 전혀 빠지지 않고 차 있는 상태에서 "
         "화학 세정제를 붓는 것은 권하지 않습니다. 고여 있는 물에 희석돼 효과가 거의 없고, 이후 작업자가 그 물을 "
         "다뤄야 해 화상 위험이 생깁니다. 물티슈나 고체 이물질이 원인이면 압축으로 더 깊이 밀려 들어가 변기를 "
         '들어내야 하는 경우도 있습니다. → <a href="/service/toilet-clog/">변기막힘 대처법</a>'),
        ("누수탐지는 벽을 뜯지 않고도 가능한가요?",
         "가능합니다. 청음식 탐지기, 열화상 카메라, 가스 주입 방식으로 벽체를 열지 않고 위치를 특정합니다. "
         "다만 콘크리트 매립 깊이가 깊거나 상부층에서 물이 타고 내려오는 경우 오차가 생겨 최소 범위로 개구 확인이 "
         '필요할 수 있습니다. 탐지 단계에서 확률과 오차 범위를 먼저 말씀드립니다. → <a href="/service/leak-detection/">누수탐지 방식 비교</a>'),
        ("야간이나 주말에도 출장이 되나요? 할증이 붙나요?",
         f"연중무휴 24시간 접수합니다. 22시~익일 06시 야간과 공휴일에는 3만원 할증이 적용되며, 전화 접수 시점에 "
         f"할증 여부를 먼저 알려드립니다. 접수 후 통보하는 방식으로 운영하지 않습니다. 번호는 주야간 동일하게 {PHONE}입니다. "
         f'→ <a href="/price/night-surcharge/">할증 기준표</a>'),
        ("전세·월세인데 배관 수리비는 누가 내나요?",
         "통상 배관 노후나 건물 구조에서 비롯된 하자는 임대인, 세입자의 사용 과실로 인한 막힘은 세입자 부담으로 "
         "나뉩니다. 저희는 작업 전후 내시경 영상과 원인 소견서를 무상 발급해 협의 자료로 쓰실 수 있게 합니다. "
         "최종 판단은 계약 내용과 개별 사정에 따르므로 분쟁이 생기면 "
         '<a href="https://www.klac.or.kr/" target="_blank" rel="noopener">대한법률구조공단</a> 상담을 함께 권합니다. '
         '→ <a href="/guide/tenant-landlord/">수리비 부담 기준 정리</a>'),
        ("시공 후 다시 막히면 어떻게 되나요?",
         "동일 구간 동일 원인으로 재발하면 6개월 이내 무상 재시공합니다. 다른 이물질 유입 등 원인이 다른 경우는 "
         "보증 대상이 아니며, 이 구분을 위해 모든 현장에서 시공 후 내시경 영상을 남깁니다. "
         '→ <a href="/about/warranty/">보증 정책 전문</a>'),
        ("우리 동네도 출동되나요?",
         f"전국 {STAT_SIGUNGU}개 시·군·구에 기사를 배치했습니다. 시·도를 고르시면 관할 구·군이 모두 나오고, "
         f"구·군을 누르면 출동 가능한 행정동까지 확인하실 수 있습니다. "
         f'→ <a href="/area/">전국 지역 페이지</a>'),
    ]
    faq_html, faq_ld = faq_html_and_ld(faq)
    rv_html, rv_ld = reviews_block(n=3)
    topics = topics_html(longtail.home_topics())
    home_gal1 = gallery(WORKS[:3], [
        ("DRAIN", "하수구 관통", "스프링 관통기로 폐색 구간을 뚫는 작업. 관경과 재질을 먼저 봅니다."),
        ("HYDRO JET", "오수관 고압세척", "관 벽에 굳은 기름층을 물 압력으로 벗겨냅니다."),
        ("TOILET", "변기 탈거", "압축으로 안 되는 이물질은 변기를 들어내 직접 꺼냅니다."),
    ])
    home_gal2 = gallery(WORKS[3:6], [
        ("KITCHEN", "주방 배수관", "식당 유지관은 퇴적 속도가 달라 세척 주기를 따로 잡습니다."),
        ("LEAK", "욕실 누수 보수", "탐지로 위치를 좁힌 뒤 최소 범위만 열어 보수합니다."),
        ("PIPING", "급수 배관 연결", "매립 전 경로를 사진으로 남겨 다음 수리 때 덜 뜯게 합니다."),
    ])

    website = {"@context": "https://schema.org", "@type": "WebSite",
               "@id": f"{SITE}/#website", "url": SITE + "/", "name": BRAND,
               "inLanguage": "ko-KR", "publisher": {"@id": f"{SITE}/#business"}}

    # 지역 허브 미리보기
    sido_cards = ""
    for gname, slugs in GROUPS:
        blocks = ""
        for s in slugs:
            sd = SIDO_BY_SLUG[s]
            chips = "".join(
                f'<a href="/area/{sd["slug"]}/{c[0]}/">{c[1]}</a>'
                for c in sd["cities"][:7])
            more = (f'<a class="more" href="/area/{sd["slug"]}/">전체 {len(sd["cities"])}곳 →</a>')
            blocks += (
                f'<details class="region">'
                f'<summary><span class="rn">{sd["name"]}</span>'
                f'<span class="rc">{len(sd["cities"])}개 시·군·구</span>'
                f'<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                f'stroke-width="2.5" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary>'
                f'<div class="region-body">'
                f'<p class="region-desc">{snip(sd["note"],150)}</p>'
                f'<div class="chips">{chips}{more}</div></div></details>')
        sido_cards += (f'<h3 class="h-sub" style="margin:40px 0 16px">{gname}</h3>{blocks}')

    body = f"""
<main id="main">

<section class="hero">
  <div class="wrap">
    <div>
      <p class="eyebrow">전국 배관공사 · 하수구막힘</p>
      <h1 class="h-display">막힌 자리를 <em>먼저 보고</em><br>그다음에 뚫습니다.</h1>
      <p class="lead">내시경으로 관 안을 확인하고 원인을 특정한 뒤 작업합니다.
        뚫리는 데까지 걸린 시간이 아니라, 왜 막혔는지를 영상으로 남겨 드립니다.</p>
      <div class="hero-cta">
        <a href="tel:{PHONE_TEL}" class="btn btn-primary btn-lg">{PHONE} 지금 접수</a>
        <a href="/price/" class="btn btn-ghost btn-lg">비용부터 확인</a>
      </div>
      <div class="trust">
        <div><b>{STAT_ARRIVE_MIN}분</b><span>도심 평균 도착</span></div>
        <div><b>15년</b><span>현장 누적</span></div>
        <div><b>6개월</b><span>동일 원인 재발 보증</span></div>
        <div><b>{STAT_SIGUNGU}곳</b><span>출동 가능 시·군·구</span></div>
      </div>
    </div>

    <div class="hero-media">
      <figure class="shot">
        <span class="shot-tag">FIELD RECORD</span>
        {img_tag('hero1', priority=True)}
        <figcaption><b>내시경 관로조사</b>뚫기 전에 관 안을 먼저 봅니다. 이물질인지, 관이 꺼졌는지, 기름이 굳은 건지에 따라 해법이 달라집니다.</figcaption>
      </figure>
      <div class="board" aria-label="최근 출동 기록">
        <div class="board-hd"><span>DISPATCH LOG</span><b>LIVE</b></div>
        <div class="board-body"><div class="board-track">
          {"".join(
            f'<div class="row"><span class="t">{t}</span><span class="b">{p} <i>· {s}</i></span><span class="m">{m}</span></div>'
            for t, p, s, m in [
              ("23:41","서울 강남구 역삼동","싱크대 하수구막힘","18분"),
              ("23:12","수원 영통구 매탄동","변기막힘 물티슈","26분"),
              ("22:47","부산 해운대구 좌동","욕실배관누수 탐지","41분"),
              ("21:58","인천 부평구 삼산동","배수구 역류 고압세척","55분"),
              ("20:33","대구 수성구 범어동","세면대 수전교체","22분"),
              ("19:40","성남 분당구 정자동","주방배관누수 부품교체","34분"),
              ("18:21","광주 서구 상무동","화장실변기교체","62분"),
              ("17:05","대전 유성구 노은동","배관막힘 내시경조사","37분"),
            ] * 2)}
        </div></div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">증상으로 찾기</p>
      <h2 class="h-sec">지금 어떤 상태인가요</h2>
      <p class="lead">가장 가까운 상황을 고르면 원인 후보와 예상 비용, 자가 조치로 되는 범위까지 정리된 페이지로 연결됩니다.</p>
    </div>
    <div class="sym">
      {"".join(
        f'<a href="{href}"><span class="no">SYM {i+1:02d}</span><strong>{t}</strong>'
        f'<span>{d}</span><em>→ {r}</em></a>'
        for i,(href,t,d,r) in enumerate([
          ("/guide/slow-drain/","물이 안 내려가요","세면대·싱크대·욕실 배수가 느리거나 완전히 정체된 상태","하수구막힘 · 배수구뚫음"),
          ("/service/toilet-clog/","변기가 막혔어요","물이 차오르거나 넘칠 것 같은 상태, 이물질 낙하 포함","변기막힘 · 이물질 제거"),
          ("/guide/water-meter/","수도 요금이 이상해요","수도를 다 잠갔는데 계량기 팽이가 계속 돌아가는 상태","누수탐지 · 수도누수"),
          ("/guide/wall-damp/","벽·천장에서 물이 새요","벽지 얼룩, 곰팡이, 아랫집 누수 항의를 받은 상태","욕실배관누수 · 누수공사"),
          ("/guide/backflow/","하수가 역류해요","배수구에서 물이 올라오거나 다른 곳에서 물이 넘치는 상태","배관막힘 · 고압세척"),
          ("/guide/sewer-smell/","하수구 냄새가 나요","트랩 봉수 증발이나 배관 이음부 틈이 의심되는 상태","배관설비 · 트랩 교체"),
          ("/service/faucet/","수전에서 물이 새요","손잡이 아래 물맺힘, 잠가도 똑똑 떨어지는 상태","수전교체 · 부품 수리"),
          ("/service/plumbing/","배관을 새로 해야 해요","노후 건물 리모델링, 상가 인테리어 동반 설비 공사","배관공사 · 노후배관 교체"),
        ]))}
    </div>
  </div>
</section>

<section class="bg-tint">
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">Services</p>
      <h2 class="h-sec">스피드서원이 하는 일</h2>
      <p class="lead">막힘·누수·교체·공사 네 갈래로 나눠 운영합니다. 각 항목은 장비와 작업 순서, 비용 산정 기준이 서로 다릅니다.</p>
    </div>
    <div class="grid g3">
      <article class="card">
        <h3>하수구막힘 · 배관막힘<span class="badge">MAIN</span></h3>
        <p>스프링 관통기로 뚫고 끝내지 않습니다. 관경과 기름때 두께를 보고 관통으로 될지, 고압세척이 필요한지 먼저 판단합니다. 관 자체가 주저앉은 경우는 뚫어도 한 달 안에 재발합니다.</p>
        <div class="tags"><a href="/service/drain-clog/">하수구막힘</a><a href="/service/pipe-clog/">배관막힘</a><a href="/service/sink-drain/">싱크대하수구막힘</a><a href="/service/basin-clog/">세면대막힘</a><a href="/service/hydro-jetting/">고압세척</a></div>
      </article>
      <article class="card">
        <h3>누수탐지 · 누수공사</h3>
        <p>벽을 뜯기 전에 청음·열화상·가스 주입으로 위치를 좁힙니다. 급수 누수인지 배수 누수인지, 우리 집인지 윗집인지부터 가려야 공사 범위와 비용 부담 주체가 정해집니다.</p>
        <div class="tags"><a href="/service/leak-detection/">누수탐지</a><a href="/service/leak-repair/">누수공사</a><a href="/service/bath-leak/">욕실배관누수</a><a href="/service/water-leak/">수도누수</a><a href="/service/ceiling-leak/">천장 물샘</a></div>
      </article>
      <article class="card">
        <h3>변기 · 수전 · 세면대 교체</h3>
        <p>부속만 갈면 되는 걸 본체 교체로 안내하지 않습니다. 볼탭·플로트·패킹 같은 부품 수리로 해결되는 비율이 실제로는 절반을 넘습니다. 교체가 필요하면 이유를 사진으로 설명합니다.</p>
        <div class="tags"><a href="/service/toilet-replace/">화장실변기교체</a><a href="/service/toilet-parts/">변기부속품수리</a><a href="/service/faucet/">수전교체</a><a href="/service/basin-replace/">세면대교체</a></div>
      </article>
      <article class="card">
        <h3>배관설비 공사<span class="badge">MAIN</span></h3>
        <p>노후 아연도강관 교체, 상가 인테리어 급배수 신설, 아파트 공용배관 보수까지. 도면 없이 시작하지 않고, 매립 전 사진과 배관 경로를 남겨 다음 수리 때 벽을 덜 뜯게 합니다.</p>
        <div class="tags"><a href="/service/plumbing/">배관공사</a><a href="/service/repipe/">노후 배관 교체</a><a href="/service/commercial/">상가·식당 배관</a><a href="/service/apartment/">아파트 공용배관</a></div>
      </article>
      <article class="card">
        <h3>내시경 관로조사 · 이물질 제거</h3>
        <p>관 안에 무엇이 있는지 직접 봅니다. 물티슈 덩어리인지, 기름이 굳은 건지, 나무뿌리가 들어온 건지, 관이 어긋난 건지에 따라 해법이 전혀 달라집니다.</p>
        <div class="tags"><a href="/service/endoscope/">내시경 관로조사</a><a href="/service/debris/">이물질 제거</a><a href="/service/backflow/">역류 원인 조사</a><a href="/service/inspection/">정기점검</a></div>
      </article>
      <article class="card">
        <h3>고압세척</h3>
        <p>식당 주방, 오래된 빌라 오수관처럼 관 벽에 기름과 스케일이 두껍게 붙은 현장은 관통기로 구멍만 뚫려 금방 다시 막힙니다. 물 압력으로 관 벽까지 벗겨내야 주기가 길어집니다.</p>
        <div class="tags"><a href="/service/hydro-jetting/">고압세척</a><a href="/service/kitchen-drain/">주방배수구막힘</a><a href="/price/hydro-jetting/">고압세척 비용</a></div>
      </article>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">비용 공개</p>
      <h2 class="h-sec">먼저 알려 드리는 가격</h2>
      <p class="lead">실제 시공 {STAT_PRICE_BASE:,}건의 청구 금액 분포입니다. 최저가를 뽑아 광고에 쓰지 않고 중간 구간을 그대로 적었습니다.</p>
    </div>
    <div class="tbl-wrap">
      <table class="tbl">
        <caption>단위: 원(부가세 별도) · 출장비 포함 · 야간(22~06시) 및 공휴일 3만원 할증</caption>
        <thead><tr><th scope="col">항목</th><th scope="col">기본 구간</th><th scope="col">확장 구간</th><th scope="col">구간이 올라가는 경우</th></tr></thead>
        <tbody>
          {"".join(
            f'<tr><th scope="row"><a href="{u}" style="box-shadow:inset 0 -2px 0 var(--gray-300)">{n}</a></th>'
            f'<td class="num">{b}</td><td class="num">{e}</td><td>{w}<small>{s}</small></td></tr>'
            for n,u,b,e,w,s in [
              ("하수구막힘 관통","/price/drain-clog/","80,000 ~ 120,000","150,000 ~ 250,000",
               "세대 내 단일 배관은 기본. 공용 오수관·맨홀까지 내려가면 확장","동일 라인 다른 세대도 물이 안 빠지면 공용관 문제일 확률이 높습니다"),
              ("변기막힘","/price/toilet-clog/","70,000 ~ 120,000","150,000 ~ 180,000",
               "압축·관통으로 해결되면 기본. 변기를 들어내고 이물질을 꺼내면 확장","칫솔, 수건, 아이 장난감은 대부분 탈거가 필요합니다"),
              ("누수탐지","/price/leak-detection/","150,000 ~ 200,000","250,000 ~ 300,000",
               "세대 내 급수 누수는 기본. 층간·다세대 구간 추적은 확장","탐지 후 저희가 공사까지 맡으면 탐지비 절반을 공사비에서 뺍니다"),
              ("누수공사","/price/leak-repair/","250,000 ~ 500,000","700,000 ~",
               "노출 배관 부분 보수는 기본. 매립 배관 철거·타일 복구 동반 시 확장","타일·방수 복구는 별도 견적으로 분리해 알려 드립니다"),
              ("수전교체","/price/faucet/","50,000 ~ 80,000","100,000 ~ 150,000",
               "시공비 기준. 벽붙이 수전 편심 교체, 부식 고착 해체 시 확장","수전 본체는 고객 준비 또는 실비 구매 중 선택"),
              ("화장실변기교체","/price/toilet-replace/","120,000 ~ 180,000","200,000 ~ 300,000",
               "시공비 기준. 배수 중심거리 불일치, 바닥 실리콘·수평 보정 시 확장","기존 변기 폐기 처리 포함"),
              ("고압세척","/price/hydro-jetting/","150,000 ~ 250,000","300,000 ~ 400,000",
               "세대 배관 기준. 상가·식당 유지관, 20m 이상 장거리 라인은 확장","세척 전후 내시경 영상을 함께 드립니다"),
              ("내시경 관로조사","/price/endoscope/","80,000 ~ 120,000","150,000 ~",
               "단독 조사 기준. 시공을 함께 진행하면 조사비는 청구하지 않습니다","영상 파일은 요청 시 전달합니다"),
            ])}
        </tbody>
      </table>
    </div>
    <p class="note"><strong>현장에서 금액이 바뀌는 경우</strong> — 전화로 안내한 범위를 넘어서는 작업이 필요하면 <strong>작업을 멈추고</strong> 사진과 함께 사유를 설명한 뒤 동의를 받습니다. 동의하지 않으시면 출장비 3만원만 정산하고 철수합니다. 소비자분쟁 관련 기준은 <a href="{OUTBOUND['ftc'][1]}" target="_blank" rel="noopener" class="out-link">공정거래위원회 소비자분쟁해결기준</a>을 따릅니다.</p>
  </div>
</section>

<section class="bg-ink">
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">Process</p>
      <h2 class="h-sec">접수부터 보증까지 6단계</h2>
      <p class="lead">순서를 지키는 이유는 단계마다 되돌릴 수 있는 지점을 남기기 위해서입니다.</p>
    </div>
    <div class="flow">
      {"".join(
        f'<div class="step"><span class="n">STEP {i+1:02d}</span><h3>{t}</h3><p>{d}</p></div>'
        for i,(t,d) in enumerate([
          ("전화 접수","물 빠짐 속도, 소리, 다른 배수구 상태를 묻고 원인 구간을 좁힙니다. 평균 통화 4분."),
          ("유선 견적","예상 범위와 야간 할증 여부를 접수 시점에 말씀드립니다. 도착 후 통보하지 않습니다."),
          ("출동·진단",f"도심 평균 {STAT_ARRIVE_MIN}분. 도착 후 내시경으로 관 내부를 확인하고 화면을 함께 봅니다."),
          ("확정 견적","진단 결과에 따른 최종 금액을 서면으로 제시하고 동의 후 착수합니다."),
          ("시공","양생 자재로 바닥과 가구를 먼저 보양합니다. 작업 후 원상 정리까지 포함입니다."),
          ("영상·보증","시공 후 내시경 영상과 소견서를 전달하고 동일 원인 6개월 보증을 등록합니다."),
        ]))}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">현장 사진</p>
      <h2 class="h-sec">저희가 실제로 찍은 것들</h2>
      <p class="lead">홍보용으로 연출한 사진이 아니라 작업하면서 남긴 기록입니다.
        고객 동의를 받아 공개하며, 개인을 식별할 수 있는 부분은 담지 않았습니다.</p>
    </div>
    {home_gal1}
    <div style="height:16px"></div>
    {home_gal2}
    <p class="gal-note">모든 현장에서 시공 전후 사진과 내시경 영상을 남깁니다.
      보증 처리와 임대인·세입자 협의 자료로 그대로 쓰실 수 있습니다.</p>
  </div>
</section>

<section class="bg-tint">
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">Field Records</p>
      <h2 class="h-sec">실제로 이렇게 해결했습니다</h2>
      <p class="lead">사진과 내시경 영상은 고객 동의를 받아 공개합니다. 잘 풀린 현장만 고르지 않고, 두 번 간 현장도 그대로 적습니다.</p>
    </div>
    <div class="grid g3">
      {"".join(
        f'<article class="case"><figure>{img_tag(k, alt=alt)}<span>{tag}</span></figure>'
        f'<div class="case-b"><h3>{t}</h3><p>{d}</p>'
        f'<div class="case-meta"><span>{loc}</span><span><b>{svc}</b></span><span>{dur}</span></div></div></article>'
        for k,tag,alt,t,d,loc,svc,dur in [
          ("case1","HYDRO JET","고압세척기로 빌라 공용 오수관 기름층을 제거하는 작업",
           "25년 된 빌라 오수관, 두 번 만에 잡은 역류",
           "1차에 관통기로 뚫었으나 열흘 만에 재발했습니다. 내시경으로 확인하니 관 벽 기름층이 원인이었고, 2차에 고압세척으로 재시공한 뒤 보증 처리했습니다.",
           "인천 부평구","배관막힘","총 3시간"),
          ("case2","ENDOSCOPE","열화상 카메라로 욕실 하부 누수 지점을 확인하는 장면",
           "아랫집 천장 누수, 원인은 윗집 욕조 배수",
           "배관이 아니라 욕조 하부 배수 이음부 틈이었습니다. 급수 누수로 오인해 벽을 뜯을 뻔한 현장으로, 탐지 단계에서 방향을 바꿔 비용을 크게 줄였습니다.",
           "서울 노원구","욕실배관누수","총 5시간"),
          ("case3","GREASE","식당 주방 배수관 내부에 굳은 기름층 내시경 화면",
           "식당 주방 배수, 3개월마다 막히던 주기를 늘리다",
           "그리스트랩 관리 부재가 근본 원인이었습니다. 고압세척과 함께 트랩 청소 주기를 잡아 드렸고 이후 1년간 재발 신고가 없었습니다.",
           "수원 팔달구","주방배수구막힘","총 4시간"),
        ])}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">전국 출장</p>
      <h2 class="h-sec">지역을 눌러 우리 동네를 찾으세요</h2>
      <p class="lead">시·도를 누르면 관할 구·군이 펼쳐지고, 구·군을 누르면 그 지역의 건물 특성과 출동 가능한 행정동까지 정리된 페이지로 이동합니다. 지역마다 건물 연식과 배관 자재가 달라 확인 순서도 달라집니다.</p>
    </div>
    {sido_cards}
    <p style="margin-top:36px"><a href="/area/" class="btn btn-dark">전국 {STAT_SIGUNGU}개 시·군·구 전체 보기</a></p>
  </div>
</section>

<section class="bg-ink">
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">주제별로 찾기</p>
      <h2 class="h-sec">지금 상황에 맞는 문서로 바로</h2>
      <p class="lead">비용부터 볼지, 밤에 부를 곳을 찾는지, 증상 원인부터 알고 싶은지에 따라
        읽어야 할 문서가 다릅니다. 상황별로 묶어 두었습니다.</p>
    </div>
    {topics}
  </div>
</section>

<section class="bg-tint">
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">자주 묻는 질문</p>
      <h2 class="h-sec">전화하기 전에 궁금한 것들</h2>
    </div>
    {faq_html}
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">누가 쓰고 누가 시공하는가</p>
      <h2 class="h-sec">이 사이트의 내용을 책임지는 사람</h2>
    </div>
    <div class="author">
      {img_tag('author')}
      <div>
        <h3>{OWNER}</h3>
        <div class="role">{BRAND} 대표 · 현장 총괄</div>
        <div class="prose">
          <p>2011년부터 15년간 배관 현장에 있었습니다. 이 사이트의 비용표와 시공 방법 설명, 지역별 페이지는 제가 직접 작성하고 실제 시공 데이터와 대조해 분기마다 갱신합니다. 인용한 수치는 저희가 시공한 현장 기록에서 나온 것이며, 출처가 외부인 경우 링크를 답니다.</p>
        </div>
        <ul class="creds"><li>배관기능사</li><li>기계설비공사업 등록</li><li>누수탐지 실무 15년</li><li>누적 시공 {STAT_TOTAL_CASES:,}건</li></ul>
        <div class="refs"><strong>참고·근거 자료</strong> —
          {" · ".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n,u in OUTBOUND.values())}<br>
          <a href="/about/editorial/">콘텐츠 작성·검수 원칙</a> · <a href="/about/warranty/">보증 정책</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="bg-tint">
  <div class="wrap">{rv_html}</div>
</section>

<section class="final">
  <div class="wrap">
    <h2>지금 물이 안 내려가고 있다면</h2>
    <p>통화 4분이면 원인 구간과 예상 비용까지 나옵니다. 야간·주말도 같은 번호입니다.</p>
    <div class="hero-cta">
      <a href="tel:{PHONE_TEL}" class="btn btn-dark btn-lg">{PHONE} 전화 접수</a>
      <a href="/contact/" class="btn btn-line btn-lg">사진 보내고 견적받기</a>
    </div>
  </div>
</section>

</main>
"""
    html = (head(f"{BRAND} | 전국 배관공사·하수구막힘 24시간 출장 · 누수탐지 · 변기막힘",
                 "전국 24시간 배관 출장. 하수구막힘·변기막힘·누수탐지·수전교체를 내시경 관로조사와 "
                 "고압세척으로 원인부터 잡습니다. 출장 전 유선 견적, 시공 후 6개월 보증.",
                 SITE + "/", [business_ld(rv_ld), website, faq_ld])
            + HEADER + body + FOOTER)
    write("index.html", html, "1.0", "weekly")


# ======================================================== 지역 허브 /area/
def build_area_hub():
    cb, cb_ld = crumb([("홈", "/"), ("지역별 출장", None)])
    blocks = ""
    for gname, slugs in GROUPS:
        inner = ""
        for s in slugs:
            sd = SIDO_BY_SLUG[s]
            chips = "".join(f'<a href="/area/{sd["slug"]}/{c[0]}/">{c[1]}</a>' for c in sd["cities"])
            inner += (
                f'<details class="region">'
                f'<summary><span class="rn">{sd["name"]}</span>'
                f'<span class="rc">{len(sd["cities"])}개 시·군·구</span>'
                f'<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                f'stroke-width="2.5" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary>'
                f'<div class="region-body">'
                f'<p class="region-desc">{sd["geo"]}</p>'
                f'<div class="chips">{chips}'
                f'<a class="more" href="/area/{sd["slug"]}/">{sd["short"]} 지역 페이지 →</a>'
                f'</div></div></details>')
        blocks += f'<h2 class="h-sub" style="margin:44px 0 16px">{gname}</h2>{inner}'

    rv_html, rv_ld = reviews_block(n=3, heading="전국에서 받은 평가")
    itemlist = {"@context": "https://schema.org", "@type": "ItemList",
                "name": "스피드서원 전국 출장 지역",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": s["name"],
                     "url": f"{SITE}/area/{s['slug']}/"}
                    for i, s in enumerate(SIDO_LIST)]}

    body = f"""
{cb}
<main id="main">
<section style="padding-top:8px">
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">Nationwide</p>
      <h1 class="h-sec">전국 {STAT_SIGUNGU}개 시·군·구 배관 출장</h1>
      <div class="prose">
        <p>스피드서원은 17개 시·도, {STAT_SIGUNGU}개 시·군·구에 기사를 배치하고 있습니다.
        아래에서 시·도를 누르면 관할 구·군이 모두 펼쳐지고, 구·군을 누르면 그 지역의 건물 연식과 지형,
        자주 나오는 증상, 출동 가능한 행정동 목록까지 정리된 페이지로 이동합니다.</p>
        <p>지역 페이지를 따로 두는 이유는 단순합니다. 1990년대 초에 지어진 신도시 아파트와 1970년대 골목 다세대,
        해안 어촌 주택은 배관 자재도 고장 나는 방식도 서로 다릅니다. 같은 &lsquo;물이 안 내려간다&rsquo;는
        말을 들어도 어느 동네인지에 따라 먼저 확인해야 할 것이 달라집니다.
        그 순서를 지역별로 정리해 두었습니다.</p>
      </div>
    </div>
    {blocks}
    {byline()}
  </div>
</section>

<section class="bg-tint">
  <div class="wrap">{rv_html}</div>
</section>
</main>
"""
    html = (head(f"전국 지역별 배관공사·하수구막힘 출장 | {BRAND}",
                 f"전국 17개 시·도, {STAT_SIGUNGU}개 시·군·구 배관 출장 지역 안내. "
                 f"시·도를 누르면 구·군이, 구·군을 누르면 출동 가능한 행정동이 모두 나옵니다.",
                 f"{SITE}/area/", [business_ld(rv_ld), cb_ld, itemlist])
            + HEADER + body + FOOTER)
    write("area/index.html", html, "0.9", "weekly")


# ==================================================== 시·도 페이지 (17개)
def build_sido(sido):
    cb, cb_ld = crumb([("홈", "/"), ("지역별 출장", "/area/"), (sido["name"], None)])
    paras = "".join(f"<p>{t}</p>" for t in content.sido_paragraphs(sido))

    blocks = ""
    for slug, cname, prof in sido["cities"]:
        dongs = "".join(
            f'<li><a href="/area/{sido["slug"]}/{slug}/{d}/">{d}</a></li>'
            for d in prof["dongs"])
        blocks += (
            f'<details class="region">'
            f'<summary><span class="rn">{cname}</span>'
            f'<span class="rc">{len(prof["dongs"])}개 구역</span>'
            f'<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2.5" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary>'
            f'<div class="region-body">'
            f'<p class="region-desc">{snip(prof["note"],170)}</p>'
            f'<ul class="dongs">{dongs}</ul>'
            f'<p style="margin-top:18px">'
            f'<a class="btn btn-dark" href="/area/{sido["slug"]}/{slug}/" '
            f'style="min-height:46px;padding:11px 20px;font-size:15px">'
            f'{cname} 배관공사·하수구막힘 자세히 보기</a></p>'
            f'</div></details>')

    chips = "".join(f'<a href="/area/{sido["slug"]}/{c[0]}/">{c[1]}</a>' for c in sido["cities"])
    total_dong = sum(len(c[2]["dongs"]) for c in sido["cities"])
    wname, wurl = sido["water"]

    # 시·도 대표 시·군·구를 기준으로 롱테일 주제를 만들되 명칭은 시·도로 바꿉니다.
    head_rec = CITY_BY_KEY[(sido["slug"], sido["cities"][0][0])]
    groups = longtail.region_topics(head_rec)
    sido_topics = topics_html([
        (t.replace(head_rec["name"], sido["short"]),
         d.replace(head_rec["name"], sido["short"]),
         [(a.replace(head_rec["name"], sido["short"]), h) for a, h in ls])
        for t, d, ls in groups])
    rv_html, rv_ld = reviews_block(sido_slug=sido["slug"], n=3,
                                   heading=f"{sido['short']} 지역 고객이 남긴 평가")
    sido_gal = gallery(pick(sido["slug"] + "g", WORKS, 3), [
        ("FIELD", f"{sido['short']} 출동 현장", "지역마다 건물 연식이 달라 확인 순서부터 다르게 잡습니다."),
        ("FIELD", "관 내부 확인", "뚫기 전에 내시경으로 원인을 특정하고 화면을 함께 봅니다."),
        ("FIELD", "시공 후 기록", "작업 후 상태를 영상으로 남겨 보증 근거로 씁니다."),
    ])

    itemlist = {"@context": "https://schema.org", "@type": "ItemList",
                "name": f"{sido['name']} 배관 출장 지역",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": c[1],
                     "url": f"{SITE}/area/{sido['slug']}/{c[0]}/"}
                    for i, c in enumerate(sido["cities"])]}

    body = f"""
{cb}
<main id="main">
<section style="padding-top:8px">
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">{sido['short']} 지역 출장</p>
      <h1 class="h-sec">{sido['name']} 배관공사·하수구막힘 출장</h1>
      <div class="prose">{paras}</div>
    </div>

    <dl class="stat-row">
      <div><dt>관할 시·군·구</dt><dd>{len(sido['cities'])}<small>곳</small></dd></div>
      <div><dt>출동 가능 구역</dt><dd>{total_dong}<small>개 동·읍·면</small></dd></div>
      <div><dt>평균 도착</dt><dd>{sido['arrive']}<small>분 (도심 기준)</small></dd></div>
      <div><dt>접수</dt><dd>24<small>시간 연중무휴</small></dd></div>
    </dl>

    <div class="h2-block"><h2>{sido['short']} 지역 시공 현장</h2></div>
    {sido_gal}

    <div class="h2-block"><h2>{sido['name']} 시·군·구 전체</h2></div>
    <div class="chips" style="margin-bottom:28px">{chips}</div>
    <p class="lead" style="margin-bottom:24px">아래 항목을 누르면 그 지역의 출동 가능한 동·읍·면이 모두 펼쳐집니다.</p>
    {blocks}

    <div class="h2-block"><h2>{sido['name']} 상수도 문의처</h2></div>
    <div class="prose">
      <p>급수관 인입부 문제나 누수로 인한 수도요금 감면 신청은 관할 기관 소관입니다.
      세대 안쪽 배관은 개인 소유라 저희 같은 업체가 맡는 영역이고, 경계가 애매하면
      저희가 먼저 확인해 어느 쪽 소관인지 알려 드립니다. 불필요한 유상 작업을 권하지 않기 위한 절차입니다.</p>
      <p><a href="{wurl}" target="_blank" rel="noopener" class="out-link">{wname}</a></p>
    </div>

    <div class="h2-block"><h2>{sido['short']} 지역에서 가능한 작업</h2></div>
    <div class="chips">
      <a href="/service/drain-clog/">하수구막힘</a><a href="/service/pipe-clog/">배관막힘</a>
      <a href="/service/toilet-clog/">변기막힘</a><a href="/service/leak-detection/">누수탐지</a>
      <a href="/service/leak-repair/">누수공사</a><a href="/service/hydro-jetting/">고압세척</a>
      <a href="/service/plumbing/">배관설비 공사</a><a href="/service/repipe/">노후 배관 교체</a>
      <a href="/service/faucet/">수전교체</a><a href="/service/endoscope/">내시경 관로조사</a>
    </div>

    <div class="h2-block"><h2>{sido['short']} 지역에서 많이 찾는 주제</h2></div>
    {sido_topics}
    {byline()}
  </div>
</section>

<section class="bg-tint">
  <div class="wrap">{rv_html}</div>
</section>

<section class="final">
  <div class="wrap">
    <h2>{sido['short']} 어디든 접수받습니다</h2>
    <p>증상만 말씀해 주시면 원인 구간과 예상 비용을 통화로 먼저 안내드립니다.</p>
    <div class="hero-cta">
      <a href="tel:{PHONE_TEL}" class="btn btn-dark btn-lg">{PHONE} 전화 접수</a>
      <a href="/contact/" class="btn btn-line btn-lg">사진 보내고 견적받기</a>
    </div>
  </div>
</section>
</main>
"""
    html = (head(f"{sido['name']} 배관공사·하수구막힘 출장 | {len(sido['cities'])}개 시·군·구 | {BRAND}",
                 f"{sido['name']} 전 지역 24시간 배관 출장. {len(sido['cities'])}개 시·군·구 "
                 f"{total_dong}개 동·읍·면 출동. 하수구막힘·누수탐지·배관공사를 내시경 진단으로 처리합니다.",
                 f"{SITE}/area/{sido['slug']}/",
                 [business_ld(rv_ld), cb_ld, itemlist])
            + HEADER + body + FOOTER)
    write(f"area/{sido['slug']}/index.html", html, "0.8", "monthly")


# ================================================ 시·군·구 페이지 (229개)
def build_city(rec):
    p, name, sido = rec["prof"], rec["name"], rec["sido"]
    full = f"{sido['short']} {name}"
    cb, cb_ld = crumb([("홈", "/"), ("지역별 출장", "/area/"),
                       (sido["name"], f"/area/{sido['slug']}/"), (name, None)])

    lead = content.lead_paragraph(rec)
    prof_paras = "".join(f"<p>{t}</p>" for t in content.profile_paragraphs(rec))
    mix_p = content.mix_paragraph(rec)
    dong_p = content.dong_paragraph(rec)
    faq_html, faq_ld = faq_html_and_ld(content.faq_items(rec))
    topics = topics_html(longtail.region_topics(rec))
    hero_key = pick(rec["slug"] + sido["slug"], HEROES)
    gal_keys = pick(rec["slug"] + "w", WORKS, 3)
    city_gal = gallery(gal_keys, [
        ("BEFORE", f"{name} 현장 도착", f"{p['spots'].split(',')[0].strip()} 일대에서 남긴 작업 기록입니다."),
        ("DURING", "원인 확인", f"{p['mix'][0][0]} 요청이 가장 많아 그 가능성부터 확인합니다."),
        ("AFTER", "시공 마무리", "작업 후 상태를 영상으로 남기고 6개월 보증을 등록합니다."),
    ])
    wide_key = pick(rec["slug"] + "x", CASES)
    rv_html, rv_ld = reviews_block(sido_slug=sido["slug"], city_slug=rec["slug"], n=3,
                                   heading=f"{name} 인근에서 받은 평가")

    bars = "".join(
        f'<div class="bar"><span>{m}</span>'
        f'<span class="track"><span class="fill" style="width:{v*2.6}%"></span></span>'
        f'<span class="pct">{v}%</span></div>' for m, v in p["mix"])

    dongs = "".join(
        f'<li><a href="/area/{sido["slug"]}/{rec["slug"]}/{d}/">{d}</a></li>'
        for d in p["dongs"])
    sibs = "".join(f'<a href="/area/{sido["slug"]}/{s}/">{n}</a>' for s, n, _ in siblings(rec, 8))
    wname, wurl = sido["water"]
    arrive = p.get("arrive")
    arrive_txt = f"{arrive}<small>분</small>" if arrive else "선박<small> 일정</small>"

    svc_links = "".join(
        f'<a href="/service/{u}/">{name} {t}</a>' for u, t in [
            ("drain-clog", "하수구막힘"), ("pipe-clog", "배관막힘"), ("toilet-clog", "변기막힘"),
            ("leak-detection", "누수탐지"), ("leak-repair", "누수공사"),
            ("hydro-jetting", "고압세척"), ("plumbing", "배관공사"), ("faucet", "수전교체")])

    service_ld = {
        "@context": "https://schema.org", "@type": "Service",
        "serviceType": "배관공사·하수구막힘·누수탐지",
        "provider": {"@id": f"{SITE}/#business"},
        "areaServed": {"@type": "AdministrativeArea", "name": f"{sido['name']} {name}"},
        "url": SITE + rec["url"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": f"{name} 배관 서비스",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{name} {t}"}}
                for t in ("하수구막힘", "변기막힘", "누수탐지", "고압세척", "배관공사")]},
    }

    body = f"""
{cb}
<main id="main">

<section class="hero" style="padding:0">
  <div class="wrap">
    <div>
      <p class="eyebrow">{sido['name']} · {name}</p>
      <h1 class="h-display" style="font-size:clamp(30px,4.2vw,50px)">{name} 배관공사<br><em>하수구막힘</em> 24시간 출장</h1>
      <p class="lead">{lead}</p>
      <div class="hero-cta">
        <a href="tel:{PHONE_TEL}" class="btn btn-primary btn-lg">{PHONE} 지금 접수</a>
        <a href="/price/" class="btn btn-ghost btn-lg">비용 먼저 확인</a>
      </div>
      <div class="trust">
        <div><b>{arrive_txt.replace('<small>','').replace('</small>','')}</b><span>평균 도착</span></div>
        <div><b>{len(p['dongs'])}곳</b><span>출동 가능 구역</span></div>
        <div><b>6개월</b><span>재발 보증</span></div>
        <div><b>24시간</b><span>야간·주말 접수</span></div>
      </div>
    </div>
    <div class="hero-media">
      <figure class="shot">
        <span class="shot-tag">{sido['short']} {name} 현장</span>
        {img_tag(hero_key, priority=True,
                 alt=f'{sido["short"]} {name} 배관 시공 현장 — {IMAGES[hero_key][3]}')}
        <figcaption><b>{full} 출동</b>{p['spots']} 일대까지 장비를 싣고 나갑니다. 뚫기 전에 관 안을 먼저 확인합니다.</figcaption>
      </figure>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="split">
      <div>
        <div class="h2-block"><h2>{name}에서 저희가 실제로 처리하는 요청</h2></div>
        <dl class="stat-row" style="margin-bottom:28px">
          <div><dt>평균 도착</dt><dd>{arrive_txt}</dd></div>
          <div><dt>출동 가능 구역</dt><dd>{len(p['dongs'])}<small>곳</small></dd></div>
          <div><dt>가장 많은 요청</dt><dd style="font-size:19px">{p['mix'][0][0]}</dd></div>
          <div><dt>재발 보증</dt><dd>6<small>개월</small></dd></div>
        </dl>
        <div class="prose"><p>{mix_p}</p></div>
        <div class="bars">{bars}</div>

        <div class="h2-block"><h2>{name} 건물 특성과 자주 나오는 배관 문제</h2></div>
        <div class="prose">{prof_paras}</div>

        <div class="h2-block"><h2>{name} 시공 현장 사진</h2></div>
        <div class="prose"><p>{name}에서 작업하며 남긴 기록입니다. 홍보용으로 연출하지 않았고,
          고객 동의를 받아 개인을 식별할 수 있는 부분은 담지 않았습니다.</p></div>
        <div style="margin-top:22px">{city_gal}</div>
        <p class="gal-note">모든 현장에서 시공 전후 사진과 내시경 영상을 남겨 드립니다.</p>

        <div class="h2-block"><h2>{name} 출동 가능 지역</h2></div>
        <div class="prose"><p>{dong_p} 동 이름을 누르면 그 동네 전용 안내 페이지로 이동합니다.</p></div>
        <ul class="dongs" style="margin-top:20px">{dongs}</ul>

        <figure class="figure-wide">
          {img_tag(wide_key, alt=f'{sido["short"]} {name} 인근 시공 사례 — {IMAGES[wide_key][3]}')}
          <figcaption><b>{name} 인근 시공 사례</b> — {IMAGES[wide_key][3]}.
            같은 증상이라도 건물 연식과 배관 재질에 따라 작업 방식이 달라집니다.</figcaption>
        </figure>

        <div class="h2-block"><h2>{name} 상수도 관련 문의처</h2></div>
        <div class="prose">
          <p>{name}의 상수도 관할은 {wname}입니다. 계량기 이전 급수관 문제나 누수로 인한 수도요금 감면
          신청은 이쪽에서 처리합니다. 계량기 이후 세대 안쪽 배관은 개인 소유라 저희가 맡는 영역입니다.</p>
          <p>어느 쪽 소관인지 애매할 때는 저희가 먼저 확인해 알려 드립니다. 관할 기관에서 처리할 수 있는 일을
          유상 작업으로 권하지 않기 위한 절차이고, 확인만으로 끝나면 비용을 청구하지 않습니다.</p>
          <p><a href="{wurl}" target="_blank" rel="noopener" class="out-link">{wname}</a> ·
             <a href="{OUTBOUND['ftc'][1]}" target="_blank" rel="noopener" class="out-link">공정거래위원회 소비자분쟁해결기준</a></p>
        </div>

        <div class="h2-block"><h2>{name}에서 가능한 작업</h2></div>
        <div class="chips">{svc_links}</div>

        <div class="h2-block"><h2>{name} 인근 지역</h2></div>
        <div class="prose"><p>{sido['name']} 안에서 {name}과 인접한 지역입니다.
          경계에 걸친 주소는 어느 쪽이든 같은 기사가 출동하는 경우가 많아, 두 지역 페이지를 함께 참고하셔도 됩니다.</p></div>
        <div class="chips">{sibs}
          <a class="more" href="/area/{sido['slug']}/">{sido['short']} 전체 →</a></div>

        <div class="h2-block"><h2>{name}에서 많이 찾는 주제</h2></div>
        <div class="prose"><p>{name} 주민분들이 실제로 많이 검색하는 상황을 묶어 두었습니다.
          지금 필요한 항목부터 보시면 됩니다.</p></div>
        <div style="margin-top:24px">{topics}</div>

        <div class="h2-block"><h2>{name} 자주 묻는 질문</h2></div>
        {faq_html}
        {byline()}
      </div>

      <aside class="aside">
        <div class="panel dark">
          <h3>{name} 24시간 접수</h3>
          <p>증상만 말씀해 주시면 통화 4분 안에 원인 구간과 예상 비용 범위를 안내드립니다.</p>
          <a href="tel:{PHONE_TEL}" class="callnum">{PHONE}</a>
          <p style="font-size:13px">야간(22~06시)·공휴일 3만원 할증 · 접수 시 먼저 고지</p>
          <p style="margin-top:14px"><a href="/contact/" class="btn btn-primary" style="width:100%">사진 보내고 견적받기</a></p>
        </div>
        <div class="panel">
          <h3>{name} 주요 출동 구역</h3>
          <p>{p['spots']}</p>
        </div>
        <div class="panel">
          <h3>이런 증상이면 연락 주세요</h3>
          <ul>
            <li><a href="/guide/slow-drain/">물이 천천히 내려갈 때</a></li>
            <li><a href="/guide/backflow/">배수구에서 물이 올라올 때</a></li>
            <li><a href="/guide/water-meter/">계량기가 계속 돌 때</a></li>
            <li><a href="/guide/wall-damp/">벽지·천장이 젖었을 때</a></li>
            <li><a href="/guide/sewer-smell/">하수구 냄새가 올라올 때</a></li>
          </ul>
        </div>
        <div class="panel">
          <h3>비용 기준</h3>
          <ul>
            <li><a href="/price/drain-clog/">하수구막힘 8만~25만원</a></li>
            <li><a href="/price/toilet-clog/">변기막힘 7만~18만원</a></li>
            <li><a href="/price/leak-detection/">누수탐지 15만~30만원</a></li>
            <li><a href="/price/hydro-jetting/">고압세척 15만~40만원</a></li>
            <li><a href="/price/how-we-quote/">견적 산정 기준 공개</a></li>
          </ul>
        </div>
      </aside>
    </div>
  </div>
</section>

<section class="bg-tint">
  <div class="wrap">{rv_html}</div>
</section>

<section class="final">
  <div class="wrap">
    <h2>{name}, 지금 물이 안 내려간다면</h2>
    <p>야간·주말도 같은 번호입니다. 출장 전에 예상 비용부터 알려 드립니다.</p>
    <div class="hero-cta">
      <a href="tel:{PHONE_TEL}" class="btn btn-dark btn-lg">{PHONE} 전화 접수</a>
      <a href="/area/{sido['slug']}/" class="btn btn-line btn-lg">{sido['short']} 다른 지역 보기</a>
    </div>
  </div>
</section>
</main>
"""
    desc = (f"{sido['short']} {name} 배관공사·하수구막힘 24시간 출장. "
            f"{p['mix'][0][0]} 요청이 가장 많은 지역으로, {len(p['dongs'])}개 동·읍·면에 출동합니다. "
            f"내시경 진단 후 시공, 6개월 재발 보증.")
    html = (head(f"{name} 배관공사·하수구막힘 24시간 출장 | {sido['short']} | {BRAND}",
                 desc[:155], SITE + rec["url"],
                 [business_ld(rv_ld), cb_ld, service_ld, faq_ld])
            + HEADER + body + FOOTER)
    write(f"area/{sido['slug']}/{rec['slug']}/index.html", html, "0.7", "monthly")


# ============================================== 행정동 페이지 (2,800여 개)
def build_dong(rec, dong):
    p, city, sido = rec["prof"], rec["name"], rec["sido"]
    seed = sido["slug"] + rec["slug"] + dong
    kind, base = dongpage.classify(dong)
    url_path = f"area/{sido['slug']}/{rec['slug']}/{dong}/"
    canonical = f"{SITE}/area/{sido['slug']}/{rec['slug']}/{quote(dong)}/"

    cb, cb_ld = crumb([("홈", "/"), ("지역별 출장", "/area/"),
                       (sido["name"], f"/area/{sido['slug']}/"),
                       (city, f"/area/{sido['slug']}/{rec['slug']}/"), (dong, None)])

    lead_p = dongpage.lead(rec, dong)
    paras = "".join(f"<p>{t}</p>" for t in dongpage.body_paragraphs(rec, dong))
    faq_html, faq_ld = faq_html_and_ld(dongpage.faq_items(rec, dong))

    hero_key = pick(seed + "h", HEROES)
    wide_key = pick(seed + "w", WORKS)
    arrive = p.get("arrive")
    arr_txt = f"{arrive}<small>분 안팎</small>" if arrive else "선박<small> 일정 협의</small>"

    # 이웃 동: 목록상 인접 6곳 (실제 생활권 인접과 가장 가깝게)
    dongs = p["dongs"]
    idx = dongs.index(dong)
    neigh = []
    step = 1
    while len(neigh) < min(6, len(dongs) - 1):
        for j in (idx + step, idx - step):
            if 0 <= j < len(dongs) and dongs[j] != dong and dongs[j] not in neigh:
                neigh.append(dongs[j])
            if len(neigh) >= min(6, len(dongs) - 1):
                break
        step += 1
        if step > len(dongs):
            break
    neigh_html = "".join(
        f'<a href="/area/{sido["slug"]}/{rec["slug"]}/{n}/">{n}</a>' for n in neigh)

    top = p["mix"][0][0]
    svc = "".join(f'<a href="/service/{u}/">{dong} {t}</a>' for u, t in [
        ("drain-clog", "하수구막힘"), ("toilet-clog", "변기막힘"),
        ("leak-detection", "누수탐지"), ("hydro-jetting", "고압세척"),
        ("plumbing", "배관공사"), ("faucet", "수전교체")])

    service_ld = {
        "@context": "https://schema.org", "@type": "Service",
        "serviceType": "배관공사·하수구막힘·누수탐지",
        "provider": {"@id": f"{SITE}/#business"},
        "areaServed": {"@type": "AdministrativeArea",
                       "name": f"{sido['name']} {city} {dong}"},
        "url": canonical,
    }

    body = f"""
{cb}
<main id="main">
<section class="hero" style="padding:0">
  <div class="wrap" style="padding-block:clamp(36px,4.5vw,60px)">
    <div>
      <p class="eyebrow">{sido['short']} {city} · {dong}</p>
      <h1 class="h-display" style="font-size:clamp(27px,3.6vw,42px)">{dong} 하수구막힘·배관공사<br><em>24시간 출장</em></h1>
      <p class="lead">{lead_p}</p>
      <div class="hero-cta">
        <a href="tel:{PHONE_TEL}" class="btn btn-primary btn-lg">{PHONE} 지금 접수</a>
        <a href="/area/{sido['slug']}/{rec['slug']}/" class="btn btn-ghost">{city} 전체 안내</a>
      </div>
      <div class="trust">
        <div><b>{arr_txt.replace('<small>','').replace('</small>','')}</b><span>평균 도착</span></div>
        <div><b>{top}</b><span>{city} 최다 요청</span></div>
        <div><b>6개월</b><span>재발 보증</span></div>
        <div><b>24시간</b><span>야간·주말 접수</span></div>
      </div>
    </div>
    <div class="hero-media">
      <figure class="shot">
        <span class="shot-tag">{sido['short']} {city} 현장</span>
        {img_tag(hero_key, priority=True,
                 alt=f'{sido["short"]} {city} {dong} 배관 시공 현장 — {IMAGES[hero_key][3]}')}
        <figcaption><b>{dong} 출동</b>{city} 담당 기사가 장비를 싣고 나갑니다. 뚫기 전에 관 안을 먼저 확인합니다.</figcaption>
      </figure>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="split">
      <div>
        <div class="h2-block"><h2>{dong} 배관 출동 안내</h2></div>
        <div class="prose">{paras}</div>

        <figure class="figure-wide">
          {img_tag(wide_key, alt=f'{city} 인근 시공 기록 — {IMAGES[wide_key][3]}')}
          <figcaption><b>{city} 인근 시공 기록</b> — {IMAGES[wide_key][3]}.
            {dong} 현장도 같은 방식으로 전후 기록을 남깁니다.</figcaption>
        </figure>

        <div class="h2-block"><h2>{dong}에서 가능한 작업</h2></div>
        <div class="chips">{svc}</div>

        <div class="h2-block"><h2>{dong} 인근 지역</h2></div>
        <div class="prose"><p>{city} 안에서 {dong}과 붙어 있는 구역입니다.
          경계에 걸친 주소는 같은 기사가 출동하므로 어느 쪽 페이지를 보셔도 됩니다.</p></div>
        <div class="chips">{neigh_html}
          <a class="more" href="/area/{sido['slug']}/{rec['slug']}/">{city} 전체 →</a></div>

        <div class="h2-block"><h2>{dong} 자주 묻는 질문</h2></div>
        {faq_html}
        {byline()}
      </div>

      <aside class="aside">
        <div class="panel dark">
          <h3>{dong} 24시간 접수</h3>
          <p>증상만 말씀해 주시면 통화 4분 안에 원인 구간과 예상 비용 범위를 안내드립니다.</p>
          <a href="tel:{PHONE_TEL}" class="callnum">{PHONE}</a>
          <p style="font-size:13px">야간(22~06시)·공휴일 3만원 할증 · 접수 시 먼저 고지</p>
        </div>
        <div class="panel">
          <h3>{city} 함께 보기</h3>
          <ul>
            <li><a href="/area/{sido['slug']}/{rec['slug']}/">{city} 배관공사·하수구막힘</a></li>
            <li><a href="/area/{sido['slug']}/">{sido['name']} 전체 지역</a></li>
            <li><a href="/price/drain-clog/">하수구막힘 비용 기준</a></li>
            <li><a href="/guide/slow-drain/">물이 천천히 내려갈 때</a></li>
          </ul>
        </div>
      </aside>
    </div>
  </div>
</section>

<section class="final">
  <div class="wrap">
    <h2>{dong}, 지금 물이 안 내려간다면</h2>
    <p>야간·주말도 같은 번호입니다. 출장 전에 예상 비용부터 알려 드립니다.</p>
    <div class="hero-cta">
      <a href="tel:{PHONE_TEL}" class="btn btn-dark btn-lg">{PHONE} 전화 접수</a>
      <a href="/area/{sido['slug']}/{rec['slug']}/" class="btn btn-line btn-lg">{city} 다른 지역 보기</a>
    </div>
  </div>
</section>
</main>
"""
    desc = (f"{sido['short']} {city} {dong} 하수구막힘·배관공사·누수탐지 24시간 출장. "
            f"내시경 진단 후 시공, 동일 원인 6개월 보증. 야간·주말 동일 번호 접수.")
    html = (head(f"{dong} 하수구막힘·배관공사 출장 | {sido['short']} {city} | {BRAND}",
                 desc[:155], canonical,
                 [business_ld(), cb_ld, service_ld, faq_ld])
            + HEADER + body + FOOTER)
    write(url_path + "index.html", html, "0.5", "monthly")


# ================================================================ 부가 파일
def build_sitemaps():
    """사이트맵(이미지 포함) · RSS · robots.txt · IndexNow 키 파일."""
    hero_img, hero_w, hero_h, hero_alt = IMAGES["hero1"]

    def urlset(pages, with_image=False):
        rows = ""
        for u, p, f, title in pages:
            img = ""
            if with_image:
                img = (f"<image:image><image:loc>{SITE}/img/{hero_img}</image:loc>"
                       f"<image:title>{esc(title)}</image:title>"
                       f"<image:caption>{esc(hero_alt)}</image:caption></image:image>")
            rows += (f"<url><loc>{SITE}{quote(u)}</loc><lastmod>{TODAY}</lastmod>"
                     f"<changefreq>{f}</changefreq><priority>{p}</priority>{img}</url>")
        ns = ('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
              ' xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"')
        return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset {ns}>{rows}</urlset>'

    def is_dong(u):
        return u.startswith("/area/") and u.count("/") >= 5
    dong = [x for x in PAGES if is_dong(x[0])]
    area = [x for x in PAGES if x[0].startswith("/area/") and not is_dong(x[0])]
    core = [x for x in PAGES if not x[0].startswith("/area/")]

    write_raw("sitemap-area.xml", urlset(area, with_image=True))
    write_raw("sitemap-core.xml", urlset(core, with_image=True))
    write_raw("sitemap-dong.xml", urlset(dong, with_image=False))
    write_raw("sitemap.xml",
              '<?xml version="1.0" encoding="UTF-8"?>\n'
              '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
              + "".join(f"<sitemap><loc>{SITE}/{n}</loc><lastmod>{TODAY}</lastmod></sitemap>"
                        for n in ("sitemap-core.xml", "sitemap-area.xml", "sitemap-dong.xml"))
              + "</sitemapindex>")

    # ---- RSS 2.0 — 네이버 서치어드바이저 'RSS 제출' 에 그대로 넣습니다.
    pub = format_datetime(datetime.now(timezone.utc))
    items = ""
    for u, p, f, title in sorted((x for x in PAGES if not is_dong(x[0])), key=lambda x: -float(x[1])):
        items += (f"<item><title>{esc(title)}</title>"
                  f"<link>{SITE}{u}</link>"
                  f"<guid isPermaLink=\"true\">{SITE}{u}</guid>"
                  f"<description>{esc(DESCS.get(u, RSS_DESC))}</description>"
                  f"<pubDate>{pub}</pubDate></item>")
    write_raw("rss.xml",
              '<?xml version="1.0" encoding="UTF-8"?>\n'
              '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">'
              f"<channel><title>{esc(RSS_TITLE)}</title>"
              f"<link>{SITE}/</link><description>{esc(RSS_DESC)}</description>"
              f"<language>ko</language><lastBuildDate>{pub}</lastBuildDate>"
              f'<atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml"/>'
              f"{items}</channel></rss>")

    # ---- IndexNow 키 파일 (루트에 <키>.txt 로 존재해야 검증됩니다)
    write_raw(f"{INDEXNOW_KEY}.txt", INDEXNOW_KEY)

    # ---- robots.txt
    write_raw("robots.txt", f"""# {BRAND} — {SITE}
# 검색엔진별로 따로 적은 이유: 네이버 Yeti 는 크롤 지연을 명시하면 그대로 따릅니다.
# 지연을 주면 229개 지역 페이지 수집이 며칠씩 늦어져 일부러 넣지 않았습니다.

User-agent: Googlebot
Allow: /

User-agent: Googlebot-Image
Allow: /

User-agent: Yeti
Allow: /

User-agent: NaverBot
Allow: /

User-agent: Daumoa
Allow: /

User-agent: bingbot
Allow: /

User-agent: *
Allow: /
Disallow: /search/
Disallow: /*?
Disallow: /_build/
Disallow: /tools/

Sitemap: {SITE}/sitemap.xml
Sitemap: {SITE}/sitemap-core.xml
Sitemap: {SITE}/sitemap-area.xml
""")


def main():
    build_home()
    build_area_hub()
    for sido in SIDO_LIST:
        build_sido(sido)
    for rec in ALL_CITIES:
        build_city(rec)
        for dong in rec["prof"]["dongs"]:
            build_dong(rec, dong)
    build_sitemaps()

    print(f"생성 완료: {len(PAGES)}개 페이지")
    n_dong = sum(len(c["prof"]["dongs"]) for c in ALL_CITIES)
    print(f"  · 메인 1 · 허브 1 · 시·도 {len(SIDO_LIST)} · 시·군·구 {len(ALL_CITIES)} · 행정동 {n_dong}")
    print(f"  · sitemap.xml (+core/+area, 이미지 확장 포함)")
    print(f"  · rss.xml  {len(PAGES)}개 항목  — 네이버 서치어드바이저 RSS 제출용")
    print(f"  · robots.txt (Googlebot / Yeti / NaverBot / Daumoa / bingbot 개별 허용)")
    print(f"  · {INDEXNOW_KEY}.txt  — IndexNow 소유 확인 키")


if __name__ == "__main__":
    main()
