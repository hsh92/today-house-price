"""데이터셋 요약 콘솔 출력."""

from __future__ import annotations

from today_house_price.domain.housing.fields import list_field_infos
from today_house_price.domain.housing.summary import CountItem, DatasetSummary


def _format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def _print_count_section(title: str, items: tuple[CountItem, ...]) -> None:
    print(f"\n[{title}]")
    if not items:
        print("  (없음)")
        return
    for item in items:
        print(f"  {item.label}: {item.count:,}건")


def print_dataset_summary(summary: DatasetSummary) -> None:
    print("\n" + "=" * 60)
    print("  데이터 요약")
    print("=" * 60)
    print(f"  파일 경로    : {summary.output_path}")
    print(f"  파일 크기    : {_format_bytes(summary.file_size_bytes)}")
    print(f"  총 건수      : {summary.total_rows:,}건")
    print(f"  헤더 형식    : {'한글' if summary.korean_headers else '영문(API 키)'}")

    if summary.contract_date_min and summary.contract_date_max:
        print(f"  계약일 범위  : {summary.contract_date_min} ~ {summary.contract_date_max}")

    if summary.amount_min is not None and summary.amount_max is not None:
        avg = summary.amount_avg or 0
        print(
            f"  거래금액(만원): 최소 {summary.amount_min:,} / "
            f"최대 {summary.amount_max:,} / 평균 {avg:,.0f}"
        )

    _print_count_section("접수년도별 건수", summary.rcpt_year_counts)
    _print_count_section("계약연도별 건수", summary.contract_year_counts)
    _print_count_section("자치구 Top 10", summary.district_top)
    _print_count_section("건물용도 Top 10", summary.building_usage_top)

    print("\n[포함 데이터 항목]")
    for field in list_field_infos():
        header_note = field.label_ko if summary.korean_headers else field.key
        print(f"  - {header_note}: {field.description}")

    print("=" * 60)
