# -*- coding: utf-8 -*-
"""사이트 전역 설정값. 실제 운영 값으로 교체할 곳을 한 파일에 모았습니다."""

SITE = "https://speedseowon.netlify.app"
BRAND = "스피드서원"
OWNER = "서원배"
PHONE = "010-5183-4300"
PHONE_TEL = "01051834300"
PHONE_E164 = "+82-10-5183-4300"
EMAIL = "help@speedseowon.co.kr"
BIZ_NO = "000-00-00000"          # TODO 실제 사업자등록번호
LICENSE_NO = "제0000호"           # TODO 실제 기계설비공사업 등록번호
ADDRESS = "경기도 수원시 팔달구 ○○로 00, 3층"
FOUNDED = "2011"
REVIEWED = "2026-08-01"          # 검수일 (바이라인 표기)

# 자사 시공 데이터 — 허위 기재 리스크가 있어 한 곳에서만 관리합니다.
STAT_TOTAL_CASES = 12400         # 누적 시공
STAT_PRICE_BASE = 4180           # 비용표 산출 모수
STAT_ARRIVE_MIN = 32             # 도심 평균 도착(분)
STAT_SIGUNGU = 230

# ---------------------------------------------------------------- 색인 관련
# 각 도구에서 발급받은 값을 붙여넣으면 <head> 에 자동 삽입됩니다.
# 빈 문자열이면 해당 메타태그를 아예 출력하지 않습니다(빈 값 삽입 방지).
GOOGLE_VERIFY = ""      # Search Console → 소유권 확인 → HTML 태그 content 값
NAVER_VERIFY = "d5688487bf653f4e6ae3025c74f349c93640fdb7"   # 네이버 서치어드바이저 소유확인
BING_VERIFY = ""        # Bing Webmaster Tools (IndexNow 와 별개)
DAUM_VERIFY = ""        # 다음 검색등록 (선택)

# IndexNow — Bing·Naver·Yandex·Seznam 이 함께 쓰는 즉시 색인 통보 규격.
# 키를 바꾸면 루트의 <키>.txt 파일명도 같이 바뀝니다(빌드가 자동 처리).
INDEXNOW_KEY = "4f5b2dac712e5c2f60fa96941ccfc449d45e74d44e77d88d"

RSS_TITLE = "스피드서원 — 전국 배관공사·하수구막힘"
RSS_DESC = ("전국 230개 시·군·구 배관 출장 정보. 지역별 건물 특성과 자주 나오는 배관 문제, "
            "비용 기준, 자가진단 방법을 정리합니다.")

SERVICES = [
    ("drain-clog", "하수구막힘", "막힘"),
    ("pipe-clog", "배관막힘", "막힘"),
    ("toilet-clog", "변기막힘", "막힘"),
    ("sink-drain", "싱크대하수구막힘", "막힘"),
    ("basin-clog", "세면대막힘", "막힘"),
    ("kitchen-drain", "주방배수구막힘", "막힘"),
    ("drain-open", "배수구뚫음", "막힘"),
    ("backflow", "하수구 역류", "막힘"),
    ("leak-detection", "누수탐지", "누수"),
    ("leak-repair", "누수공사", "누수"),
    ("bath-leak", "욕실배관누수", "누수"),
    ("kitchen-leak", "주방배관누수", "누수"),
    ("water-leak", "수도누수", "누수"),
    ("water-repair", "수도수리", "누수"),
    ("ceiling-leak", "천장 물샘", "누수"),
    ("faucet", "수전교체", "교체"),
    ("toilet-replace", "화장실변기교체", "교체"),
    ("toilet-parts", "변기부속품수리", "교체"),
    ("basin-replace", "세면대교체", "교체"),
    ("trap", "배수 트랩 교체", "교체"),
    ("plumbing", "배관설비 공사", "공사"),
    ("repipe", "노후 배관 교체", "공사"),
    ("hydro-jetting", "고압세척", "공사"),
    ("endoscope", "내시경 관로조사", "공사"),
    ("debris", "이물질 제거", "공사"),
    ("commercial", "상가·식당 배관", "공사"),
    ("apartment", "아파트 공용배관", "공사"),
]
SERVICE_NAME = {s: n for s, n, _ in SERVICES}

# ---------------------------------------------------------------- 이미지 슬롯
# 고객 제공 현장사진 21장을 21개 슬롯에 1:1로 배치합니다.
# tools/make_images.py 가 원본을 슬롯 비율로 크롭해 WebP 30KB 이하로 굽습니다.
# (Netlify 빌드에서 tools/netlify-build.sh 가 드라이브 원본을 받아 자동 실행)
IMAGES = {
    # 히어로 — 지역별로 4장이 돌아가며 노출됩니다
    "hero1": ("field-endoscope-pipe-inspection.webp", 880, 660,
              "관로 내시경 카메라로 배관 내부를 확인하는 스피드서원 시공 현장"),
    "hero2": ("field-hydro-jetting-sewer.webp", 880, 660,
              "고압세척기로 오수관 내부를 세척하는 스피드서원 시공 현장"),
    "hero3": ("field-pipe-replacement-work.webp", 880, 660,
              "노후 배관을 절단해 교체하는 스피드서원 배관공사 현장"),
    "hero4": ("field-leak-detection-work.webp", 880, 660,
              "누수 탐지 장비로 급수관 누수 위치를 찾는 스피드서원 현장"),

    # 본문 작업 사진 — 지역별로 3장씩 조합이 달라집니다
    "work01": ("work-drain-clog-removal.webp", 640, 480, "하수구 막힘 관통 작업 현장"),
    "work02": ("work-sewer-line-jetting.webp", 640, 480, "오수관 고압세척으로 기름층을 제거하는 작업"),
    "work03": ("work-toilet-clog-repair.webp", 640, 480, "변기를 탈거해 배수 소켓 이물질을 꺼내는 작업"),
    "work04": ("work-kitchen-drain-grease.webp", 640, 480, "식당 주방 배수관에 굳은 기름층 제거 작업"),
    "work05": ("work-bathroom-leak-repair.webp", 640, 480, "욕실 바닥 배관 누수 부위를 보수하는 작업"),
    "work06": ("work-water-pipe-connection.webp", 640, 480, "급수 배관 이음부를 새로 연결하는 배관공사"),
    "work07": ("work-old-pipe-corrosion.webp", 640, 480, "부식이 진행된 노후 아연도강관 절단면"),
    "work08": ("work-basin-drain-service.webp", 640, 480, "세면대 배수관과 트랩을 분해해 정비하는 작업"),
    "work09": ("work-manhole-sewer-check.webp", 640, 480, "건물 앞 맨홀에서 공용 오수관 상태를 확인하는 점검"),
    "work10": ("work-faucet-replacement.webp", 640, 480, "노후 수전을 철거하고 새 수전으로 교체하는 작업"),
    "work11": ("work-pipe-endoscope-screen.webp", 640, 480, "내시경 화면으로 확인한 배관 내부 폐색 상태"),
    "work12": ("work-apartment-riser-repair.webp", 640, 480, "아파트 공용 수직배관 구간을 보수하는 작업"),

    # 시공사례 카드
    "case1": ("case-villa-sewer-backflow.webp", 640, 480, "빌라 오수관 역류 현장 고압세척 시공"),
    "case2": ("case-ceiling-leak-tracing.webp", 640, 480, "아랫집 천장 누수 원인을 추적한 욕실 배관 현장"),
    "case3": ("case-restaurant-kitchen-drain.webp", 640, 480, "식당 주방 배수관 정기 세척 시공 현장"),

    "author": ("seo-wonbae-field-portrait.webp", 400, 400,
               "스피드서원 대표 서원배 배관 시공 현장 사진"),
    "og": ("og-speedseowon-1200x630.webp", 1200, 630,
           "스피드서원 전국 배관공사·하수구막힘 24시간 출장"),
}

HEROES = ["hero1", "hero2", "hero3", "hero4"]
WORKS = [f"work{i:02d}" for i in range(1, 13)]
CASES = ["case1", "case2", "case3"]

# 구글드라이브 원본 폴더 (고객 제공 현장사진)
DRIVE_FOLDER_ID = "11dJNqXRX1jePsz_Z9G4oGOYXqrDsYhQe"

OUTBOUND = {
    "law": ("국가법령정보센터", "https://www.law.go.kr/"),
    "molit": ("국토교통부", "https://www.molit.go.kr/"),
    "me": ("환경부", "https://www.me.go.kr/"),
    "kwwa": ("한국상하수도협회", "https://www.kwwa.or.kr/"),
    "ftc": ("공정거래위원회", "https://www.ftc.go.kr/"),
    "klac": ("대한법률구조공단", "https://www.klac.or.kr/"),
}
