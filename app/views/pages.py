from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter(include_in_schema=False)
_TEMPLATES = os.path.join(os.path.dirname(__file__), "..", "..", "templates")


@router.get("/", response_class=HTMLResponse)
def dashboard():
    with open(os.path.join(_TEMPLATES, "index.html"), encoding="utf-8") as f:
        return f.read()


@router.get("/user", response_class=HTMLResponse)
def user_portal():
    with open(os.path.join(_TEMPLATES, "user.html"), encoding="utf-8") as f:
        return f.read()
