from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models


DEFAULT_HIGH_USAGE_THRESHOLD = 3.0
DEFAULT_MONTHLY_BILL_WARNING = 3000.0
DEFAULT_SPIKE_MULTIPLIER = 2.0
DEFAULT_RATE_PER_KWH = 8.0


@dataclass(frozen=True)
class AlertThresholds:
    high_usage_threshold: float = DEFAULT_HIGH_USAGE_THRESHOLD
    monthly_bill_warning: float = DEFAULT_MONTHLY_BILL_WARNING
    spike_multiplier: float = DEFAULT_SPIKE_MULTIPLIER
    rate_per_kwh: float = DEFAULT_RATE_PER_KWH


def create_alerts_for_reading(
    reading_id: int,
    thresholds: AlertThresholds = AlertThresholds(),
    db: Session | None = None,
) -> list[str]:
    """Evaluate all alert rules for a stored reading.

    Returns a list of alert types created for easier testing and logging.
    """
    owns_session = db is None
    db = db or SessionLocal()
    created_alert_types: list[str] = []
    try:
        reading = db.get(models.MeterReading, reading_id)
        if not reading:
            return created_alert_types

        meter = db.get(models.SmartMeter, reading.meter_id)
        if not meter:
            return created_alert_types

        household_id = meter.household_id
        value = float(reading.energy_consumed_kwh or 0)

        household = db.get(models.Household, household_id)
        daily_limit = float(household.daily_kwh_threshold) if household else 20.0
        household_name = household.customer_name if household else f"Household {household_id}"

        if value > thresholds.high_usage_threshold:
            _create_alert(
                db,
                household_id=household_id,
                meter_id=reading.meter_id,
                alert_type="HIGH_USAGE",
                message=(
                    f"{household_name} consumed {value:.4f} kWh in a single reading, "
                    f"exceeding the {thresholds.high_usage_threshold:g} kWh threshold."
                ),
                severity="HIGH",
            )
            created_alert_types.append("HIGH_USAGE")

        avg_value = _get_average_usage(db, reading.meter_id, exclude_reading_id=reading.reading_id)
        if avg_value and value > (thresholds.spike_multiplier * avg_value):
            _create_alert(
                db,
                household_id=household_id,
                meter_id=reading.meter_id,
                alert_type="SPIKE_DETECTED",
                message=(
                    f"{household_name} reading spiked to {value:.4f} kWh, "
                    f"more than {thresholds.spike_multiplier:g}x their average of {avg_value:.4f} kWh."
                ),
                severity="MEDIUM",
            )
            created_alert_types.append("SPIKE_DETECTED")

        daily_total = _get_daily_total(db, household_id, reading.timestamp)
        if daily_total > daily_limit:
            _create_alert(
                db,
                household_id=household_id,
                meter_id=reading.meter_id,
                alert_type="DAILY_LIMIT_EXCEEDED",
                message=(
                    f"{household_name} daily usage reached {daily_total:.4f} kWh, "
                    f"exceeding their limit of {daily_limit:g} kWh."
                ),
                severity="HIGH",
            )
            created_alert_types.append("DAILY_LIMIT_EXCEEDED")

        monthly_total = _get_monthly_total(db, household_id, reading.timestamp)
        estimated_bill = round(monthly_total * thresholds.rate_per_kwh, 2)
        if estimated_bill > thresholds.monthly_bill_warning:
            _create_alert(
                db,
                household_id=household_id,
                meter_id=reading.meter_id,
                alert_type="MONTHLY_BILL_WARNING",
                message=(
                    f"{household_name} estimated monthly bill reached ₹{estimated_bill:.2f}, "
                    f"exceeding the warning threshold of ₹{thresholds.monthly_bill_warning:.2f}."
                ),
                severity="MEDIUM",
            )
            created_alert_types.append("MONTHLY_BILL_WARNING")

        return created_alert_types
    finally:
        if owns_session:
            db.close()



def _create_alert(db, household_id, meter_id, alert_type, message, severity):
    existing = db.scalar(
        select(models.Alert).where(
            models.Alert.household_id == household_id,
            models.Alert.meter_id == meter_id,
            models.Alert.alert_type == alert_type,
            models.Alert.status == "OPEN",
            models.Alert.message == message,
        )
    )
    if existing:
        return existing

    alert = models.Alert(
        household_id=household_id,
        meter_id=meter_id,
        alert_type=alert_type,
        message=message,
        severity=severity,
        status="OPEN",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def _get_average_usage(db, meter_id: int, exclude_reading_id: int | None = None) -> float:
    q = select(models.MeterReading.energy_consumed_kwh).where(models.MeterReading.meter_id == meter_id)
    if exclude_reading_id is not None:
        q = q.where(models.MeterReading.reading_id != exclude_reading_id)
    readings = db.scalars(q).all()
    if not readings:
        return 0.0
    return sum(float(r or 0) for r in readings) / len(readings)


def _get_daily_total(db, household_id: int, timestamp: datetime) -> float:
    day_start, day_end = _day_window(timestamp)
    values = db.execute(
        select(models.MeterReading.energy_consumed_kwh)
        .join(models.SmartMeter, models.MeterReading.meter_id == models.SmartMeter.meter_id)
        .where(models.SmartMeter.household_id == household_id)
        .where(models.MeterReading.timestamp >= day_start)
        .where(models.MeterReading.timestamp < day_end)
    ).all()
    return sum(float(value or 0) for (value,) in values)


def _get_monthly_total(db, household_id: int, timestamp: datetime) -> float:
    month_start, month_end = _month_window(timestamp)
    values = db.execute(
        select(models.MeterReading.energy_consumed_kwh)
        .join(models.SmartMeter, models.MeterReading.meter_id == models.SmartMeter.meter_id)
        .where(models.SmartMeter.household_id == household_id)
        .where(models.MeterReading.timestamp >= month_start)
        .where(models.MeterReading.timestamp < month_end)
    ).all()
    return sum(float(value or 0) for (value,) in values)


def _day_window(timestamp: datetime) -> tuple[datetime, datetime]:
    day = timestamp.astimezone(timezone.utc) if timestamp.tzinfo else timestamp.replace(tzinfo=timezone.utc)
    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    end = datetime(day.year, day.month, day.day, tzinfo=timezone.utc) + timedelta(days=1)
    return start, end


def _month_window(timestamp: datetime) -> tuple[datetime, datetime]:
    day = timestamp.astimezone(timezone.utc) if timestamp.tzinfo else timestamp.replace(tzinfo=timezone.utc)
    start = datetime(day.year, day.month, 1, tzinfo=timezone.utc)
    if day.month == 12:
        end = datetime(day.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(day.year, day.month + 1, 1, tzinfo=timezone.utc)
    return start, end
