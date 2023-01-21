import base64
import secrets
import hashlib
from pathlib import Path
from urllib.parse import quote
import json

from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
import requests

from famfitness.auth.helpers import get_token
from famfitness.constants import (
    CLIENT_SECRET,
    AUTH_URL,
    REDIRECT_URL,
    RESOURCE_URL,
    STATE,
    SESSION_MIDDLEWARE_SECRET,
    SCOPES,
)


app = FastAPI()

# Install the SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_MIDDLEWARE_SECRET,
)


@app.get("/")
def index():
    # Return the index.html file from the static directory
    return HTMLResponse(Path("fe/index.html").read_text())


@app.get("/callback")
def callback(request: Request, code: str, state: str) -> Response:
    """Exchange the authorization code for an access token."""
    # Validate the state value to protect against CSRF attacks

    if state != STATE:
        return Response(status_code=400, content="Invalid state value")

    # Get the code verifier from the user's session
    code_verifier = request.session["code_verifier"]

    # get access_token from session if its there, otherwise use get token
    access_token = request.session.get("access_token")
    if not access_token:
        token_response = get_token(code_verifier, code)
        access_token = token_response["access_token"]
        request.session["access_token"] = access_token

        # if the token has the user_id field, save it as json to the tokens/ folder
        if "user_id" in token_response:
            user_id = token_response["user_id"]
            with open(f"tokens/{user_id}.json", "w") as file:
                json.dump(token_response, file)

    # Send a request to the protected resource using the access token
    resource_response = requests.get(
        RESOURCE_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=5,
    )

    # Return the response from the protected resource
    return Response(
        content=json.dumps(resource_response.json(), indent=4),
        media_type="application/json",
    )


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


# Serve the "fe" directory as a static directory
app.mount("/", StaticFiles(directory="fe"), name="static")


def main():
    from uvicorn import run

    run(app, host="localhost", port=8000)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
