class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AllEntities(metaclass=Singleton):
    def __init__(self):
        self.servers = {}
        self.clients = {}
        self.tokens = dict()
        self.server_num = 0
        self.client_num = 0
        self.faulty_num = 0

    def add_server(self, server):
        self.servers[server.id] = server

    def add_client(self, client):
        self.clients[client.id] = client

    def remove_server(self, server):
        self.servers.pop(server.id, None)

    def remove_client(self, client):
        self.clients.pop(client.id, None)

    def add_token(self, token):
        self.tokens[token.id] = token

    def get_servers(self):
        return self.servers.values()

    def get_clients(self):
        return self.clients.values()

    # for initialization purposes only
    def get_tokens(self):
        return self.tokens.values()

    def print_data(self):
        for server in list(self.get_servers()):
            for token in server.token_info.keys():
                print(f"{server.id} says : {token} belongs to {server.token_info[token][0]} version {server.token_info[token][1]}")

    def set_server_num(self, server_num):
        self.server_num = server_num

    def set_client_num(self, client_num):
        self.client_num = client_num

    def set_faulty_num(self, faulty_num):
        self.faulty_num = faulty_num

