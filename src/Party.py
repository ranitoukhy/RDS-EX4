import enum
import random
import threading
import time
from asyncio import sleep
import threading
import time

from src.AllEntities import *

OMISSION_DELAY = 15

OMISSION_PROB = 0.05


class PartyType(enum.Enum):
    SERVER = "SERVER",
    CLIENT = "CLIENT",
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
        self.pending_requests = set()
        self.current_request = None
        self.received_messages = []
        self.sent_messages = []
        self.token_info = {}

    def get_tokens(self):
        if random.uniform(0, 1) < OMISSION_PROB:
            return StatusCode.OMISSION_TOO_LONG
        pass

    def pay(self, token_id, version, owner_id):
        pay_request = PayMessage(token_id, version, owner_id, self.id)
        self.sent_messages.append(pay_request)

        for server in AllEntities().get_servers():
            print(f"{self.id} says: sending message to {server.id}")
            self.send_message(recipient=server, message=pay_request)

        self.sent_messages.remove(pay_request)

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

    def send_message(self, recipient, message):
        # Simulate sending a message to another client
        recipient.receive_message(self, message)

    def receive_message(self, sender, message):
        self.received_messages.append((sender, message))
        print(f"{self.id} received a message from {sender.id}")
        # Add your custom code here to handle the received message

    def listen_for_messages(self):
        while True:
            # Simulated check for incoming messages
            if self.received_messages:
                echo_count = 0
                # server/client logic when receiving PAY request
                sender, message = self.received_messages.pop(0)
                if type(message) is PayMessage: #or gettokens request:
                    # if received pay message
                    if message not in self.pending_requests:
                        self.pending_requests.add(message)
                    if not self.current_request:
                        self.current_request = message
                    self.token_info[message.token_id] = (message.owner, message.version)

                    #send message to all servers
                    for server in AllEntities().get_servers():
                        echo_pay = EchoPayMessage(self.id, message)
                        self.send_message(recipient=server, message=echo_pay)

                elif type(message) is EchoPayMessage and message.pay_message == self.current_request:
                    echo_count += 1

                if echo_count >= (AllEntities().server_num - AllEntities().faulty_num):
                    self.pending_requests.remove(message)
                    self.current_request = None
                    self.send_message(sender, StatusCode.OK)
                    print(f"{self.id} says: i got {echo_count} echos")



    def start_listening(self):
        # Start listening for messages in a separate thread
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
