from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..database import get_db
from .. import schemas, models
from ..services import alert_service

# READINGS ENDPOINTS - submit and retrieve energy readings

router = APIRouter()


# SUBMIT READING - POST /readings/ (saves reading, then triggers alert checks in background)
@router.post("/", response_model=schemas.ReadingOut, status_code=201)
def post_reading(
    payload: schemas.ReadingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    meter = db.get(models.SmartMeter, payload.meter_id)
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")

    reading = models.MeterReading(**payload.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)

    # BACKGROUND ALERT CHECK - alert_service runs after response is returned to caller
    background_tasks.add_task(alert_service.create_alerts_for_reading, reading.reading_id, db=db)
    return reading


# GET READINGS BY METER - GET /readings/meter/{meter_id}
@router.get("/meter/{meter_id}", response_model=List[schemas.ReadingOut])
def get_meter_readings(meter_id: int, db: Session = Depends(get_db)):
    meter = db.get(models.SmartMeter, meter_id)
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")
    return db.scalars(
        select(models.MeterReading)
        .where(models.MeterReading.meter_id == meter_id)
        .order_by(models.MeterReading.timestamp.desc())
    ).all()


# GET READINGS BY HOUSEHOLD - GET /readings/household/{household_id}
@router.get("/household/{household_id}", response_model=List[schemas.ReadingOut])
def get_household_readings(household_id: int, db: Session = Depends(get_db)):
    return (
        db.scalars(
            select(models.MeterReading)
            .join(models.SmartMeter, models.MeterReading.meter_id == models.SmartMeter.meter_id)
            .where(models.SmartMeter.household_id == household_id)
            .order_by(models.MeterReading.timestamp.desc())
        )
        .all()
    )
