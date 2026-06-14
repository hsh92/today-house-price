"""실거래 CSV/API 필드 정의."""

from __future__ import annotations

from dataclasses import dataclass

CSV_COLUMNS: tuple[str, ...] = (
    "RCPT_YR",
    "CGG_CD",
    "CGG_NM",
    "STDG_CD",
    "STDG_NM",
    "LOTNO_SE",
    "LOTNO_SE_NM",
    "MNO",
    "SNO",
    "BLDG_NM",
    "CTRT_DAY",
    "THING_AMT",
    "ARCH_AREA",
    "LAND_AREA",
    "FLR",
    "RGHT_SE",
    "RTRCN_DAY",
    "ARCH_YR",
    "BLDG_USG",
    "DCLR_SE",
    "OPBIZ_RESTAGNT_SGG_NM",
)

LEGACY_FIELD_MAP: dict[str, str] = {
    "ACC_YEAR": "RCPT_YR",
    "SGG_CD": "CGG_CD",
    "SGG_NM": "CGG_NM",
    "BJDONG_CD": "STDG_CD",
    "BJDONG_NM": "STDG_NM",
    "BONBEON": "MNO",
    "BUBEON": "SNO",
    "DEAL_YMD": "CTRT_DAY",
    "OBJ_AMT": "THING_AMT",
    "BLDG_AREA": "ARCH_AREA",
    "TOT_AREA": "LAND_AREA",
    "BUILD_YEAR": "ARCH_YR",
    "HOUSE_TYPE": "BLDG_USG",
    "REQ_GBN": "DCLR_SE",
    "RDEALER_LAWDNM": "OPBIZ_RESTAGNT_SGG_NM",
}

KOREAN_HEADERS: dict[str, str] = {
    "RCPT_YR": "접수년도",
    "CGG_CD": "자치구코드",
    "CGG_NM": "자치구명",
    "STDG_CD": "법정동코드",
    "STDG_NM": "법정동명",
    "LOTNO_SE": "지번구분코드",
    "LOTNO_SE_NM": "지번구분",
    "MNO": "본번",
    "SNO": "부번",
    "BLDG_NM": "건물명",
    "CTRT_DAY": "계약일",
    "THING_AMT": "물건금액_만원",
    "ARCH_AREA": "건물면적_㎡",
    "LAND_AREA": "대지권면적_㎡",
    "FLR": "층",
    "RGHT_SE": "권리구분",
    "RTRCN_DAY": "해제사유발생일",
    "ARCH_YR": "건축년도",
    "BLDG_USG": "건물용도",
    "DCLR_SE": "신고구분",
    "OPBIZ_RESTAGNT_SGG_NM": "개업공인중개사_시군구",
}

FIELD_DESCRIPTIONS: dict[str, str] = {
    "RCPT_YR": "신고·접수 연도",
    "CGG_CD": "자치구 코드",
    "CGG_NM": "자치구 이름",
    "STDG_CD": "법정동 코드",
    "STDG_NM": "법정동 이름",
    "LOTNO_SE": "지번 구분 코드",
    "LOTNO_SE_NM": "지번 구분(대지/산 등)",
    "MNO": "지번 본번",
    "SNO": "지번 부번",
    "BLDG_NM": "건물·단지명",
    "CTRT_DAY": "계약일(YYYYMMDD)",
    "THING_AMT": "거래 금액(만원)",
    "ARCH_AREA": "건물 면적(㎡)",
    "LAND_AREA": "대지권 면적(㎡)",
    "FLR": "층",
    "RGHT_SE": "권리 구분",
    "RTRCN_DAY": "해제 사유 발생일",
    "ARCH_YR": "건축 연도",
    "BLDG_USG": "건물 용도(아파트, 오피스텔 등)",
    "DCLR_SE": "신고 구분(중개거래/직거래)",
    "OPBIZ_RESTAGNT_SGG_NM": "개업 공인중개사 소재 시군구",
}


@dataclass(frozen=True)
class FieldInfo:
    key: str
    label_ko: str
    description: str


def list_field_infos() -> tuple[FieldInfo, ...]:
    return tuple(
        FieldInfo(
            key=key,
            label_ko=KOREAN_HEADERS[key],
            description=FIELD_DESCRIPTIONS[key],
        )
        for key in CSV_COLUMNS
    )
