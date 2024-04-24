import enum
import random
from asyncio import sleep

from src.AllEntities import *

OMISSION_DELAY = 15

OMISSION_PROB = 0.05

class PartyType(enum.Enum):
    SERVER = "SERVER",
    CLIENT = "CLIENT"
    FAULTY_SERVER = "FAULTY_SERVER"


class StatusCode(enum.Enum):
    OK = "OK"
    OMISSION_TOO_LONG = "OMISSION_TOO_LONG"
    BAD_REQUEST = "BAD_REQUEST"


class Message:
    def __init__(self, sender_id):
        self.is_active = True
        self.sender_id = sender_id


class PayMessage(Message):
    def __init__(self, token_id, version, owner, sender):
        super().__init__(sender)
        self.token_id = token_id
        self.version = version
        self.owner = owner


class EchoPayMessage(Message):
    def __init__(self, sender_id, pay_message: PayMessage):
        super().__init__(sender_id)
        self.pay_message = pay_message


class Party:
    def __init__(self, id, party_type: PartyType):
        self.id = id
        self.tokens = {}
        self.party_type = party_type
        self.current_requests = set()

    def get_tokens(self):
        if random.uniform(0, 1) < OMISSION_PROB:
            return StatusCode.OMISSION_TOO_LONG
        pass

    def pay(self, pay_request: PayMessage, party_type: PartyType):
        if pay_request in self.current_requests:
            return None

        if self._handle_omission() == StatusCode.OMISSION_TOO_LONG:
            return StatusCode.OMISSION_TOO_LONG

        self.current_requests.add(pay_request)

        responses = set()
        all_servers = AllEntities().get_servers()
        for server in all_servers:
            responses.add(server.pay(pay_request, self.party_type))

        return StatusCode.OK

    def pay(self, token_id, version, owner_id):
        pay_request = PayMessage(token_id, version, owner_id, self.id)
        return self.pay(pay_request, self.party_type)


    def receive_message(self, sender, message):
        pass

    def _handle_omission(self):
        if self.party_type == PartyType.CLIENT or self.party_type == PartyType.FAULTY_SERVER:
            if random.uniform(0, 1) < OMISSION_PROB:
                sleep(OMISSION_DELAY)
                return StatusCode.OMISSION_TOO_LONG

        return StatusCode.OK


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
