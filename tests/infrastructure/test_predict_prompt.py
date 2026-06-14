"""Interactive predict prompt tests."""

from today_house_price.infrastructure.cli.predict_prompt import (
    ask_yes_no,
    collect_property_input,
    select_interactive_mode,
)


def test_select_interactive_mode() -> None:
    inputs = iter(["1"])
    mode = select_interactive_mode(input_fn=lambda _: next(inputs), output_fn=lambda _: None)
    assert mode == 1


def test_collect_property_input_with_choices() -> None:
    inputs = iter(["1", "1", "84.5", "2010", "10", "20260601"])
    row = collect_property_input(input_fn=lambda _: next(inputs), output_fn=lambda _: None)

    assert row["CGG_NM"] == "강남구"
    assert row["BLDG_USG"] == "아파트"
    assert row["ARCH_AREA"] == "84.5"
    assert row["CTRT_DAY"] == "20260601"


def test_ask_yes_no() -> None:
    assert ask_yes_no("continue", input_fn=lambda _: "y", output_fn=lambda _: None) is True
    assert ask_yes_no("continue", input_fn=lambda _: "n", output_fn=lambda _: None) is False
