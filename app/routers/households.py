from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..database import get_db
from .. import schemas, models
from .auth import _hash_password

router = APIRouter()


@router.post("/", response_model=schemas.HouseholdOut, status_code=201)
def create_household(payload: schemas.HouseholdCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(models.Household).where(models.Household.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    household = models.Household(**payload.model_dump(), password_hash=_hash_password("admin"))
    db.add(household)
    db.commit()
    db.refresh(household)
    return household


@router.get("/", response_model=List[schemas.HouseholdOut])
def list_households(db: Session = Depends(get_db)):
    return db.scalars(select(models.Household).order_by(models.Household.household_id.desc())).all()


@router.get("/{household_id}", response_model=schemas.HouseholdOut)
def get_household(household_id: int, db: Session = Depends(get_db)):
    household = db.get(models.Household, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return household


@router.put("/{household_id}", response_model=schemas.HouseholdOut)
def update_household(household_id: int, payload: schemas.HouseholdUpdate, db: Session = Depends(get_db)):
    household = db.get(models.Household, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    if payload.email and payload.email != household.email:
        existing = db.scalar(select(models.Household).where(models.Household.email == payload.email))
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(household, field, value)
    db.commit()
    db.refresh(household)
    return household


@router.delete("/{household_id}", status_code=204)
def delete_household(household_id: int, db: Session = Depends(get_db)):
    household = db.get(models.Household, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    db.query(models.Alert).filter(models.Alert.household_id == household_id).delete()
    db.delete(household)
    db.commit()


@router.get("/{household_id}/readings", response_model=List[schemas.ReadingOut])
def get_household_readings(household_id: int, db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(models.MeterReading)
            .join(models.SmartMeter, models.MeterReading.meter_id == models.SmartMeter.meter_id)
            .where(models.SmartMeter.household_id == household_id)
            .order_by(models.MeterReading.timestamp.desc())
        )
        .scalars()
        .all()
    )
    return rows


@router.get("/{household_id}/alerts", response_model=List[schemas.AlertOut])
def get_household_alerts(household_id: int, db: Session = Depends(get_db)):
    return (
        db.scalars(
            select(models.Alert)
            .where(models.Alert.household_id == household_id)
            .order_by(models.Alert.created_at.desc())
        )
        .all()
    )


@router.get("/{household_id}/bill-estimate", response_model=schemas.BillEstimateOut)
def get_household_bill_estimate(household_id: int, db: Session = Depends(get_db)):
    total_kwh = _get_household_total_kwh(db, household_id)
    rate = _get_current_rate(db)
    return schemas.BillEstimateOut(
        household_id=household_id,
        total_kwh=total_kwh,
        rate_per_kwh=rate,
        estimated_bill=round(total_kwh * rate, 2),
    )


def _get_household_total_kwh(db: Session, household_id: int) -> float:
    result = db.execute(
        select(models.MeterReading.energy_consumed_kwh)
        .join(models.SmartMeter, models.MeterReading.meter_id == models.SmartMeter.meter_id)
        .where(models.SmartMeter.household_id == household_id)
    ).all()
    return round(sum(row[0] or 0 for row in result), 4)


def _get_current_rate(db: Session) -> float:
    tariff = db.scalars(select(models.TariffConfig).order_by(models.TariffConfig.effective_from.desc())).first()
    return float(tariff.rate_per_kwh) if tariff else 8.0
