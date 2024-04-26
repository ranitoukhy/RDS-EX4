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
        self.orig_message = pay_message

class GetTokensMessage(Message):
    def __init__(self, owner, sender):
        super().__init__(sender)
        self.owner = owner


class EchoGetTokensMessage(Message):
    def __init__(self, sender_id, get_tokens_message: GetTokensMessage, tokens_info: dict):
        super().__init__(sender_id)
        self.orig_message = get_tokens_message
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
        if type(message) is PayMessage:
            print(f"{self.id} received a pay message from {sender.id}")
        if type(message) is GetTokensMessage:
            print(f"{self.id} received a getTokens message from {sender.id}")
        if type(message) is GetTokensResponse:
            print(f"{self.id} received a getTokensResponse message from {sender.id}")
        if type(message) is EchoPayMessage:
            print(f"{self.id} received an echo pay message from {sender.id}")
        if type(message) is EchoGetTokensMessage:
            print(f"{self.id} received an echo getTokens message from {sender.id}")
        if type(message) is GetTokensUpdateRequest:
            print(f"{self.id} received an getTokensUpdateRequest message from {sender.id}")
        if type(message) is StatusCode:
            print(f"{self.id} received a status code message from {sender.id}")

    def listen_for_messages(self):
        echo_pay_messages = []
        echo_get_messages = []
        get_token_update_requests = []
        done = False
        while True:
            # Simulated check for incoming messages
            if self.received_messages:
                # server/client logic when receiving PAY request
                sender, message = self.received_messages.pop(0)
                is_messgae_a_request = type(message) is PayMessage or type(message) is GetTokensMessage
                if (sender, message) not in self.pending_requests and is_messgae_a_request:
                    #move the new request from received messages to pending requests
                    self.pending_requests.append((sender, message))


                #if the message is not a new pay or gettokens request
                elif type(messgae) is EchoPayMessage:
                        print (f"{self.id} says: i appended an echo pay message from {sender.id}")
                        echo_pay_messages.append((sender, message))
                elif type(message) is EchoGetTokensMessage:
                        print (f"{self.id} says: i appended an echo get tokens message from {sender.id}")

                        echo_get_messages.append((sender, message))
                elif type(message) is GetTokensUpdateRequest:
                        self.tokens_info = message.tokens_info
                print (f"{self.id} says: i received so far:{len(self.pending_requests) } request messages , {len(echo_pay_messages)} echo pay messages, {len(echo_get_messages)} echo get messages, {len(get_token_update_requests)} get token update requests")
                if not self.current_request:
                    self.current_request = self.pending_requests.pop(0)
                    done = False
                    print(f"{self.id} says: initialized parameters")


                if type(self.current_request[1]) is PayMessage:
                    # if received pay message
                    if not done:
                        current_owner, current_version = self.tokens_info[self.current_request[1].token_id]
                        if self.current_request[1].version > current_version:
                            self.tokens_info[message.token_id] = (self.current_request[1].owner, self.current_request[1].version)
                        #send message to all servers
                        for server in AllEntities().get_servers():
                            echo_pay = EchoPayMessage(self.id, self.current_request[1])
                            print (f"{self.id} says: sending echo pay message to {server.id}")

                            self.send_message(recipient=server, message=echo_pay)
                        print (f"{self.id} says: done pay request, waiting for echos")
                        done = True

                    relevant_echos = self.filter_echos_for_current_request(echo_pay_messages)
                    print (f"{self.id} says: {len(relevant_echos)} pay echos received")

                    if len(relevant_echos) >= (AllEntities().server_num - AllEntities().faulty_num):
                        self.send_message(self.current_request[0], StatusCode.OK)
                        self.pending_requests.remove(message)
                        echo_pay_messages = [echo for echo in echo_pay_messages if echo not in relevant_echos]
                        self.current_request = None


                if type(self.current_request[1]) is GetTokensMessage:
                    # if received getTokens message - send echo message to all servers
                    if not done:
                        for server in AllEntities().get_servers():
                            echo_get_tokens = EchoGetTokensMessage(self.id, self.current_request[1], self.tokens_info)
                            print (f"{self.id} says: sending echo get tokens message to {server.id}")
                            self.send_message(recipient=server, message=echo_get_tokens)
                        print (f"{self.id} says: done gettokens request, waiting for echos")
                        done = True

                    relevant_echos = self.filter_echos_for_current_request(echo_get_messages)
                    print (f"{self.id} says: {len(relevant_echos)} gettokens echos received")
                    if len(relevant_echos) >= (AllEntities().server_num - AllEntities().faulty_num):
                        most_updated_tokens_ds = self.choose_most_updated_tokens_ds(echo_get_messages)
                        self.tokens_info = most_updated_tokens_ds
                        self.get_tokens_send_info_to_client_and_servers(message.owner)
                        self.pending_requests.remove(message)
                        echo_get_messages = [echo for echo in echo_get_messages if echo not in relevant_echos]

                        self.current_request = None




    def filter_echos_for_current_request(self, echo_messages):
        #filter echo messages by current request
        print("1111111")
        filtered_echos = [echo for echo in echo_messages if echo.orig_message == self.current_request[1]]
        print("2222222")
        return filtered_echos
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
