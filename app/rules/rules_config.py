from __future__ import annotations

from dataclasses import dataclass

from app.config import settings


@dataclass(frozen=True)
class RuleDefinition:
    name: str
    signal_type: str
    description: str
    enabled: bool
    applicable_timeframes: tuple[str, ...]


RULES_CONFIG: tuple[RuleDefinition, ...] = (
    RuleDefinition(
        name="PRICE_ACTION_BUY",
        signal_type="BUY",
        description=(
            "BUY when the latest candle closes above the previous candle high "
            "and the latest candle low is higher than the previous candle low."
        ),
        enabled=True,
        applicable_timeframes=("5m", "15m", "1h"),
    ),
    RuleDefinition(
        name="PRICE_ACTION_EXIT",
        signal_type="EXIT",
        description=(
            "EXIT when the latest candle closes below the previous candle low "
            "and the latest candle high is lower than the previous candle high."
        ),
        enabled=True,
        applicable_timeframes=("5m", "15m", "1h"),
    ),
)


def validate_rules_config(
    rules: tuple[RuleDefinition, ...],
    valid_timeframes: tuple[str, ...],
) -> tuple[RuleDefinition, ...]:
    valid_timeframe_set = set(valid_timeframes)

    for rule in rules:
        invalid_timeframes = [timeframe for timeframe in rule.applicable_timeframes if timeframe not in valid_timeframe_set]
        if invalid_timeframes:
            raise ValueError(
                f"Rule '{rule.name}' contains invalid timeframe values: {', '.join(invalid_timeframes)}"
            )

    return rules


VALIDATED_RULES_CONFIG = validate_rules_config(RULES_CONFIG, settings.timeframes)
