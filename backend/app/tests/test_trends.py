def test_trend_signal_growing():
    from app.services.trends.scoring import trend_signal
    result = trend_signal([
        {"year": 2021, "papers": 2},
        {"year": 2022, "papers": 3},
        {"year": 2023, "papers": 5},
        {"year": 2024, "papers": 8},
    ])
    assert result["direction"] == "growing"
    assert result["growth_rate"] > 0

def test_trend_signal_insufficient():
    from app.services.trends.scoring import trend_signal
    assert trend_signal([])["direction"] == "insufficient_data"

def test_forecast_has_uncertainty():
    from app.services.trends.scoring import forecast_signal
    result = forecast_signal([{"year": 2023, "papers": 2}, {"year": 2024, "papers": 4}])
    assert "confidence" in result
    assert "warning" in result
