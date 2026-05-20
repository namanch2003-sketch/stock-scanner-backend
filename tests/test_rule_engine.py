from datetime import UTC, datetime

from app.models.candle import Candle
from app.rules.rules_config import RuleDefinition, validate_rules_config
from app.services.rule_engine import RuleEngine


def make_candle(
    *,
    symbol: str,
    timeframe: str,
    open_price: float,
    high: float,
    low: float,
    close: float,
) -> Candle:
    return Candle(
        symbol=symbol,
        timeframe=timeframe,
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=100000,
        candle_time=datetime.now(UTC),
    )


def test_price_action_buy_rule_returns_buy_signal() -> None:
    engine = RuleEngine()
    previous = make_candle(
        symbol="RELIANCE",
        timeframe="5m",
        open_price=100.0,
        high=101.8,
        low=99.7,
        close=100.9,
    )
    current = make_candle(
        symbol="RELIANCE",
        timeframe="5m",
        open_price=101.0,
        high=103.0,
        low=100.9,
        close=102.5,
    )

    signal = engine.evaluate(previous, current)

    assert signal is not None
    assert signal.signal_type == "BUY"
    assert signal.rule_name == "PRICE_ACTION_BUY"
    assert signal.rule_description == (
        "BUY when the latest candle closes above the previous candle high "
        "and the latest candle low is higher than the previous candle low."
    )
    assert signal.conditions_met == [
        "Latest close 102.50 > previous high 101.80",
        "Latest low 100.90 > previous low 99.70",
    ]


def test_price_action_exit_rule_returns_exit_signal() -> None:
    engine = RuleEngine()
    previous = make_candle(
        symbol="RELIANCE",
        timeframe="15m",
        open_price=100.5,
        high=101.5,
        low=99.2,
        close=100.2,
    )
    current = make_candle(
        symbol="RELIANCE",
        timeframe="15m",
        open_price=99.9,
        high=100.1,
        low=98.0,
        close=98.4,
    )

    signal = engine.evaluate(previous, current)

    assert signal is not None
    assert signal.signal_type == "EXIT"
    assert signal.rule_name == "PRICE_ACTION_EXIT"
    assert signal.rule_description == (
        "EXIT when the latest candle closes below the previous candle low "
        "and the latest candle high is lower than the previous candle high."
    )
    assert signal.conditions_met == [
        "Latest close 98.40 < previous low 99.20",
        "Latest high 100.10 < previous high 101.50",
    ]


def test_disabled_rule_does_not_return_signal() -> None:
    engine = RuleEngine(
        rules=(
            RuleDefinition(
                name="PRICE_ACTION_BUY",
                signal_type="BUY",
                description="Disabled buy rule",
                enabled=False,
                applicable_timeframes=("5m", "15m", "1h"),
            ),
        )
    )
    previous = make_candle(
        symbol="RELIANCE",
        timeframe="5m",
        open_price=100.0,
        high=101.8,
        low=99.7,
        close=100.9,
    )
    current = make_candle(
        symbol="RELIANCE",
        timeframe="5m",
        open_price=101.0,
        high=103.0,
        low=100.9,
        close=102.5,
    )

    signal = engine.evaluate(previous, current)

    assert signal is None


def test_rule_timeframe_applicability_is_respected() -> None:
    engine = RuleEngine(
        rules=(
            RuleDefinition(
                name="PRICE_ACTION_BUY",
                signal_type="BUY",
                description="5m and 15m only",
                enabled=True,
                applicable_timeframes=("5m", "15m"),
            ),
        )
    )
    previous = make_candle(
        symbol="RELIANCE",
        timeframe="1h",
        open_price=100.0,
        high=101.8,
        low=99.7,
        close=100.9,
    )
    current = make_candle(
        symbol="RELIANCE",
        timeframe="1h",
        open_price=101.0,
        high=103.0,
        low=100.9,
        close=102.5,
    )

    signal = engine.evaluate(previous, current)

    assert signal is None


def test_invalid_timeframe_values_raise_validation_error() -> None:
    rules = (
        RuleDefinition(
            name="BROKEN_RULE",
            signal_type="BUY",
            description="Broken timeframe config",
            enabled=True,
            applicable_timeframes=("2m",),
        ),
    )

    try:
        validate_rules_config(rules, ("5m", "15m", "1h"))
    except ValueError as exc:
        assert "BROKEN_RULE" in str(exc)
        assert "2m" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid timeframe values")
