from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy.orm import relationship


class Household(Base):
    __tablename__ = 'households'
    household_id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    daily_kwh_threshold = Column(Float, nullable=False, default=20.0)
    password_hash = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meters = relationship('SmartMeter', back_populates='household', cascade='all, delete-orphan')
    alerts = relationship('Alert', cascade='all, delete-orphan')


class SmartMeter(Base):
    __tablename__ = 'smart_meters'
    meter_id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey('households.household_id', ondelete='CASCADE'), unique=True)
    meter_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default='ACTIVE')
    installed_date = Column(DateTime(timezone=True), server_default=func.now())
    household = relationship('Household', back_populates='meters')
    readings = relationship('MeterReading', back_populates='meter', cascade='all, delete-orphan')


class MeterReading(Base):
    __tablename__ = 'meter_readings'
    reading_id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(Integer, ForeignKey('smart_meters.meter_id', ondelete='CASCADE'))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    energy_consumed_kwh = Column(Float, nullable=False)
    voltage = Column(Float)
    current = Column(Float)
    power_factor = Column(Float)
    meter = relationship('SmartMeter', back_populates='readings')


class Alert(Base):
    __tablename__ = 'alerts'
    alert_id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey('households.household_id', ondelete='CASCADE'))
    meter_id = Column(Integer, ForeignKey('smart_meters.meter_id', ondelete='SET NULL'))
    alert_type = Column(String(50))
    message = Column(Text)
    severity = Column(String(20))
    status = Column(String(20), default='OPEN')
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TariffConfig(Base):
    __tablename__ = 'tariff_config'
    tariff_id = Column(Integer, primary_key=True, index=True)
    rate_per_kwh = Column(Float, nullable=False)
    effective_from = Column(DateTime(timezone=True), server_default=func.now())
