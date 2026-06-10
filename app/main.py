from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import households, meters, readings, alerts, reports, auth
from .views import pages

app = FastAPI(title="Smart Energy Consumption Monitoring System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status", tags=["health"])
def status():
    return {"status": "ok", "service": "smart-energy-backend"}

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(households.router, prefix="/households", tags=["households"])
app.include_router(meters.router, prefix="/meters", tags=["meters"])
app.include_router(readings.router, prefix="/readings", tags=["readings"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
