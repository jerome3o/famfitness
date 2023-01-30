from famfitness.fitbit_client import get_fitbit_clients


def main():
    clients = get_fitbit_clients()
    print(clients)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
