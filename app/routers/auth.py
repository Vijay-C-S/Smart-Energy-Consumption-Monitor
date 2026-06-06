from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db
from ..models import Household
import hashlib, os, base64

router = APIRouter(prefix="/auth", tags=["auth"])


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return base64.b64encode(salt + dk).decode()


def _verify_password(password: str, stored: str) -> bool:
    try:
        data = base64.b64decode(stored.encode())
        salt, dk = data[:16], data[16:]
        new_dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
        return new_dk == dk
    except Exception:
        return False


class RegisterRequest(BaseModel):
    customer_name: str
    email: str
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None
    daily_kwh_threshold: float = 20.0


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    household_id: int
    customer_name: str
    email: str


@router.post("/register", response_model=AuthResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = db.query(Household).filter(Household.email == data.email).first()

    if existing:
        if existing.password_hash and not _verify_password("admin", existing.password_hash):
            # account already claimed with a real password — reject
            raise HTTPException(status_code=400, detail="Email already registered")
        # admin-created household (default password) — let the user claim it
        existing.password_hash = _hash_password(data.password)
        existing.customer_name = data.customer_name
        existing.daily_kwh_threshold = data.daily_kwh_threshold
        if data.phone:
            existing.phone = data.phone
        if data.address:
            existing.address = data.address
        db.commit()
        db.refresh(existing)
        return AuthResponse(
            household_id=existing.household_id,
            customer_name=existing.customer_name,
            email=existing.email,
        )

    household = Household(
        customer_name=data.customer_name,
        email=data.email,
        password_hash=_hash_password(data.password),
        phone=data.phone,
        address=data.address,
        daily_kwh_threshold=data.daily_kwh_threshold,
    )
    db.add(household)
    db.commit()
    db.refresh(household)
    return AuthResponse(
        household_id=household.household_id,
        customer_name=household.customer_name,
        email=household.email,
    )


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.email == data.email).first()
    if not household or not household.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not _verify_password(data.password, household.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return AuthResponse(
        household_id=household.household_id,
        customer_name=household.customer_name,
        email=household.email,
    )
