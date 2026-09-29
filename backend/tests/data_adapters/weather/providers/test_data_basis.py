"""B2 tests: WeatherDataBasis classification.

Per docs/data/b2-open-meteo-adapter.md sections 11-13, 34 ("Data basis").
"""

from datetime import date, datetime, timezone

from app.modules.data_adapters.weather.models import TemporalPosition, WeatherDataBasis

from .helpers import json_handler, make_payload, make_request, run_provider_call


def test_previous_provider_local_date_is_archived_forecast():
    request = make_request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 10), reference_date=date(2027, 7, 10))
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    clock = lambda: datetime(2027, 7, 12, tzinfo=timezone.utc)
    result = run_provider_call(json_handler(200, payload), request, clock=clock)
    assert result.records[0].data_basis == WeatherDataBasis.ARCHIVED_FORECAST


def test_current_provider_local_date_is_live_forecast():
    request = make_request(start_date=date(2027, 7, 12), end_date=date(2027, 7, 12), reference_date=date(2027, 7, 12))
    payload = make_payload(times=["2027-07-12"], precipitation=[1.0])
    # 06:00 UTC on the 12th is ~11:30 IST on the 12th - same IST calendar day.
    clock = lambda: datetime(2027, 7, 12, 6, 0, tzinfo=timezone.utc)
    result = run_provider_call(json_handler(200, payload), request, clock=clock)
    assert result.records[0].data_basis == WeatherDataBasis.LIVE_FORECAST


def test_future_provider_local_date_is_live_forecast():
    request = make_request(start_date=date(2027, 7, 14), end_date=date(2027, 7, 14), reference_date=date(2027, 7, 12))
    payload = make_payload(times=["2027-07-14"], precipitation=[1.0])
    clock = lambda: datetime(2027, 7, 12, tzinfo=timezone.utc)
    result = run_provider_call(json_handler(200, payload), request, clock=clock)
    assert result.records[0].data_basis == WeatherDataBasis.LIVE_FORECAST


def test_data_basis_classification_independent_of_b1_reference_date():
    # Same clock, same record date, two very different reference_dates -
    # data_basis must not change.
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    clock = lambda: datetime(2027, 7, 15, tzinfo=timezone.utc)

    near_reference = make_request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 10), reference_date=date(2027, 7, 10))
    far_reference = make_request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 10), reference_date=date(2020, 1, 1))

    result_near = run_provider_call(json_handler(200, payload), near_reference, clock=clock)
    result_far = run_provider_call(json_handler(200, payload), far_reference, clock=clock)

    assert result_near.records[0].data_basis == result_far.records[0].data_basis == WeatherDataBasis.ARCHIVED_FORECAST
    # ...but TemporalPosition, owned by B1, does change with reference_date:
    assert result_near.records[0].temporal_position == TemporalPosition.CURRENT_DAY
    assert result_far.records[0].temporal_position == TemporalPosition.FUTURE


def test_future_temporal_position_can_coexist_with_archived_forecast_basis():
    # Historical replay scenario: reference_date is in the past relative to
    # the record date (-> FUTURE), but the data was actually fetched well
    # after the record date (-> ARCHIVED_FORECAST). Both are correct and
    # must not be "repaired" into a suspicious-looking pairing.
    request = make_request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 10), reference_date=date(2020, 1, 1))
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    clock = lambda: datetime(2027, 7, 15, tzinfo=timezone.utc)
    result = run_provider_call(json_handler(200, payload), request, clock=clock)
    record = result.records[0]
    assert record.temporal_position == TemporalPosition.FUTURE
    assert record.data_basis == WeatherDataBasis.ARCHIVED_FORECAST


def test_past_data_is_never_labelled_observation():
    request = make_request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 10), reference_date=date(2027, 7, 10))
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    clock = lambda: datetime(2027, 8, 1, tzinfo=timezone.utc)
    result = run_provider_call(json_handler(200, payload), request, clock=clock)
    assert result.records[0].data_basis != WeatherDataBasis.OBSERVATION


def test_clock_is_captured_exactly_once_and_shared_by_retrieved_at_and_basis():
    calls = {"count": 0}

    def counting_clock():
        calls["count"] += 1
        return datetime(2027, 7, 15, tzinfo=timezone.utc)

    request = make_request(
        start_date=date(2027, 7, 10),
        end_date=date(2027, 7, 12),
        reference_date=date(2027, 7, 12),
    )
    payload = make_payload(times=["2027-07-10", "2027-07-11", "2027-07-12"], precipitation=[1.0, 2.0, 3.0])
    result = run_provider_call(json_handler(200, payload), request, clock=counting_clock)

    assert calls["count"] == 1
    assert result.provenance.retrieved_at == datetime(2027, 7, 15, tzinfo=timezone.utc)
