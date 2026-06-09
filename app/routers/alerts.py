from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..database import get_db
from .. import models, schemas

# ALERT ENDPOINTS - list, create, resolve alerts
# ALERT LOGIC (auto-generation) is in services/alert_service.py

router = APIRouter()


# LIST ALL ALERTS - GET /alerts/
@router.get("/", response_model=List[schemas.AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    return db.scalars(select(models.Alert).order_by(models.Alert.created_at.desc())).all()


# LIST ALERTS BY HOUSEHOLD - GET /alerts/household/{household_id}
@router.get("/household/{household_id}", response_model=List[schemas.AlertOut])
def list_household_alerts(household_id: int, db: Session = Depends(get_db)):
    return db.scalars(
        select(models.Alert)
        .where(models.Alert.household_id == household_id)
        .order_by(models.Alert.created_at.desc())
    ).all()


# CREATE ALERT MANUALLY - POST /alerts/
@router.post("/", response_model=schemas.AlertOut, status_code=201)
def create_alert(payload: schemas.AlertCreate, db: Session = Depends(get_db)):
    alert = models.Alert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


# RESOLVE ALERT - PUT /alerts/{alert_id}/resolve (sets status to RESOLVED)
@router.put("/{alert_id}/resolve", response_model=schemas.AlertOut)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(models.Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "RESOLVED"
    db.commit()
    db.refresh(alert)
    return alert
