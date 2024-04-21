import random

from src.Party import *
from src.AllEntities import AllEntities
from src.Party import PartyType
from src.Token import Token


def main():
    # Generate servers
    server_num = random.randint(3, 7)
    faulty_num = random.randint(1, server_num // 2)
    all_entities = AllEntities()
    generate_servers(server_num, faulty_num, all_entities)

    # Generate clients
    generate_clients(all_entities)
    all_entities.print_data()

    print("Generated entities")


def generate_servers(server_num, faulty_num, all_entities):
    for server_id in range(1, server_num + 1):
        server_type = PartyType.FAULTY_SERVER if faulty_num > 0 else PartyType.SERVER
        server = Party(server_id, server_type)
        faulty_num -= 1
        all_entities.add_server(server)


def generate_clients(all_entities):
    for client_id in range(1, 7):
        client = Party(client_id, PartyType.CLIENT)
        all_entities.add_client(client)
        for token_id in range(client_id * 100, client_id * 100 + 6):
            token = Token(token_id, 1, client_id)
            client.add_token(token)
            all_entities.add_token(token)


if __name__ == "__main__":
    main()
