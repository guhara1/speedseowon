# -*- coding: utf-8 -*-
"""지역 페이지 본문 생성기.

핵심 원칙: 문장을 '지역명만 바꿔' 찍어내지 않습니다.
각 문단은 그 지역의 era / stock / terrain / biz / note / dongs / mix 값을
실제로 읽어 서로 다른 내용을 만듭니다. 문장 골격도 slug 해시로 분기시켜
같은 틀이 반복되지 않게 했습니다.
"""
import hashlib

from config import PHONE, STAT_ARRIVE_MIN


def _h(seed, n):
    return int(hashlib.md5(seed.encode()).hexdigest(), 16) % n


def _batchim(word):
    """마지막 글자에 받침이 있는지."""
    for ch in reversed(word):
        if "가" <= ch <= "힣":
            return (ord(ch) - 0xAC00) % 28 != 0
        if ch.isdigit():
            return ch in "0136780"
        if ch.isalpha():
            return ch.lower() in "lmnr"
    return False


def J(word, with_b, without_b):
    """조사 자동 선택: J(name,'은','는') → '강남구는' / '옹진군은'"""
    return word + (with_b if _batchim(word) else without_b)


# ---------------------------------------------------------------- 리드 문단
def lead_paragraph(rec):
    p, name, sido = rec["prof"], rec["name"], rec["sido"]
    top = p["mix"][0][0]
    arrive = p.get("arrive")
    when = (f"도심 기준 평균 {arrive}분 안에 도착합니다."
            if arrive else "도서 지역이라 선박 운항 일정에 맞춰 출동 시간을 따로 잡습니다.")
    frames = [
        f"{name}에서 가장 많이 들어오는 요청은 {top}입니다. "
        f"{p['stock']} 그래서 같은 증상이라도 {name} 안에서 원인이 갈립니다. {when}",

        f"{J(name,'은','는')} {p['terrain']} 이 지형 조건이 배수 속도와 누수 양상에 그대로 반영됩니다. "
        f"접수된 요청 중 {top} 비중이 가장 높습니다. {when}",

        f"{p['era']} 건물이 지어진 시기가 다르면 배관 자재와 관경이 다르고, "
        f"고장 나는 방식도 달라집니다. {name}에서는 {top} 요청이 가장 많습니다. {when}",
    ]
    return frames[_h(rec["slug"] + "lead", len(frames))]


# ------------------------------------------------------- 건물·지형 특성 문단
def profile_paragraphs(rec):
    p, name = rec["prof"], rec["name"]
    out = []

    a = [
        f"{name}의 주택은 한 시기에 몰려 지어지지 않았습니다. {p['era']}",
        f"먼저 건물 연식을 봅니다. {p['era']}",
        f"{name}에 출동할 때 가장 먼저 확인하는 것이 준공 시기입니다. {p['era']}",
    ][_h(rec["slug"] + "a", 3)]
    a += f" {p['stock']}"
    out.append(a)

    b = [
        f"지형도 배관에 영향을 줍니다. {p['terrain']} 배수관은 결국 중력으로 물을 내보내는 설비라, "
        f"지대가 낮거나 기울기를 충분히 못 준 구간은 이물질이 조금만 쌓여도 정체가 생깁니다.",
        f"{p['terrain']} 이 조건은 배수 구배와 하수 본관 부하에 직접 연결됩니다. "
        f"같은 양의 이물질이라도 지형에 따라 막히는 속도가 다릅니다.",
        f"{p['terrain']} 그래서 세대 안에서 원인을 못 찾을 때 건물 밖 합류 지점까지 보게 되는 경우가 있습니다.",
    ][_h(rec["slug"] + "b", 3)]
    out.append(b)

    out.append(
        f"{name}에서 사람이 모이는 곳은 {p['biz']}입니다. "
        f"상업시설이 밀집한 구역은 주거지와 배수 성격이 달라 장비와 작업 방식을 다르게 잡습니다."
    )

    # 이 지역에만 해당하는 핵심 관찰 — 페이지의 실질적 차별점
    out.append(p["note"])
    return out


# --------------------------------------------------------- 증상 구성 문단
def mix_paragraph(rec):
    p, name = rec["prof"], rec["name"]
    (m1, v1), (m2, v2), (m3, v3) = p["mix"]
    return (
        f"{name}에서 접수된 요청을 유형별로 나누면 {J(m1,'이','가')} {v1}%로 가장 많고, "
        f"{m2} {v2}%, {m3} {v3}%가 뒤를 잇습니다. "
        f"{m1} 문의가 많다는 것은 이 지역 건물과 지형이 그 방향으로 부담을 받고 있다는 뜻이라, "
        f"전화로 증상을 들을 때도 그 가능성부터 확인하고 구간을 좁힙니다."
    )


# --------------------------------------------------------- 행정동 안내 문단
def dong_paragraph(rec):
    p, name = rec["prof"], rec["name"]
    dongs = p["dongs"]
    sample = ", ".join(dongs[:6])
    return (
        f"{name} 전 지역에 출동합니다. 아래는 {len(dongs)}개 구역이며 "
        f"{sample} 등이 여기에 포함됩니다. "
        f"‘○○1동·2동’처럼 숫자로만 나뉜 곳은 대표 지명 한 곳으로 묶어 표기했으니, "
        f"세부 번호가 달라도 같은 지역으로 보시면 됩니다. "
        f"목록에 없는 신설 동이나 인접 경계 지역도 전화 주시면 출동 가능 여부를 바로 확인해 드립니다."
    )


# --------------------------------------------------------- 지역 맞춤 FAQ
def faq_items(rec):
    p, name = rec["prof"], rec["name"]
    top = p["mix"][0][0]
    arrive = p.get("arrive")
    water_name, water_url = rec["prof"].get("water") or rec["sido"]["water"]

    arrive_a = (
        f"{name} 도심 기준 평균 {arrive}분입니다. 다만 이 수치는 평균이고, "
        f"{p['terrain']} 이런 지형 조건과 시간대에 따라 편차가 생깁니다. "
        f"접수하실 때 정확한 주소를 말씀해 주시면 예상 도착 시간을 그 자리에서 알려 드리고, "
        f"늦어질 것 같으면 미리 연락드립니다."
    ) if arrive else (
        f"{J(name,'은','는')} 도서 지역이라 선박 운항 일정에 맞춰 출동합니다. "
        f"당일 왕복이 어려운 경우 작업을 하루에 몰아 처리하도록 사전에 조율합니다. "
        f"가능 여부와 예상 일정을 접수 단계에서 정확히 말씀드리며, 지킬 수 없는 약속은 하지 않습니다."
    )

    items = [
        (f"{J(name,'은','는')} 출장까지 얼마나 걸리나요?", arrive_a),
        (f"{name}에서 {top} 작업 비용은 얼마쯤 나오나요?",
         f"{J(top,'은','는')} 원인에 따라 구간이 갈립니다. 세대 내 단일 배관에서 끝나면 기본 구간, "
         f"공용관이나 건물 밖까지 내려가면 확장 구간입니다. "
         f"{J(name,'은','는')} {p['stock']} 이 조건이 어느 구간으로 갈지를 크게 좌우합니다. "
         f"전화로 증상을 들으면 대략의 범위를 먼저 안내드리고, 현장에서 그 범위를 벗어나면 "
         f"작업을 멈추고 사유를 설명한 뒤 동의를 받습니다. 동의하지 않으시면 출장비만 정산하고 철수합니다."),
        (f"{name}에서 특히 자주 나오는 문제가 있나요?", p["note"]),
        (f"{name} 상수도 관련 문의는 어디에 하나요?",
         f"관할은 {water_name}입니다. 급수관 인입부 문제나 누수로 인한 요금 감면 신청은 "
         f"이쪽에서 처리합니다. 세대 안쪽 배관은 개인 소유라 저희 같은 업체가 맡는 영역이고, "
         f"경계가 애매하면 저희가 확인해 어느 쪽 소관인지 먼저 알려 드립니다. "
         f"불필요한 유상 작업을 권하지 않기 위한 절차입니다."),
        (f"{name}도 야간이나 주말에 출동되나요?",
         f"연중무휴 24시간 접수합니다. 22시부터 익일 06시까지의 야간과 공휴일에는 3만원 할증이 붙고, "
         f"전화 접수 시점에 할증 여부를 먼저 알려 드립니다. 도착한 뒤에 통보하는 방식으로 운영하지 않습니다. "
         f"접수 번호는 주간·야간 동일하게 {PHONE}입니다."),
    ]
    return items


# ------------------------------------------------------------- 시도 페이지
def sido_paragraphs(sido):
    n = len(sido["cities"])
    unit = "개 시·군·구"
    return [
        f"{J(sido['name'],'은','는')} {n}{unit}로 나뉘고, 스피드서원은 이 전 지역에 출동합니다. "
        f"{sido['geo']}",
        f"{sido['stock']}",
        sido["note"],
        f"아래에서 구·군을 누르면 그 지역의 건물 특성, 자주 나오는 증상, "
        f"출동 가능한 행정동 목록이 정리된 페이지로 이동합니다. "
        f"어느 동네인지에 따라 확인해야 할 순서가 달라서, 지역별로 따로 정리해 두었습니다.",
    ]
