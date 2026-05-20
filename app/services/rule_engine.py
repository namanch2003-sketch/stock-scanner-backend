from __future__ import annotations

from datetime import UTC, datetime

from app.models.candle import Candle
from app.models.signal import Signal
from app.rules.rules_config import RuleDefinition, VALIDATED_RULES_CONFIG


class RuleEngine:
    def __init__(self, rules: tuple[RuleDefinition, ...] = VALIDATED_RULES_CONFIG) -> None:
        self._rules = rules

    def evaluate(self, previous: Candle, current: Candle) -> Signal | None:
        for rule in self._rules:
            if not rule.enabled or current.timeframe not in rule.applicable_timeframes:
                continue

            if rule.name == "PRICE_ACTION_BUY":
                if current.close > previous.high and current.low > previous.low:
                    return self._build_signal(
                        previous=previous,
                        current=current,
                        signal_type=rule.signal_type,
                        rule_name=rule.name,
                        rule_description=rule.description,
                        conditions_met=[
                            f"Latest close {current.close:.2f} > previous high {previous.high:.2f}",
                            f"Latest low {current.low:.2f} > previous low {previous.low:.2f}",
                        ],
                    )

            if rule.name == "PRICE_ACTION_EXIT":
                if current.close < previous.low and current.high < previous.high:
                    return self._build_signal(
                        previous=previous,
                        current=current,
                        signal_type=rule.signal_type,
                        rule_name=rule.name,
                        rule_description=rule.description,
                        conditions_met=[
                            f"Latest close {current.close:.2f} < previous low {previous.low:.2f}",
                            f"Latest high {current.high:.2f} < previous high {previous.high:.2f}",
                        ],
                    )

        return None

    def _build_signal(
        self,
        previous: Candle,
        current: Candle,
        signal_type: str,
        rule_name: str,
        rule_description: str,
        conditions_met: list[str],
    ) -> Signal:
        signal_id = f"{current.symbol}_{current.timeframe}_{rule_name}_{current.candle_time.isoformat()}"
        return Signal(
            id=signal_id,
            symbol=current.symbol,
            timeframe=current.timeframe,
            signal_type=signal_type,
            trigger_price=round(current.close, 2),
            current_price=round(current.close, 2),
            rule_name=rule_name,
            triggered_at=datetime.now(UTC),
            candle_time=current.candle_time,
            previous_high=round(previous.high, 2),
            previous_low=round(previous.low, 2),
            current_high=round(current.high, 2),
            current_low=round(current.low, 2),
            current_close=round(current.close, 2),
            rule_description=rule_description,
            conditions_met=conditions_met,
            status="ACTIVE",
        )
