from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "smart-energy-backend"}


def test_household_meter_reading_flow(db_session):
    household_payload = {
        "customer_name": "Ravi Kumar",
        "email": "ravi@example.com",
        "phone": "9876543210",
        "address": "Pune, Maharashtra",
    }
    household_response = client.post("/households/", json=household_payload)
    assert household_response.status_code == 201
    household_id = household_response.json()["household_id"]

    meter_response = client.post(
        "/meters/",
        json={"household_id": household_id, "meter_number": "MTR1001"},
    )
    assert meter_response.status_code == 201
    meter_id = meter_response.json()["meter_id"]

    reading_response = client.post(
        "/readings/",
        json={
            "meter_id": meter_id,
            "energy_consumed_kwh": 3.5,
            "voltage": 230.0,
            "current": 12.5,
            "power_factor": 0.95,
        },
    )
    assert reading_response.status_code == 201

    household_readings = client.get(f"/households/{household_id}/readings")
    assert household_readings.status_code == 200
    assert len(household_readings.json()) == 1

    household_alerts = client.get(f"/households/{household_id}/alerts")
    assert household_alerts.status_code == 200
    assert len(household_alerts.json()) >= 1


def test_monthly_report_and_bill_estimate(db_session):
    household_response = client.post(
        "/households/",
        json={
            "customer_name": "Anita Sharma",
            "email": "anita@example.com",
            "phone": "9999999999",
            "address": "Mumbai, Maharashtra",
        },
    )
    household_id = household_response.json()["household_id"]

    meter_response = client.post(
        "/meters/",
        json={"household_id": household_id, "meter_number": "MTR2001"},
    )
    meter_id = meter_response.json()["meter_id"]

    for reading in (1.2, 1.8, 2.5):
        client.post(
            "/readings/",
            json={
                "meter_id": meter_id,
                "energy_consumed_kwh": reading,
                "voltage": 230.0,
                "current": 10.0,
                "power_factor": 0.96,
            },
        )

    report_response = client.get(f"/reports/monthly/{household_id}")
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["reading_count"] == 3
    assert report["total_kwh"] == 5.5
    assert report["peak_kwh"] == 2.5

    bill_response = client.get(f"/reports/bill-estimate/{household_id}")
    assert bill_response.status_code == 200
    bill = bill_response.json()
    assert bill["household_id"] == household_id
    assert bill["total_kwh"] == 5.5
    assert bill["estimated_bill"] > 0
