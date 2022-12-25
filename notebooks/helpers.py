from pathlib import Path
import fitbit
import json
import os

_token_file = Path(__file__).parent / "token.json"


def refresh_cb(token_dict: dict) -> None:
    with open(_token_file, "w", encoding="utf-8") as f:
        json.dump(token_dict, f, indent=4)


def get_token_dict() -> dict:
    with open(_token_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_fitbit_client() -> fitbit.Fitbit:
    client_secret = os.environ["OAUTH_SECRET"]
    client_id = os.environ["OAUTH_ID"]
    token_dict = get_token_dict()
    return fitbit.Fitbit(
        client_id,
        client_secret,
        access_token=token_dict["access_token"],
        refresh_token=token_dict["refresh_token"],
        refresh_cb=refresh_cb,
    )


def get_heart_data(client: fitbit.Fitbit = None):
    client = client or get_fitbit_client()
    client.heart()


def main():
    get_heart_data()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
