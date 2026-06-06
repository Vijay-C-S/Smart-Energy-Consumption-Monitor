from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..database import get_db
from .. import schemas, models

router = APIRouter()


@router.post("/", response_model=schemas.MeterOut, status_code=201)
def register_meter(payload: schemas.MeterCreate, db: Session = Depends(get_db)):
    household = db.get(models.Household, payload.household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")

    existing = db.scalar(select(models.SmartMeter).where(models.SmartMeter.meter_number == payload.meter_number))
    if existing:
        raise HTTPException(status_code=409, detail="Meter number already registered")

    household_meter = db.scalar(select(models.SmartMeter).where(models.SmartMeter.household_id == payload.household_id))
    if household_meter:
        raise HTTPException(status_code=409, detail="This household already has a meter registered")

    meter = models.SmartMeter(**payload.model_dump())
    db.add(meter)
    db.commit()
    db.refresh(meter)
    return meter


@router.get("/", response_model=List[schemas.MeterOut])
def list_meters(db: Session = Depends(get_db)):
    return db.scalars(select(models.SmartMeter).order_by(models.SmartMeter.meter_id)).all()


@router.get("/{meter_id}", response_model=schemas.MeterOut)
def get_meter(meter_id: int, db: Session = Depends(get_db)):
    meter = db.get(models.SmartMeter, meter_id)
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")
    return meter


@router.delete("/{meter_id}", status_code=204)
def delete_meter(meter_id: int, db: Session = Depends(get_db)):
    meter = db.get(models.SmartMeter, meter_id)
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")
    db.delete(meter)
    db.commit()
