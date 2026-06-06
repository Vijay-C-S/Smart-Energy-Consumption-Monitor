from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Any

import pandas as pd


DEFAULT_RATE_PER_KWH = 8.0


@dataclass(frozen=True)
class PeakUsage:
    timestamp: str | None
    energy_consumed_kwh: float


def _normalize_readings(readings: pd.DataFrame | Iterable[Mapping[str, Any]]) -> pd.DataFrame:
    if isinstance(readings, pd.DataFrame):
        df = readings.copy()
    else:
        df = pd.DataFrame(list(readings))

    if df.empty:
        return pd.DataFrame(columns=["timestamp", "energy_consumed_kwh"])

    if "timestamp" not in df.columns:
        raise ValueError("readings must contain a 'timestamp' column")
    if "energy_consumed_kwh" not in df.columns:
        raise ValueError("readings must contain an 'energy_consumed_kwh' column")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["energy_consumed_kwh"] = pd.to_numeric(df["energy_consumed_kwh"], errors="coerce").fillna(0.0)
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
    return df


def daily_consumption(readings: pd.DataFrame | Iterable[Mapping[str, Any]]) -> pd.Series:
    df = _normalize_readings(readings)
    if df.empty:
        return pd.Series(dtype=float)
    return df.groupby(df["timestamp"].dt.date)["energy_consumed_kwh"].sum()


def weekly_consumption(readings: pd.DataFrame | Iterable[Mapping[str, Any]]) -> pd.Series:
    df = _normalize_readings(readings)
    if df.empty:
        return pd.Series(dtype=float)
    return df.groupby(df["timestamp"].dt.to_period("W"))["energy_consumed_kwh"].sum()


def monthly_consumption(readings: pd.DataFrame | Iterable[Mapping[str, Any]]) -> pd.Series:
    df = _normalize_readings(readings)
    if df.empty:
        return pd.Series(dtype=float)
    return df.groupby(df["timestamp"].dt.to_period("M"))["energy_consumed_kwh"].sum()


def average_usage(readings: pd.DataFrame | Iterable[Mapping[str, Any]]) -> float:
    df = _normalize_readings(readings)
    if df.empty:
        return 0.0
    return round(float(df["energy_consumed_kwh"].mean()), 4)


def peak_usage(readings: pd.DataFrame | Iterable[Mapping[str, Any]]) -> PeakUsage:
    df = _normalize_readings(readings)
    if df.empty:
        return PeakUsage(timestamp=None, energy_consumed_kwh=0.0)

    row = df.loc[df["energy_consumed_kwh"].idxmax()]
    return PeakUsage(timestamp=row["timestamp"].isoformat(), energy_consumed_kwh=round(float(row["energy_consumed_kwh"]), 4))


def estimated_monthly_bill(
    readings: pd.DataFrame | Iterable[Mapping[str, Any]],
    rate_per_kwh: float = DEFAULT_RATE_PER_KWH,
) -> float:
    df = _normalize_readings(readings)
    if df.empty:
        return 0.0
    total_kwh = float(df["energy_consumed_kwh"].sum())
    return round(total_kwh * rate_per_kwh, 2)


def consumption_report(
    readings: pd.DataFrame | Iterable[Mapping[str, Any]],
    rate_per_kwh: float = DEFAULT_RATE_PER_KWH,
) -> dict:
    df = _normalize_readings(readings)
    if df.empty:
        return {
            "reading_count": 0,
            "total_kwh": 0.0,
            "average_kwh": 0.0,
            "peak": PeakUsage(timestamp=None, energy_consumed_kwh=0.0).__dict__,
            "daily": {},
            "weekly": {},
            "monthly": {},
            "estimated_bill": 0.0,
        }

    daily = daily_consumption(df)
    weekly = weekly_consumption(df)
    monthly = monthly_consumption(df)
    peak = peak_usage(df)

    return {
        "reading_count": int(len(df)),
        "total_kwh": round(float(df["energy_consumed_kwh"].sum()), 4),
        "average_kwh": average_usage(df),
        "peak": peak.__dict__,
        "daily": {str(key): round(float(value), 4) for key, value in daily.items()},
        "weekly": {str(key): round(float(value), 4) for key, value in weekly.items()},
        "monthly": {str(key): round(float(value), 4) for key, value in monthly.items()},
        "estimated_bill": estimated_monthly_bill(df, rate_per_kwh=rate_per_kwh),
    }
