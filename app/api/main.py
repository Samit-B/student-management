from fastapi import FastAPI, Request, Form, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, Response
from app.api.routes.routes import router
from app.api.core.database.db import get_students  

app = FastAPI()

# Serve static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates setup for rendering HTML pages
templates = Jinja2Templates(directory="templates")

# ✅ Login Page Route - Displays the login page
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ✅ Handle Login Form Submission - Authenticates user and sets a cookie
@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "password":  # Simple authentication logic
        response = RedirectResponse(url="/index", status_code=303)
        response.set_cookie(key="is_logged_in", value="true", httponly=True)  # Set a secure login cookie
        return response
    return RedirectResponse(url="/login", status_code=303)  # Redirect back to login on failure

# ✅ Load Index Page With Student Data - Only accessible if logged in
@app.get("/index")
async def index_page(request: Request, is_logged_in: str = Cookie(default="false")):
    if is_logged_in != "true":
        return RedirectResponse(url="/login", status_code=303)  # Redirect to login if not authenticated

    students = get_students()  # Fetch student records from the database
    return templates.TemplateResponse("index.html", {"request": request, "students": students, "is_logged_in": True})

# ✅ Logout Route - Clears login session and redirects to login page
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("is_logged_in")  # Remove authentication cookie
    return response

# ✅ Include API Routes from the router (handles additional functionalities)
app.include_router(router)
