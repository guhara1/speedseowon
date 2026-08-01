# -*- coding: utf-8 -*-
"""고객 후기 데이터.

⚠️ 반드시 실제 수집분으로 교체하세요.
   구글은 화면에 보이지 않거나 실재하지 않는 리뷰를 Review/AggregateRating 스키마로
   넣는 것을 스팸 정책 위반으로 봅니다. 리치 결과 제재 대상입니다.

   - 아래 항목은 형식을 보여주기 위한 표본입니다.
   - 네이버·구글 리뷰에서 옮길 때 작성자 표기 방식(익명/이니셜)은 동의 범위 안에서 정하세요.
   - AggregateRating 은 이 목록에서 자동 계산되므로 따로 숫자를 적을 필요가 없습니다.
     (임의로 평점을 부풀리는 경로 자체를 만들지 않으려고 이렇게 했습니다)

필드
  sido      : 지역 매칭용 시도 slug
  city      : 지역 매칭용 시군구 slug (없으면 None)
  where     : 화면 표기용 지역명
  service   : 시공 항목
  date      : 작성 연월 (YYYY-MM)
  rating    : 1~5
  body      : 후기 본문
"""

REVIEWS = [
    dict(sido="seoul", city="gangdong", where="서울 강동구", service="하수구막힘",
         date="2026-06", rating=5,
         body="밤 11시에 전화했는데 30분 만에 오셨어요. 카메라로 안을 보여주면서 물티슈 때문이라고 "
              "설명해 주셔서 납득이 됐습니다. 다음부터 안 버리기로 했습니다."),
    dict(sido="gyeonggi", city="suwon", where="경기 수원시 영통구", service="변기부속품수리",
         date="2026-05", rating=5,
         body="다른 데선 전체 배관을 갈아야 한다고 했는데 여기선 부속만 바꾸면 된다고 하셔서 8만원에 "
              "끝났습니다. 굳이 안 해도 되는 걸 안 시키는 게 제일 좋았어요."),
    dict(sido="busan", city="haeundae", where="부산 해운대구", service="누수탐지",
         date="2026-04", rating=4,
         body="누수 위치 찾는 데 두 번 오셨습니다. 처음에 못 찾은 건 아쉬웠지만 추가 비용 없이 다시 와서 "
              "결국 잡아 주셨고, 아랫집 협의 자료까지 만들어 주셨어요."),
    dict(sido="seoul", city="nowon", where="서울 노원구", service="욕실배관누수",
         date="2026-06", rating=5,
         body="아랫집에서 천장 샌다고 연락이 와서 급하게 불렀습니다. 우리 집 급수 문제인 줄 알고 벽 뜯을 "
              "각오를 했는데 욕조 밑 이음부라고 하시더군요. 예상보다 훨씬 적게 들었습니다."),
    dict(sido="incheon", city="bupyeong", where="인천 부평구", service="배관막힘",
         date="2026-05", rating=4,
         body="한 번 뚫고 열흘 만에 다시 막혔는데, 보증이라고 하시면서 무료로 다시 오셨습니다. "
              "두 번째는 고압세척으로 하셨고 그 뒤로는 괜찮습니다. 처음부터 그렇게 했으면 좋았겠다 싶어요."),
    dict(sido="gyeonggi", city="seongnam", where="경기 성남시 분당구", service="노후배관 교체",
         date="2026-03", rating=5,
         body="90년대 초 아파트라 녹물이 계속 나왔습니다. 전체 교체 견적을 받았다가 여기서 내시경으로 "
              "보고 두 구간만 하면 된다고 해서 절반 이하로 끝냈습니다."),
    dict(sido="daegu", city="suseong", where="대구 수성구", service="주방배수구막힘",
         date="2026-05", rating=5,
         body="식당 하는데 주말마다 물이 안 빠져서 애를 먹었습니다. 그리스트랩 청소 주기까지 잡아 주셔서 "
              "이제 미리 관리하고 있습니다. 영업 안 끊기게 아침 일찍 와 주신 것도 고마웠어요."),
    dict(sido="daejeon", city="seo-daejeon", where="대전 서구", service="수전교체",
         date="2026-04", rating=5,
         body="수전만 갈면 되는 간단한 일인데도 바닥에 양생 깔고 하시더라고요. 끝나고 정리까지 깔끔했습니다."),
    dict(sido="gyeonggi", city="goyang", where="경기 고양시 일산서구", service="누수탐지",
         date="2026-02", rating=4,
         body="탐지 결과가 100%는 아니라고 미리 말씀해 주셨고 실제로 조금 어긋났습니다. 다만 그 범위 안이라 "
              "개구는 작게 끝났어요. 과장 없이 말해 주신 게 오히려 신뢰가 갔습니다."),
    dict(sido="gwangju", city="seo-gwangju", where="광주 서구", service="화장실변기교체",
         date="2026-06", rating=5,
         body="변기 교체하면서 배수 중심거리가 안 맞는다고 사진으로 설명해 주셨습니다. 추가 비용도 미리 "
              "말씀하시고 동의 받고 진행하셔서 기분 상할 일이 없었습니다."),
    dict(sido="gangwon", city="chuncheon", where="강원 춘천시", service="동파 수리",
         date="2026-01", rating=5,
         body="한파에 계량기가 터졌는데 다들 며칠 걸린다고 해서 포기하고 있었습니다. 당일에 와 주셨고 "
              "다른 노출 배관 보온까지 봐 주셨어요."),
    dict(sido="gyeongnam", city="changwon", where="경남 창원시 성산구", service="하수구막힘",
         date="2026-05", rating=5,
         body="전화로 물 빠지는 속도 물어보시더니 공용관 문제일 것 같다고 하셨는데 정확했습니다. "
              "관리사무소에 낼 소견서까지 써 주셔서 관리비로 처리했습니다."),
    dict(sido="jeonbuk", city="jeonju", where="전북 전주시 완산구", service="배관공사",
         date="2026-03", rating=4,
         body="한옥이라 배관이 어디로 가는지 아무도 몰랐습니다. 찾는 데 시간이 좀 걸렸고 비용도 처음 안내보다 "
              "올라갔는데, 올라가기 전에 멈추고 설명해 주셔서 수긍했습니다."),
    dict(sido="seoul", city="gwanak", where="서울 관악구", service="하수구 역류",
         date="2026-07", rating=5,
         body="장마 때 반지하 배수구에서 물이 올라왔습니다. 뚫는 것보다 역류방지밸브를 다는 게 낫다고 하셔서 "
              "그렇게 했는데 그 뒤 비 올 때 마음이 편합니다."),
]


def aggregate():
    """평점 평균과 개수를 실제 목록에서 계산합니다."""
    n = len(REVIEWS)
    avg = sum(r["rating"] for r in REVIEWS) / n
    return round(avg, 1), n


def for_region(sido_slug=None, city_slug=None, n=3):
    """지역이 일치하는 후기를 우선 배치하고 모자라면 전국 후기로 채웁니다."""
    exact = [r for r in REVIEWS if city_slug and r["city"] == city_slug]
    same_sido = [r for r in REVIEWS if sido_slug and r["sido"] == sido_slug and r not in exact]
    rest = [r for r in REVIEWS if r not in exact and r not in same_sido]
    # 지역 페이지마다 전국 후기가 같은 순서로 반복되지 않도록 회전시킵니다.
    if city_slug:
        off = sum(ord(c) for c in city_slug) % max(len(rest), 1)
        rest = rest[off:] + rest[:off]
    return (exact + same_sido + rest)[:n]
