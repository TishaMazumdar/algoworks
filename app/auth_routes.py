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
async def signup_post(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    result = signup(email, password)

    if result == "Username already exists.":
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error": "Email already registered"
        })

    # Set session and redirect to home with toast
    request.session["user"] = {"email": email, "name": name}
    request.session["toast"] = "Signup successful. Welcome, " + name + "!"
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
    return JSONResponse(content={"message": "Logged out."})

# Get current logged-in user
@router.get("/me")
async def get_logged_in_user(request: Request):
    user = request.session.get("user")
    return JSONResponse(content={"current_user": user})