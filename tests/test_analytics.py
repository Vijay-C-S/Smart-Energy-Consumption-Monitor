from __future__ import annotations

import pandas as pd

from app.services.analytics_service import (
    average_usage,
    consumption_report,
    daily_consumption,
    estimated_monthly_bill,
    monthly_consumption,
    peak_usage,
    weekly_consumption,
)


def _sample_readings():
    return pd.DataFrame(
        [
            {"timestamp": "2026-06-01T00:00:00Z", "energy_consumed_kwh": 1.2},
            {"timestamp": "2026-06-01T01:00:00Z", "energy_consumed_kwh": 2.3},
            {"timestamp": "2026-06-08T01:00:00Z", "energy_consumed_kwh": 3.5},
        ]
    )


def test_analytics_breakdown():
    df = _sample_readings()

    daily = daily_consumption(df)
    weekly = weekly_consumption(df)
    monthly = monthly_consumption(df)

    assert round(float(daily.iloc[0]), 2) == 3.5
    assert round(float(weekly.sum()), 2) == 7.0
    assert len(weekly) == 2
    assert round(float(monthly.iloc[0]), 2) == 7.0
    assert average_usage(df) == 2.3333
    assert peak_usage(df).energy_consumed_kwh == 3.5
    assert estimated_monthly_bill(df, rate_per_kwh=8.0) == 56.0


def test_consumption_report():
    report = consumption_report(_sample_readings(), rate_per_kwh=8.0)
    assert report["reading_count"] == 3
    assert report["total_kwh"] == 7.0
    assert report["estimated_bill"] == 56.0
    assert report["peak"]["energy_consumed_kwh"] == 3.5
