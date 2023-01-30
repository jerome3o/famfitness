# All functions must have type hints!
from typing import Dict, List, Tuple
import json
from pathlib import Path

# import fitbit client
from fitbit import Fitbit

from famfitness.constants import CLIENT_ID, CLIENT_SECRET

_DEFAULT_FITBIT_TOKEN_PATH = "tokens/"

# function that takes in a path to a json holding fitbit oauth tokens and returns a fitbit client
def get_fitbit_client(path: Path) -> Fitbit:
    # open json file
    with open(path) as f:
        # load json file
        data = json.load(f)

    # create callback that updates the json file with new tokens
    def callback(token):
        with open(path, "w") as f:
            json.dump(token, f, indent=4)

    # create fitbit client
    fitbit_client = Fitbit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        **data,
        refresh_cb=callback,
    )

    # return fitbit client
    return fitbit_client


# function that loads in all tokens in a directory and returns a dictionary of fitbit clients
def get_fitbit_clients(path: Path = None) -> Dict[str, Fitbit]:
    path = path or _DEFAULT_FITBIT_TOKEN_PATH
    path = Path(path)

    # using dictionary comprehension and glob
    return {
        # get the name of the file without the extension
        file.stem: get_fitbit_client(file)
        # iterate over all files in the directory
        for file in path.glob("*.json")
    }
