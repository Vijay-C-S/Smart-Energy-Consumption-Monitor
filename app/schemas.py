from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# ALL REQUEST/RESPONSE SCHEMAS (Pydantic validation) are defined in this file

# SCHEMA: Household - create, update, and response shapes
class HouseholdCreate(BaseModel):
    customer_name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    daily_kwh_threshold: float = 20.0

class HouseholdUpdate(BaseModel):
    customer_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    daily_kwh_threshold: Optional[float] = None

class HouseholdOut(HouseholdCreate):
    model_config = ConfigDict(from_attributes=True)

    household_id: int
    created_at: datetime

# SCHEMA: SmartMeter - register a meter and response shape
class MeterCreate(BaseModel):
    household_id: int
    meter_number: str


class MeterOut(MeterCreate):
    model_config = ConfigDict(from_attributes=True)

    meter_id: int
    status: Optional[str] = "ACTIVE"
    installed_date: Optional[datetime]

# SCHEMA: MeterReading - submit a reading (energy_consumed_kwh must be > 0)
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

# SCHEMA: Alert - create and response shape (severity: LOW/MEDIUM/HIGH, status: OPEN/RESOLVED)
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


# SCHEMA: BillEstimateOut - total kWh * rate_per_kwh = estimated_bill
class BillEstimateOut(BaseModel):
    household_id: int
    total_kwh: float
    rate_per_kwh: float
    estimated_bill: float


# SCHEMA: MonthlyReportOut - aggregated stats: total, average, peak kWh
class MonthlyReportOut(BaseModel):
    household_id: int
    total_kwh: float
    average_kwh: float
    peak_kwh: float
    reading_count: int
