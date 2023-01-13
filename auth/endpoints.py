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
