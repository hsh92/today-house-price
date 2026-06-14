"""Dataset domain tests."""

from today_house_price.domain.housing.dataset import (
    filter_complete_rows,
    is_blank,
    split_train_test,
)


def _row(**overrides: str) -> dict[str, str]:
    base = {
        "RCPT_YR": "2024",
        "CGG_NM": "강남구",
        "STDG_NM": "역삼동",
        "CTRT_DAY": "20240101",
        "THING_AMT": "100000",
        "ARCH_AREA": "84.5",
        "ARCH_YR": "2010",
        "BLDG_USG": "아파트",
        "FLR": "10",
        "RTRCN_DAY": "",
        "OPBIZ_RESTAGNT_SGG_NM": "",
    }
    base.update(overrides)
    return base


def test_is_blank() -> None:
    assert is_blank("")
    assert is_blank("  ")
    assert is_blank(None)
    assert not is_blank("0")
    assert not is_blank(0)


def test_filter_complete_rows_keeps_sparse_optional_columns() -> None:
    rows = [_row(), _row(THING_AMT="")]

    kept, removed = filter_complete_rows(rows)

    assert len(kept) == 1
    assert removed == 1


def test_filter_complete_rows_strict_mode() -> None:
    rows = [_row()]

    kept, removed = filter_complete_rows(rows, strict=True)

    assert len(kept) == 0
    assert removed == 1


def test_split_train_test_is_reproducible() -> None:
    rows = [_row(THING_AMT=str(i)) for i in range(10)]

    train_a, test_a = split_train_test(rows, train_ratio=0.8, seed=7)
    train_b, test_b = split_train_test(rows, train_ratio=0.8, seed=7)

    assert len(train_a) == 8
    assert len(test_a) == 2
    assert train_a == train_b
    assert test_a == test_b


def test_split_train_test_invalid_ratio() -> None:
    try:
        split_train_test([], train_ratio=1.0)
        raised = False
    except ValueError:
        raised = True
    assert raised
