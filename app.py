import base64
import secrets
import os
import hashlib

from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
import requests

app = FastAPI()

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
        f"&redirect_uri={REDIRECT_URL}"
        f"&state={STATE}"
        f"&code_challenge={code_challenge}"
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
    )

    # Extract the access token from the response
    access_token = token_response.json()["access_token"]

    # Send a request to the protected resource using the access token
    resource_response = requests.get(
        RESOURCE_URL, headers={"Authorization": f"Bearer {access_token}"}
    )

    # Return the response from the protected resource
    return Response(content=resource_response.json(), media_type="application/json")
