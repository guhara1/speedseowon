# -*- coding: utf-8 -*-
"""전국 지역 트리 레지스트리.

구조: 시도(17) → 시군구(229) → 행정동(대표 표기)
'○○1동/2동'처럼 숫자로만 갈린 행정동은 데이터 단계에서 대표 1곳으로 통합했습니다.
"""
import re

from data_seoul import SIDO as SEOUL
from data_gyeonggi import GYEONGGI, INCHEON
from data_metro import BUSAN, DAEGU, GWANGJU, DAEJEON, ULSAN, SEJONG
from data_prov1 import GANGWON, CHUNGBUK, CHUNGNAM
from data_prov2 import JEONBUK, JEONNAM
from data_prov3 import GYEONGBUK, GYEONGNAM, JEJU, GUNWI
from data_gus import GUS

# 2023년 군위군 대구 편입 반영
DAEGU["cities"].append(GUNWI)

# 2026년 7월 1일 광주광역시 + 전라남도 통합 → 전남광주통합특별시 출범
JNGJ = {
    "slug": "jeonnam-gwangju", "name": "전남광주통합특별시", "short": "전남광주",
    "kind": "통합특별시",
    "water": ("전남광주통합특별시청 물관리 부서", "https://www.jeonnam.go.kr/"),
    "arrive": 42,
    "notice": "2026년 7월 1일 광주광역시와 전라남도가 통합해 전남광주통합특별시로 출범했습니다. "
              "관할 27개 시·군·구는 그대로 유지되며, 본 페이지는 통합시 기준입니다.",
    "geo": "무등산 도심권에서 지리산 산간, 영산강 평야, 다도해 해안까지 한 광역단체 안에 "
           "있습니다. 1986년 분리 이후 40년 만에 다시 하나가 된 구역이라 도시와 농어촌의 "
           "격차가 전국에서 가장 큰 축에 듭니다.",
    "stock": "광주 도심 5개 구는 아파트와 원도심 주택이, 전남 22개 시·군은 농어촌 단독주택과 "
             "산업도시 배후 주거가 중심입니다. 같은 통합시 안에서 주거 형태의 스펙트럼이 가장 넓습니다.",
    "note": "통합으로 행정 명칭은 바뀌었지만 배관 사정은 지역별로 그대로입니다. 광주 도심권은 "
            "상가 배수 부하와 원도심 노후관, 전남 해안은 염해 부식, 산간은 동파가 각각 중심이라 "
            "저희는 통합 이전과 동일하게 권역별 담당 기사를 유지합니다. 옛 광주광역시·전라남도 "
            "주소 그대로 접수하셔도 됩니다.",
    "cities": GWANGJU["cities"] + JEONNAM["cities"],
}
# 광주권 5개 구는 상수도 관할이 별도라 개별 표기합니다.
for _slug, _name, _prof in GWANGJU["cities"]:
    _prof["water"] = ("광주 상수도사업본부", "https://www.gwangju.go.kr/waterworks")

# 화면 노출 순서 (수도권 → 광역시 → 도)
SIDO_LIST = [
    SEOUL, GYEONGGI, INCHEON,
    BUSAN, DAEGU, DAEJEON, ULSAN, SEJONG,
    GANGWON, CHUNGBUK, CHUNGNAM, JEONBUK, JNGJ,
    GYEONGBUK, GYEONGNAM, JEJU,
]

GROUPS = [
    ("수도권", ["seoul", "gyeonggi", "incheon"]),
    ("영남권", ["busan", "daegu", "ulsan", "gyeongbuk", "gyeongnam"]),
    ("충청권", ["daejeon", "sejong", "chungbuk", "chungnam"]),
    ("호남권", ["jeonnam-gwangju", "jeonbuk"]),
    ("강원·제주", ["gangwon", "jeju"]),
]


def _dedupe_dongs(dongs):
    """'상계1동' 같은 숫자 접미 행정동을 대표 1곳으로 합칩니다."""
    seen, out = set(), []
    for d in dongs:
        base = re.sub(r"[0-9]+(가)?(동|가)$", lambda m: m.group(1) or "" + "동", d)
        base = re.sub(r"([가-힣]+?)[0-9]+동$", r"\1동", d)
        base = re.sub(r"([가-힣]+?)[0-9]+가동$", r"\1동", base)
        if base not in seen:
            seen.add(base)
            out.append(base)
    return out


def build_index():
    """slug 조회용 인덱스와 검증 결과를 만듭니다."""
    sido_by_slug, city_by_key, all_cities = {}, {}, []
    for sido in SIDO_LIST:
        sido_by_slug[sido["slug"]] = sido
        for slug, name, prof in sido["cities"]:
            gus = GUS.get((sido["slug"], slug))
            if gus:
                # 일반구 보유 시: 구 매핑이 동 목록의 원본이 됩니다.
                gus = [(g, _dedupe_dongs(ds)) for g, ds in gus]
                prof["gus"] = gus
                prof["dongs"] = [d for _, ds in gus for d in ds]
                gu_of = {d: g for g, ds in gus for d in ds}
            else:
                prof["dongs"] = _dedupe_dongs(prof["dongs"])
                gu_of = {}
            rec = {
                "slug": slug, "name": name, "prof": prof,
                "sido": sido, "gu_of": gu_of,
                "url": f"/area/{sido['slug']}/{slug}/",
            }
            city_by_key[(sido["slug"], slug)] = rec
            all_cities.append(rec)
    return sido_by_slug, city_by_key, all_cities


SIDO_BY_SLUG, CITY_BY_KEY, ALL_CITIES = build_index()


def siblings(rec, n=8):
    """같은 시도 내 형제 시군구 (자기 자신 제외, 순환 선택)."""
    fam = [c for c in rec["sido"]["cities"]]
    idx = [i for i, (s, _, _) in enumerate(fam) if s == rec["slug"]][0]
    out = []
    step = 1
    while len(out) < min(n, len(fam) - 1):
        for d in (idx + step, idx - step):
            if 0 <= d < len(fam) and fam[d][0] != rec["slug"]:
                cand = fam[d]
                if cand not in out:
                    out.append(cand)
            if len(out) >= min(n, len(fam) - 1):
                break
        step += 1
        if step > len(fam):
            break
    return out


if __name__ == "__main__":
    print("시도", len(SIDO_LIST), "· 시군구", len(ALL_CITIES))
    total_dong = sum(len(c["prof"]["dongs"]) for c in ALL_CITIES)
    print("행정동(대표 표기)", total_dong)
    for s in SIDO_LIST:
        print(f"  {s['name']:<12} {len(s['cities']):>3}")
