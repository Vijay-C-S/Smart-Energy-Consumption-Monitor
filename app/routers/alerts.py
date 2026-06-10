from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    return db.scalars(select(models.Alert).order_by(models.Alert.created_at.desc())).all()


@router.get("/household/{household_id}", response_model=List[schemas.AlertOut])
def list_household_alerts(household_id: int, db: Session = Depends(get_db)):
    return db.scalars(
        select(models.Alert)
        .where(models.Alert.household_id == household_id)
        .order_by(models.Alert.created_at.desc())
    ).all()


@router.post("/", response_model=schemas.AlertOut, status_code=201)
def create_alert(payload: schemas.AlertCreate, db: Session = Depends(get_db)):
    alert = models.Alert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.put("/{alert_id}/resolve", response_model=schemas.AlertOut)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(models.Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "RESOLVED"
    db.commit()
    db.refresh(alert)
    return alert
