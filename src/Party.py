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

class GetTokensMessage(Message):
    def __init__(self, owner, sender):
        super().__init__(sender)
        self.owner = owner


class EchoGetTokensMessage(Message):
    def __init__(self, sender_id, get_tokens_message: GetTokensMessage, tokens_info: dict):
        super().__init__(sender_id)
        self.get_tokens_message = get_tokens_message
        self.tokens_info = tokens_info

class GetTokensResponse(Message):
    def __init__(self, tokens_info, owner, sender):
        super().__init__(sender)
        self.tokens_info = tokens_info
        self.owner = owner

class GetTokensUpdateRequest(Message):
    def __init__(self, sender, tokens_info: dict):
        super().__init__(sender)
        self.tokens_info = tokens_info
class Party:
    def __init__(self, id, party_type: PartyType):
        self.id = id
        self.tokens = {}
        self.party_type = party_type
        self.pending_requests = []
        self.current_request = None
        self.received_messages = []
        self.sent_messages = []
        self.tokens_info = {}



    def pay(self, token_id, version, owner_id):
        pay_request = PayMessage(token_id, version, owner_id, self.id)
        self.sent_messages.append(pay_request)

        for server in AllEntities().get_servers():
            print(f"{self.id} says: sending pay message to {server.id}")
            self.send_message(recipient=server, message=pay_request)

        self.sent_messages.remove(pay_request)

    def getTokens(self, owner_id):
        getTokensRequest = GetTokensMessage(owner_id, self.id)
        self.sent_messages.append(getTokensRequest)

        for server in AllEntities().get_servers():
            print(f"{self.id} says: sending getTokens message to {server.id}\n")
            self.send_message(recipient=server, message=getTokensRequest)

        self.sent_messages.remove(getTokensRequest)

    def choose_most_updated_tokens_ds(self, list_of_get_echos):
        token_info_ds_list = []
        for echo in list_of_get_echos:
            token_info_ds_list.append(echo.tokens_info)
        #go over all tokens_info in token_info_ds_list and for each token with the same token_id choose the one with the highest version
        most_updated_tokens_ds = {}
        for token_info_ds in token_info_ds_list:
            for token_id, token_info in token_info_ds.items():
                if token_id in most_updated_tokens_ds:
                    if token_info[1] > most_updated_tokens_ds[token_id][1]:
                        most_updated_tokens_ds[token_id] = token_info
                else:
                    most_updated_tokens_ds[token_id] = token_info
        return most_updated_tokens_ds

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
        echo_count_pay = 0
        echo_count_get = []
        while True:
            # Simulated check for incoming messages
            if self.received_messages:
                echo_count_pay = 0
                echo_count_get = []
                # server/client logic when receiving PAY request
                sender, message = self.received_messages.pop(0)

                if (sender, message) not in self.pending_requests:
                    self.pending_requests.append((sender, message))
                if not self.current_request:
                    self.current_request = self.pending_requests.pop(0)
                    echo_count_pay = 0
                    echo_count_get = []
                    print(f"{self.id} says: initialized parameters")
                if type(message) is PayMessage:
                    # if received pay message
                    current_owner, current_version = self.tokens_info[message.token_id]
                    if message.version > current_version:
                        self.tokens_info[message.token_id] = (message.owner, message.version)

                    #send message to all servers
                    for server in AllEntities().get_servers():
                        echo_pay = EchoPayMessage(self.id, message)
                        self.send_message(recipient=server, message=echo_pay)

                if type(message) is EchoPayMessage and message.pay_message == self.current_request:
                    echo_count_pay += 1

                if echo_count_pay >= (AllEntities().server_num - AllEntities().faulty_num):
                    self.pending_requests.remove(message)
                    self.current_request = None
                    self.send_message(sender, StatusCode.OK)
                    print(f"{self.id} says: i got {echo_count_pay} echos")

                if type(message) is GetTokensMessage:
                    print(f"{self.id} says: got gettokens message")
                    # if received getTokens message - send echo message to all servers
                    for server in AllEntities().get_servers():
                        echo_get_tokens = EchoGetTokensMessage(self.id, message, self.tokens_info)
                        self.send_message(recipient=server, message=echo_get_tokens)

                if type(message) is EchoGetTokensMessage and message.get_tokens_message == self.current_request[1]:
                    echo_count_get.append(message)
                    print(f"{self.id} says: echo_count_get length is {len(echo_count_get)}")
                    if len(echo_count_get) >= (AllEntities().server_num - AllEntities().faulty_num):
                        print(f"{self.id} says: got EchoGetTokensMessage from {sender}")
                        most_updated_tokens_ds = self.choose_most_updated_tokens_ds(echo_count_get)
                        self.tokens_info = most_updated_tokens_ds
                        self.get_tokens_send_info_to_client_and_servers(message.get_tokens_message.owner)
                        self.pending_requests.remove(message)
                        self.current_request = None

                        print(
                            f"{self.id} says: i got {len(echo_count_get)} echos and sent most updated tokens_info to client")

                if type(message) is GetTokensUpdateRequest:
                    self.tokens_info = message.tokens_info


    def filter_tokens_by_owner(self, owner_id):
        #filter tokens_info by owner
        filtered_dict = {token_id: (owner, version) for token_id, (owner, version) in self.tokens_info.items() if owner == owner_id}
        for token_id in filtered_dict.keys():
            print(f"token id {token_id}: owned by {filtered_dict[token_id][0]} with version {filtered_dict[token_id][1]}")
        return filtered_dict

    def get_tokens_send_info_to_client_and_servers(self, owner):
        #return the tokens that belong to the owner in the client request
        get_tokens_response_message = GetTokensResponse(self.filter_tokens_by_owner(owner), owner, self.id)
        self.send_message(self.current_request[0], get_tokens_response_message)

        get_tokens_update_request = GetTokensUpdateRequest(self, self.tokens_info)

        for server in AllEntities().get_servers():
            self.send_message(server, get_tokens_update_request)




    def start_listening(self):
        # Start listening for messages in a separate thread
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
