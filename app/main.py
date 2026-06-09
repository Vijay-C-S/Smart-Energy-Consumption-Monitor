from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import households, meters, readings, alerts, reports, auth
from .views import pages

# APP ENTRY POINT - all routers registered here

app = FastAPI(title="Smart Energy Consumption Monitoring System")

# CORS MIDDLEWARE - allows all origins (open for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HEALTH CHECK endpoint - GET /api/status
@app.get("/api/status", tags=["health"])
def status():
    return {"status": "ok", "service": "smart-energy-backend"}

# ROUTER REGISTRATION - each feature maps to a router file
app.include_router(pages.router)                                           # frontend HTML pages -> views/pages.py
app.include_router(auth.router)                                            # login/auth -> routers/auth.py
app.include_router(households.router, prefix="/households", tags=["households"])  # household CRUD -> routers/households.py
app.include_router(meters.router, prefix="/meters", tags=["meters"])              # meter registration -> routers/meters.py
app.include_router(readings.router, prefix="/readings", tags=["readings"])        # submit readings -> routers/readings.py
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])              # alert management -> routers/alerts.py
app.include_router(reports.router, prefix="/reports", tags=["reports"])           # bill + monthly report -> routers/reports.py
