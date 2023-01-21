import base64

import requests

from constants import CLIENT_ID, CLIENT_SECRET, REDIRECT_URL, TOKEN_URL


def get_token(code_verifier: str, code: str) -> dict:

    # Create the authorization code grant request body
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
        timeout=5,
    )

    return token_response.json()
