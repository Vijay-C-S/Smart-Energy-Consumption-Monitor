from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database import get_db
from .. import models, schemas

# REPORTS ENDPOINTS - monthly usage report and bill estimate

router = APIRouter()


# MONTHLY REPORT - GET /reports/monthly/{household_id} (total, average, peak kWh)
@router.get("/monthly/{household_id}", response_model=schemas.MonthlyReportOut)
def monthly_report(household_id: int, db: Session = Depends(get_db)):
    meter_ids = db.scalars(
        select(models.SmartMeter.meter_id).where(models.SmartMeter.household_id == household_id)
    ).all()
    if not meter_ids:
        raise HTTPException(status_code=404, detail="Household not found or no meters registered")

    readings = db.scalars(
        select(models.MeterReading).where(models.MeterReading.meter_id.in_(meter_ids))
    ).all()
    if not readings:
        return schemas.MonthlyReportOut(household_id=household_id, total_kwh=0.0, average_kwh=0.0, peak_kwh=0.0, reading_count=0)

    values = [float(r.energy_consumed_kwh or 0) for r in readings]
    total = round(sum(values), 4)
    count = len(values)
    average = round(total / count, 4) if count else 0.0
    peak = round(max(values), 4)

    return schemas.MonthlyReportOut(
        household_id=household_id,
        total_kwh=total,
        average_kwh=average,
        peak_kwh=peak,
        reading_count=count,
    )


# BILL ESTIMATE (reports) - GET /reports/bill-estimate/{household_id}
@router.get("/bill-estimate/{household_id}", response_model=schemas.BillEstimateOut)
def bill_estimate(household_id: int, db: Session = Depends(get_db)):
    total_kwh = 0.0
    meter_ids = db.scalars(
        select(models.SmartMeter.meter_id).where(models.SmartMeter.household_id == household_id)
    ).all()
    if meter_ids:
        total_kwh = round(
            sum(
                float(value or 0)
                for (value,) in db.execute(
                    select(models.MeterReading.energy_consumed_kwh).where(models.MeterReading.meter_id.in_(meter_ids))
                ).all()
            ),
            4,
        )

    tariff = db.scalars(select(models.TariffConfig).order_by(models.TariffConfig.effective_from.desc())).first()
    rate = float(tariff.rate_per_kwh) if tariff else 8.0
    return schemas.BillEstimateOut(
        household_id=household_id,
        total_kwh=total_kwh,
        rate_per_kwh=rate,
        estimated_bill=round(total_kwh * rate, 2),
    )
