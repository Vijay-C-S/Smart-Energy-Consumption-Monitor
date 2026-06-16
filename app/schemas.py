from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class HouseholdCreate(BaseModel):
    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[A-Za-z][A-Za-z .'-]*$",
    )
    email: str = Field(
        ...,
        max_length=100,
        pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$",
    )
    phone: Optional[str] = Field(default=None, pattern=r"^\d{10}$")
    address: Optional[str] = None
    daily_kwh_threshold: float = Field(default=20.0, gt=0)


class HouseholdUpdate(BaseModel):
    customer_name: Optional[str] = Field(default=None, min_length=2, max_length=100, pattern=r"^[A-Za-z][A-Za-z .'-]*$")
    email: Optional[str] = Field(default=None, max_length=100, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    phone: Optional[str] = Field(default=None, pattern=r"^\d{10}$")
    address: Optional[str] = None
    daily_kwh_threshold: Optional[float] = Field(default=None, gt=0)


class HouseholdOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    daily_kwh_threshold: float
    household_id: int
    created_at: datetime


class MeterCreate(BaseModel):
    household_id: int
    meter_number: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9-]*$",
    )


class MeterOut(MeterCreate):
    model_config = ConfigDict(from_attributes=True)

    meter_id: int
    status: Optional[str] = "ACTIVE"
    installed_date: Optional[datetime]


class ReadingCreate(BaseModel):
    meter_id: int
    energy_consumed_kwh: float = Field(..., gt=0)
    voltage: Optional[float]
    current: Optional[float]
    power_factor: Optional[float]


class ReadingOut(ReadingCreate):
    model_config = ConfigDict(from_attributes=True)

    reading_id: int
    timestamp: datetime


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    alert_id: int
    household_id: Optional[int]
    meter_id: Optional[int]
    alert_type: str
    message: str
    severity: Optional[str]
    status: str
    created_at: datetime


class AlertCreate(BaseModel):
    household_id: Optional[int] = None
    meter_id: Optional[int] = None
    alert_type: str
    message: str
    severity: str = "MEDIUM"
    status: str = "OPEN"


class BillEstimateOut(BaseModel):
    household_id: int
    total_kwh: float
    rate_per_kwh: float
    estimated_bill: float


class MonthlyReportOut(BaseModel):
    household_id: int
    total_kwh: float
    average_kwh: float
    peak_kwh: float
    reading_count: int
