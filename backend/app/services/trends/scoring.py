from __future__ import annotations

from typing import Any


def trend_signal(timeline: list[dict[str, Any]]) -> dict[str, Any]:
    if not timeline:
        return {"direction": "insufficient_data", "growth_rate": None, "confidence": 0.0}
    ordered = sorted(timeline, key=lambda x: x.get("year", 0))
    values = [float(x.get("papers", x.get("paper_count", 0))) for x in ordered]
    if len(values) < 2:
        return {"direction": "insufficient_data", "growth_rate": None, "confidence": 0.2}
    first = sum(values[:max(1, len(values)//2)])
    last = sum(values[-max(1, len(values)//2):])
    growth = (last - first) / max(1.0, first)
    direction = "growing" if growth > 0.15 else "declining" if growth < -0.15 else "stable"
    confidence = min(1.0, 0.2 + 0.1 * len(values))
    return {
        "direction": direction,
        "growth_rate": round(growth, 4),
        "confidence": round(confidence, 3),
    }


def forecast_signal(timeline: list[dict[str, Any]], horizon_years: int = 5) -> dict[str, Any]:
    signal = trend_signal(timeline)
    if signal["growth_rate"] is None:
        return {"forecast": "insufficient_data", "confidence": signal["confidence"]}
    return {
        "horizon_years": horizon_years,
        "direction": signal["direction"],
        "growth_rate": signal["growth_rate"],
        "confidence": round(max(0.0, signal["confidence"] * 0.75), 3),
        "method": "historical trend extrapolation",
        "warning": "Forecast is a corpus-derived trend signal, not a guaranteed future prediction.",
    }
