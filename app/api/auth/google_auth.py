from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    client_kwargs={"scope": "openid email profile"},
)

@router.get("/login/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_auth")
    print(f"Redirect URI: {redirect_uri}")  # Debugging output
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google")
async def google_auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get("userinfo")
        request.session["user"] = user
        print(f"User info: {user}")  # Debugging output
        return RedirectResponse(url="/dashboard")
    except Exception as e:
        print(f"Error during Google authentication: {e}")  # Debugging output
        raise
