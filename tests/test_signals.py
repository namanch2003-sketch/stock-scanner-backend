from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.models.signal import Signal
from app.services import signal_service


def make_signal(
    *,
    signal_id: str,
    symbol: str,
    timeframe: str,
    signal_type: str,
    status: str = "ACTIVE",
    triggered_at: datetime | None = None,
) -> Signal:
    now = triggered_at or datetime.now(UTC)
    return Signal(
        id=signal_id,
        symbol=symbol,
        timeframe=timeframe,
        signal_type=signal_type,
        trigger_price=100.0,
        current_price=101.0,
        rule_name="RULE",
        triggered_at=now,
        candle_time=now,
        previous_high=99.0,
        previous_low=98.0,
        current_high=102.0,
        current_low=99.0,
        current_close=101.0,
        rule_description="Test rule description",
        conditions_met=["Condition one", "Condition two"],
        status=status,
    )


def test_signals_filters_work() -> None:
    with TestClient(app) as client:
        signal_service.clear_signals()
        signal_service.add_signal(
            make_signal(
                signal_id="RELIANCE_5m_BUY_1",
                symbol="RELIANCE",
                timeframe="5m",
                signal_type="BUY",
            )
        )
        signal_service.add_signal(
            make_signal(
                signal_id="TCS_15m_SELL_1",
                symbol="TCS",
                timeframe="15m",
                signal_type="SELL",
            )
        )
        response = client.get("/signals", params={"timeframe": "5m", "signal_type": "BUY", "symbol": "rel"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["symbol"] == "RELIANCE"
    assert payload[0]["timeframe"] == "5m"
    assert payload[0]["signal_type"] == "BUY"
    assert payload[0]["rule_description"] == "Test rule description"
    assert payload[0]["conditions_met"] == ["Condition one", "Condition two"]


def test_signals_support_status_date_and_pagination_filters() -> None:
    now = datetime.now(UTC)
    older = now - timedelta(days=3)
    oldest = now - timedelta(days=7)

    with TestClient(app) as client:
        signal_service.clear_signals()
        signal_service.add_signal(
            make_signal(
                signal_id="RELIANCE_5m_BUY_NEW",
                symbol="RELIANCE",
                timeframe="5m",
                signal_type="BUY",
                status="ACTIVE",
                triggered_at=now,
            )
        )
        signal_service.add_signal(
            make_signal(
                signal_id="TCS_15m_EXIT_OLD",
                symbol="TCS",
                timeframe="15m",
                signal_type="EXIT",
                status="CLOSED",
                triggered_at=older,
            )
        )
        signal_service.add_signal(
            make_signal(
                signal_id="INFY_1h_BUY_OLDEST",
                symbol="INFY",
                timeframe="1h",
                signal_type="BUY",
                status="ACTIVE",
                triggered_at=oldest,
            )
        )

        filtered = client.get(
            "/signals",
            params={
                "status": "ACTIVE",
                "from_date": (now - timedelta(days=5)).isoformat(),
                "limit": 1,
                "offset": 0,
            },
        )

        paged = client.get("/signals", params={"limit": 2, "offset": 1})

    assert filtered.status_code == 200
    filtered_payload = filtered.json()
    assert len(filtered_payload) == 1
    assert filtered_payload[0]["symbol"] == "RELIANCE"
    assert filtered_payload[0]["status"] == "ACTIVE"

    assert paged.status_code == 200
    paged_payload = paged.json()
    assert len(paged_payload) == 2
    assert paged_payload[0]["symbol"] == "TCS"
    assert paged_payload[1]["symbol"] == "INFY"
