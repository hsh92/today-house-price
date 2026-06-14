"""Use case tests with mocks."""

from today_house_price.application.housing.use_cases.fetch_and_export import (
    FetchAndExportInput,
    FetchAndExportUseCase,
)


class FakeFetcher:
    def fetch_years(
        self,
        years,
        page_size,
        delay,
        timeout,
        max_pages,
        on_progress,
        workers=1,
        year_workers=1,
    ):
        on_progress("fetching")
        assert workers == 6
        assert year_workers == 2
        return [
            {
                "RCPT_YR": "2024",
                "CGG_NM": "강남구",
                "CTRT_DAY": "20240101",
                "THING_AMT": "10000",
                "BLDG_USG": "아파트",
            }
        ]


class FakeExporter:
    def save(self, rows, output_path, korean_headers):
        return 512


def test_fetch_and_export_use_case() -> None:
    use_case = FetchAndExportUseCase(fetcher=FakeFetcher(), exporter=FakeExporter())
    params = FetchAndExportInput(
        years_back=1,
        output_path="data/out.csv",
        korean_headers=True,
        page_size=100,
        delay=0,
        timeout=10,
        max_pages=1,
        workers=6,
        year_workers=2,
    )

    result = use_case.execute(params, [2024])

    assert result.summary.total_rows == 1
    assert result.summary.file_size_bytes == 512
    assert result.target_years == (2024,)


def test_fetch_and_export_raises_when_empty() -> None:
    class EmptyFetcher:
        def fetch_years(self, *args, **kwargs):
            return []

    use_case = FetchAndExportUseCase(fetcher=EmptyFetcher(), exporter=FakeExporter())
    params = FetchAndExportInput(
        years_back=1,
        output_path="data/out.csv",
        korean_headers=False,
        page_size=100,
        delay=0,
        timeout=10,
        max_pages=None,
    )

    try:
        use_case.execute(params, [2024])
        raised = False
    except ValueError:
        raised = True

    assert raised
