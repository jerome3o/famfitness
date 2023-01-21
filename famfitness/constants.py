import os
import secrets


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
RESOURCE_URL = "https://api.fitbit.com/1/user/-/activities/heart/date/2022-12-24/1d.json"

# A state value to use for CSRF protection
STATE = os.environ.get("STATE_SECRET") or secrets.token_hex(16)

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
