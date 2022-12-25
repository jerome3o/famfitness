from pathlib import Path
import fitbit
import json
import os

_token_file = Path(__file__).parent / "token.json"
_personal_token_file = Path(__file__).parent / "personal_token.json"


def refresh_cb(token_dict: dict, token_file: str = None) -> None:
    token_file = token_file or _token_file
    with open(_token_file, "w", encoding="utf-8") as f:
        json.dump(token_dict, f, indent=4)


def get_token_dict(token_file: str = None) -> dict:
    token_file = token_file or _token_file
    with open(token_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_fitbit_client(personal: bool = False) -> fitbit.Fitbit:
    if personal:
        client_secret = os.environ["PERSONAL_OAUTH_SECRET"]
        client_id = os.environ["PERSONAL_OAUTH_ID"]
    else:
        client_secret = os.environ["OAUTH_SECRET"]
        client_id = os.environ["OAUTH_ID"]

    token_file = _personal_token_file if personal else _token_file
    token_dict = get_token_dict(token_file=token_file)
    return fitbit.Fitbit(
        client_id,
        client_secret,
        access_token=token_dict["access_token"],
        refresh_token=token_dict["refresh_token"],
        refresh_cb=lambda x: refresh_cb(x, token_file=token_file),
    )


def get_heart_data(client: fitbit.Fitbit = None):
    client = client or get_fitbit_client(personal=True)
    client.heart()


def main():
    get_heart_data()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
