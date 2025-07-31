from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth import signup, login, logout

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Render login/signup page
@router.get("/login", response_class=HTMLResponse)
async def show_login_form(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})

# Handle signup
@router.post("/signup", response_class=HTMLResponse)
async def signup_post(request: Request, username: str = Form(...), password: str = Form(...)):
    result = signup(username, password)

    if result == "Username already exists.":
        return templates.TemplateResponse("auth.html", {
            "request": request,
            "error": "name already registered"
        })

    request.session["user"] = {"name": username}
    request.session["toast"] = "Signup successful. Welcome, " + username + "!"
    return RedirectResponse(url="/", status_code=302)

# Handle login and store in session
@router.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    result = login(username, password)

    if result == "Login successful.":
        request.session["user"] = {"name": username}
        request.session["toast"] = "Welcome back, " + username + "!"
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse("auth.html", {
        "request": request,
        "error": "Invalid credentials"
    })

# Logout and clear session
@router.post("/logout")
async def logout_user(request: Request):
    request.session.clear()
    request.session["toast"] = "You’ve been logged out successfully."
    return RedirectResponse(url="/", status_code=302)

# Get current logged-in user
@router.get("/me")
async def get_logged_in_user(request: Request):
    user = request.session.get("user")
    return JSONResponse(content={"current_user": user})