import base64
import secrets
import os
import hashlib
from pathlib import Path
from urllib.parse import quote
import json

from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import requests


# Replace these values with your own client ID and client secret
CLIENT_ID = os.environ.get("OAUTH_ID")
CLIENT_SECRET = os.environ.get("OAUTH_SECRET")

# The authorization URL for Fitbit's OAuth 2.0 authorization server
AUTH_URL = "https://www.fitbit.com/oauth2/authorize"

# The token URL for Fitbit's OAuth 2.0 authorization server
TOKEN_URL = "https://api.fitbit.com/oauth2/token"

# The URL of your application
REDIRECT_URL = "http://localhost:8000/callback"

# The URL of the protected resource that you want to access
RESOURCE_URL = "https://api.fitbit.com/1/user/-/activities/date/today.json"

# A state value to use for CSRF protection
STATE = secrets.token_hex(16)

# Secret value for session
SESSION_MIDDLEWARE_SECRET = secrets.token_hex(16)


# SCOPE
SCOPES = [
    "activity",
    "heartrate",
    "location",
    "nutrition",
    "oxygen_saturation",
    "profile",
    "respiratory_rate",
    "settings",
    "sleep",
    "social",
    "temperature",
    "weight",
]


app = FastAPI()

# Install the SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=SESSION_MIDDLEWARE_SECRET)


@app.get("/")
def index():
    # Return the index.html file from the static directory
    return Path("fe/index.html").read_text()


@app.get("/login")
def login(request: Request) -> Response:
    """Redirect the user to the Fitbit authorization page."""
    # Generate the code verifier and code challenge
    code_verifier = secrets.token_hex(32)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )

    # Save the code verifier in the user's session
    request.session["code_verifier"] = code_verifier

    # Construct the authorization URL
    auth_url = (
        f"{AUTH_URL}?"
        "response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={quote(REDIRECT_URL)}"
        f"&state={STATE}"
        f"&code_challenge={code_challenge}"
        f"&scope={'%20'.join(SCOPES)}"
        "&code_challenge_method=S256"
    )

    # Redirect the user to the authorization URL
    return RedirectResponse(auth_url)


@app.get("/callback")
def callback(request: Request, code: str, state: str) -> Response:
    """Exchange the authorization code for an access token."""
    # Validate the state value to protect against CSRF attacks
    if state != STATE:
        return Response(status_code=400, content="Invalid state value")

    # Get the code verifier from the user's session
    code_verifier = request.session["code_verifier"]

    auth_token = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")).decode("utf-8")
    auth_header = f"Basic {auth_token}"

    # Send a request to the token URL to exchange the authorization code for an access token
    token_response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "code_verifier": code_verifier,
            "redirect_uri": REDIRECT_URL,
            "code": code,
        },
        headers={"Authorization": auth_header},
    )
    print(token_response.json())

    # Extract the access token from the response
    access_token = token_response.json()["access_token"]

    # Send a request to the protected resource using the access token
    resource_response = requests.get(
        RESOURCE_URL, headers={"Authorization": f"Bearer {access_token}"}
    )

    # Return the response from the protected resource
    return Response(
        content=json.dumps(resource_response.json(), indent=4), media_type="application/json"
    )


# Serve the "fe" directory as a static directory
app.mount("/", StaticFiles(directory="fe"), name="static")


def main():
    from uvicorn import run

    run(app, host="localhost", port=8000)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
