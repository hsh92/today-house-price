"""대화형 집값 예측 프롬프트."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

from today_house_price.domain.housing.features import describe_inference_row_errors
from today_house_price.domain.housing.prediction_options import (
    BUILDING_USAGES,
    INTERACTIVE_MODES,
    SEOUL_DISTRICTS,
)

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]


def _print_options(output: OutputFn, title: str, options: tuple[str, ...]) -> None:
    output("")
    output(title)
    for index, label in enumerate(options, start=1):
        output(f"  {index}. {label}")
    output("  0. 직접 입력")


def _read_choice(
    prompt: str,
    options: tuple[str, ...],
    input_fn: InputFn,
    output_fn: OutputFn,
    *,
    allow_custom: bool = True,
) -> str:
    while True:
        if allow_custom:
            _print_options(output_fn, prompt, options)
            raw = input_fn("번호 또는 직접 입력값: ").strip()
            if raw == "0":
                custom = input_fn("직접 입력: ").strip()
                if custom:
                    return custom
                output_fn("값을 입력해 주세요.")
                continue
        else:
            output_fn("")
            output_fn(prompt)
            for index, label in enumerate(options, start=1):
                output_fn(f"  {index}. {label}")
            raw = input_fn("번호 선택: ").strip()

        if raw.isdigit():
            choice = int(raw)
            if 1 <= choice <= len(options):
                return options[choice - 1]
        elif allow_custom and raw:
            return raw

        output_fn("올바른 번호를 선택해 주세요.")


def _read_text(prompt: str, input_fn: InputFn, output_fn: OutputFn) -> str:
    while True:
        value = input_fn(f"{prompt}: ").strip()
        if value:
            return value
        output_fn("값을 입력해 주세요.")


def _read_contract_day(input_fn: InputFn, output_fn: OutputFn) -> str:
    output_fn("")
    output_fn("계약일 입력 (YYYYMMDD, 예: 20260601)")
    today = date.today().strftime("%Y%m%d")
    output_fn(f"  Enter만 누르면 오늘({today}) 사용")
    while True:
        raw = input_fn("계약일: ").strip()
        value = raw or today
        if len(value) == 8 and value.isdigit():
            return value
        output_fn("YYYYMMDD 형식 8자리 숫자로 입력해 주세요.")


def collect_property_input(
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
) -> dict[str, str]:
    """질문·선택으로 예측 입력 dict를 수집한다."""
    output_fn("")
    output_fn("=== 매물 정보 입력 ===")

    district = _read_choice("자치구를 선택하세요.", SEOUL_DISTRICTS, input_fn, output_fn)
    usage = _read_choice("건물용도를 선택하세요.", BUILDING_USAGES, input_fn, output_fn)
    arch_area = _read_text("건물면적(㎡)", input_fn, output_fn)
    arch_yr = _read_text("건축년도(4자리)", input_fn, output_fn)
    floor = _read_text("층", input_fn, output_fn)
    ctrt_day = _read_contract_day(input_fn, output_fn)

    row = {
        "CGG_NM": district,
        "BLDG_USG": usage,
        "ARCH_AREA": arch_area,
        "ARCH_YR": arch_yr,
        "FLR": floor,
        "CTRT_DAY": ctrt_day,
    }

    reason = describe_inference_row_errors(row)
    if reason:
        raise ValueError(reason)
    return row


def select_interactive_mode(input_fn: InputFn = input, output_fn: OutputFn = print) -> int:
    """시작 메뉴 번호(1~3)를 반환한다."""
    output_fn("")
    output_fn("=== 서울 집값 예측 ===")
    choice = _read_choice(
        "실행 방식을 선택하세요.",
        INTERACTIVE_MODES,
        input_fn,
        output_fn,
        allow_custom=False,
    )
    return INTERACTIVE_MODES.index(choice) + 1


def ask_yes_no(prompt: str, input_fn: InputFn = input, output_fn: OutputFn = print) -> bool:
    while True:
        raw = input_fn(f"{prompt} (y/n): ").strip().lower()
        if raw in {"y", "yes", "예"}:
            return True
        if raw in {"n", "no", "아니오"}:
            return False
        output_fn("y 또는 n을 입력해 주세요.")


def collect_csv_paths(
    input_fn: InputFn = input, output_fn: OutputFn = print
) -> tuple[str, str, str]:
    """일괄 예측용 입력·출력·오류 로그 경로를 입력받는다."""
    output_fn("")
    output_fn("=== CSV 일괄 예측 ===")
    input_csv = _read_text("입력 CSV 경로", input_fn, output_fn)
    output_csv = _read_text("출력 CSV 경로", input_fn, output_fn)
    error_log = input_fn("오류 로그 CSV 경로 (Enter=자동): ").strip()
    return input_csv, output_csv, error_log
