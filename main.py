from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import jwt
import time
import uuid
from cryptography.hazmat.primitives import serialization

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


APP_ID = "vpaas-magic-cookie-45d97b5bc5794b1b86a5c1f9b176581b"
JITSI_DOMAIN = f"{APP_ID}.8x8.vc"
KEY_ID = "vpaas-magic-cookie-45d97b5bc5794b1b86a5c1f9b176581b/976b5a"

def generate_jwt_token(room_name: str):
    with open("jaas_private.key", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )

    payload = {
        "aud": "jitsi",
        "iss": "chat",
        "sub": APP_ID,
        "room": room_name,
        "exp": int(time.time()) + 3600,
        "nbf": int(time.time()),
        "context": {
            "features": {
                "livestreaming": True,
                "recording": True,
                "outbound-call": True,
                "sip-outbound-call": False,
                "transcription": True
            },
            "user": {
                "name": "Zmedios",
                "email": "zmediostech@gmail.com",
                "moderator": True
            }
        }
    }

    headers = {
        "kid": KEY_ID
    }

    token = jwt.encode(payload, private_key, algorithm="RS256", headers=headers)
    return token

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    room_name = f"room-{uuid.uuid4().hex[:6]}"
    token = generate_jwt_token(room_name)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "domain": JITSI_DOMAIN,
        "room": room_name,
        "token": token
    })
