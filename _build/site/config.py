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
STAT_SIGUNGU = 229

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

# 이미지 슬롯 — tools/import-drive-photos.sh 가 같은 파일명으로 덮어씁니다.
IMAGES = {
    "hero":       ("field-endoscope-inspection.webp", 880, 660,
                   "스피드서원 기사가 관로 내시경 카메라로 배관 내부를 확인하는 현장"),
    "jetting":    ("hydro-jetting-sewer-line.webp", 640, 480,
                   "고압세척기로 오수관 내부 기름층을 제거하는 작업 장면"),
    "leak":       ("leak-detection-thermal.webp", 640, 480,
                   "열화상 카메라로 욕실 바닥 온수배관 누수 위치를 좁히는 장면"),
    "repipe":     ("old-galvanized-pipe-replace.webp", 640, 480,
                   "부식된 아연도강관을 절단해 교체하는 노후 배관 공사 현장"),
    "toilet":     ("toilet-clog-removal.webp", 640, 480,
                   "변기를 탈거해 배수 소켓에 걸린 이물질을 꺼내는 작업"),
    "kitchen":    ("kitchen-drain-grease.webp", 640, 480,
                   "식당 주방 배수관에 굳은 기름층을 확인한 내시경 화면"),
    "author":     ("seo-wonbae-portrait.webp", 400, 400,
                   "스피드서원 대표 서원배 현장 사진"),
    "og":         ("og-speedseowon-1200x630.webp", 1200, 630,
                   "스피드서원 전국 배관공사·하수구막힘 24시간 출장"),
}

OUTBOUND = {
    "law": ("국가법령정보센터", "https://www.law.go.kr/"),
    "molit": ("국토교통부", "https://www.molit.go.kr/"),
    "me": ("환경부", "https://www.me.go.kr/"),
    "kwwa": ("한국상하수도협회", "https://www.kwwa.or.kr/"),
    "ftc": ("공정거래위원회", "https://www.ftc.go.kr/"),
    "klac": ("대한법률구조공단", "https://www.klac.or.kr/"),
}
