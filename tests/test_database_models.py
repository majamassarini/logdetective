import datetime

import pytest

from test_helpers import (
    DatabaseFactory,
    PopulateDatabase,
)

from logdetective.server.database.models import AnalyzeRequestMetrics, EndpointType


def test_create_and_update_AnalyzeRequestMetrics():
    with DatabaseFactory().make_new_db() as session_factory:
        metrics_id = AnalyzeRequestMetrics.create(
            endpoint=EndpointType.ANALYZE,
            log_url="https://example.com/logs/123",
        )
        assert metrics_id == 1
        AnalyzeRequestMetrics.update(
            id_=metrics_id,
            response_sent_at=datetime.datetime.now(datetime.timezone.utc),
            response_length=0,
            response_certainty=37.7,
        )

        metrics = (
            session_factory()
            .query(AnalyzeRequestMetrics)
            .filter_by(id=metrics_id)
            .first()
        )

        assert metrics is not None
        assert metrics.log_url == "https://example.com/logs/123"
        assert metrics.response_length == 0
        assert metrics.response_certainty == 37.7


@pytest.mark.parametrize(
    "endpoint",
    [EndpointType.ANALYZE, EndpointType.ANALYZE_STAGED],
)
def test_AnalyzeRequestMetrics_ger_request_in_period(endpoint):
    duration = datetime.timedelta(hours=13)
    with PopulateDatabase.populate_db_and_mock_postgres(
        duration=duration,
        endpoint=endpoint,
    ) as _:
        end_time = datetime.datetime.now(datetime.timezone.utc)
        start_time = end_time - datetime.timedelta(hours=10)
        time_format = "%Y-%m-%d %H"
        counts_dict = AnalyzeRequestMetrics.get_requests_in_period(
            start_time, end_time, time_format, endpoint
        )
        assert len(counts_dict) == 10 or len(counts_dict) == 11


@pytest.mark.parametrize(
    "endpoint",
    [EndpointType.ANALYZE, EndpointType.ANALYZE_STAGED],
)
def test_AnalyzeRequestMetrics_ger_responses_average_time(endpoint):
    duration = datetime.timedelta(hours=13)
    with PopulateDatabase.populate_db_and_mock_postgres(
        duration=duration,
        endpoint=endpoint,
    ) as _:
        end_time = datetime.datetime.now(datetime.timezone.utc)
        start_time = end_time - datetime.timedelta(hours=10)
        time_format = "%Y-%m-%d %H"
        average_times_dict = AnalyzeRequestMetrics.get_responses_average_time_in_period(
            start_time, end_time, time_format, endpoint
        )
        assert len(average_times_dict) == 10 or len(average_times_dict) == 11
        values = list(average_times_dict.values())
        # responses times always increase in the same way inside the hour
        assert values[2] == pytest.approx(values[3], abs=1e-3)
        assert values[4] == pytest.approx(values[5], abs=1e-3)


@pytest.mark.parametrize(
    "endpoint",
    [EndpointType.ANALYZE, EndpointType.ANALYZE_STAGED],
)
def test_AnalyzeRequestMetrics_ger_responses_average_length(endpoint):
    duration = datetime.timedelta(hours=13)
    with PopulateDatabase.populate_db_and_mock_postgres(
        duration=duration,
        endpoint=endpoint,
    ) as _:
        end_time = datetime.datetime.now(datetime.timezone.utc)
        start_time = end_time - datetime.timedelta(hours=10)
        time_format = "%Y-%m-%d %H"
        average_lengths_dict = AnalyzeRequestMetrics.get_responses_average_length_in_period(
            start_time, end_time, time_format, endpoint
        )
        assert len(average_lengths_dict) == 10 or len(average_lengths_dict) == 11
