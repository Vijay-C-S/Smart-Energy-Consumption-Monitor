from __future__ import annotations

from app import models
from app.services.alert_service import AlertThresholds, create_alerts_for_reading


def test_alert_service_creates_high_usage_and_spike(db_session):
    household = models.Household(customer_name="Test User", email="test@example.com")
    db_session.add(household)
    db_session.commit()
    db_session.refresh(household)

    meter = models.SmartMeter(household_id=household.household_id, meter_number="MTR3001")
    db_session.add(meter)
    db_session.commit()
    db_session.refresh(meter)

    first = models.MeterReading(
        meter_id=meter.meter_id,
        energy_consumed_kwh=1.0,
        voltage=230.0,
        current=8.0,
        power_factor=0.95,
    )
    db_session.add(first)
    db_session.commit()
    db_session.refresh(first)

    second = models.MeterReading(
        meter_id=meter.meter_id,
        energy_consumed_kwh=4.2,
        voltage=231.0,
        current=14.0,
        power_factor=0.93,
    )
    db_session.add(second)
    db_session.commit()
    db_session.refresh(second)

    created = create_alerts_for_reading(second.reading_id, AlertThresholds(rate_per_kwh=8.0), db=db_session)
    assert "HIGH_USAGE" in created
    assert "SPIKE_DETECTED" in created

    alerts = db_session.query(models.Alert).all()
    alert_types = {alert.alert_type for alert in alerts}
    assert "HIGH_USAGE" in alert_types
    assert "SPIKE_DETECTED" in alert_types
