from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from auth import get_current_user

app = FastAPI(title="Railway AI Monitoring")

templates = Jinja2Templates(directory="templates")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/login")

@app.get("/dashboard")
def dashboard(request: Request, user=Depends(get_current_user)):
    role = user["role"]
    if role == "admin":
        template = "dashboard_admin.html"
    elif role == "station_master":
        template = "dashboard_master.html"
    elif role == "employee":
        template = "dashboard_employee.html"
    else:
        template = "dashboard_passenger.html"
    return templates.TemplateResponse(template, {"request": request, "user": user})
