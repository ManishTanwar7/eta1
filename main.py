from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from auth import authenticate_user, create_access_token, get_current_user

app = FastAPI(title="Railway AI Monitoring")
templates = Jinja2Templates(directory="templates")

# Root redirects to login
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/login")

# GET: show login form
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# POST: process login
@app.post("/login")
def login_action(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        # Invalid credentials → reload login with error
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})
    # Create token (for demo we skip storing it in cookies, just redirect)
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    # Redirect to dashboard
    return RedirectResponse(url="/dashboard", status_code=303)

# Dashboard route with role‑based template
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
