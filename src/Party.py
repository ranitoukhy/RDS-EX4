import enum
import random

from src.AllEntities import *


class PartyType(enum.Enum):
    SERVER = "SERVER",
    CLIENT = "CLIENT"
    FAULTY_SERVER = "FAULTY_SERVER"


class StatusCode(enum.Enum):
    OK = "OK"
    OMISSION_TOO_LONG = "OMISSION_TOO_LONG"
    BAD_REQUEST = "BAD_REQUEST"


OMISSION_PROB = 0.05


class Party:
    def __init__(self, id, party_type: PartyType):
        self.id = id
        self.tokens = {}
        self.party_type = party_type

    def get_tokens(self):
        if random.uniform(0, 1) < OMISSION_PROB:
            return StatusCode.OMISSION_TOO_LONG
        pass

    def pay(self, token_id, version, owner_id):
        if random.uniform(0, 1) < OMISSION_PROB:
            return StatusCode.OMISSION_TOO_LONG

        all_servers = AllEntities().get_servers()
        for server in all_servers:
            server.pay(token_id, version, owner_id)
        pass

    def add_token(self, token):
        self.tokens[token.id] = token

    def transform_to_server(self):
        if self.party_type == PartyType.SERVER:
            return
        pass

    def transform_to_client(self):
        if self.party_type == PartyType.CLIENT:
            return

        self.party_type = PartyType.CLIENT

    def set_server_to_faulty(self):
        if self.party_type in [PartyType.FAULTY_SERVER, PartyType.CLIENT]:
            return StatusCode.BAD_REQUEST

        self.party_type = PartyType.FAULTY_SERVER
