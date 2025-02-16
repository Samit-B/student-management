from fastapi import FastAPI, Request, Form, Cookie, Depends, HTTPException,APIRouter

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, Response, JSONResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
import os
import traceback
from dotenv import load_dotenv

# Import routes and database utilities
from app.api.routes.routes import router
from app.api.core.database.db import get_students
from app.api.routes.events import router as event_router
from app.api.core.database.db import events_collection
from app.api.agent import run_agent  # LangChain agent
from app.api.auth.google_auth import router as google_auth_router

# Import Google OAuth authentication


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# ✅ Middleware for session-based authentication
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# ✅ Mount Google Auth Routes

app.include_router(google_auth_router, prefix="/auth")


# ✅ Serve static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Jinja2 template setup for rendering HTML pages
templates = Jinja2Templates(directory="templates")


# ✅ Chatbot API Route
class ChatRequest(BaseModel):
    message: str

@app.post("/chatbot")
async def chatbot_endpoint(request: ChatRequest):
    user_message = request.message.strip()  # Get user's message

    try:
        # 🔥 Call LangChain agent to process query
        bot_response = run_agent(user_message)

        # Ensure response is valid
        if not bot_response or not isinstance(bot_response, str):
            return JSONResponse(content={"reply": "I'm sorry, but I couldn't generate a response."})

        return JSONResponse(content={"reply": bot_response})

    except Exception as e:
        print("Error in chatbot:", str(e))
        print(traceback.format_exc())  # Debugging output
        return JSONResponse(content={"reply": "An error occurred while processing your request."}, status_code=500)


# ✅ Home Route
@app.get("/")
async def home():
    return {"message": "Welcome to FastAPI Google Auth"}


# ✅ Login Page Route (Displays login page with Google login option)
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# ✅ Normal Login (Username/Password)
@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "password":  # Simple authentication logic
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="is_logged_in", value="true", httponly=True)  # Set login cookie
        return response
    return RedirectResponse(url="/login", status_code=303)  # Redirect back to login on failure


# ✅ Dashboard Page (After Login)
@app.get("/dashboard")
async def dashboard_page(request: Request, is_logged_in: str = Cookie(default="false")):
    if is_logged_in != "true":
        return RedirectResponse(url="/login", status_code=303)  # Redirect to login if not authenticated
    return templates.TemplateResponse("dashboard.html", {"request": request, "is_logged_in": True})


# ✅ Student Page (After Login)
@app.get("/students")
async def student_page(request: Request, is_logged_in: str = Cookie(default="false")):
    if is_logged_in != "true":
        return RedirectResponse(url="/login", status_code=303)  # Redirect to login if not authenticated

    students = get_students()  # Fetch student records from the database
    return templates.TemplateResponse("student.html", {"request": request, "students": students})


# ✅ Analytics Page (After Login)
@app.get("/analytics")
async def analytics_page(request: Request, is_logged_in: str = Cookie(default="false")):
    try:
        if is_logged_in != "true":
            return RedirectResponse(url="/login", status_code=303)
        return templates.TemplateResponse("analytics.html", {"request": request})
    except Exception as e:
        print("Error in Analytics Page:", str(e))
        return JSONResponse(content={"detail": "Internal Server Error"}, status_code=500)


# ✅ Logout Route (Clears session and redirects to login)
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("is_logged_in")  # Remove authentication cookie
    return response


# ✅ Include Additional API Routes
app.include_router(router)
app.include_router(event_router)


# ✅ Events API (CRUD Operations)
from bson import ObjectId

class Event(BaseModel):
    title: str
    date: str  # Format: "YYYY-MM-DD"

@app.post("/events")
async def add_event(event: Event):
    events_collection.insert_one(event.dict())
    return {"message": "Event added successfully"}

@app.get("/events")
async def get_events():
    events = list(events_collection.find({}, {"_id": 0}))
    return events

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")

    result = events_collection.delete_one({"_id": ObjectId(event_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event deleted successfully"}
