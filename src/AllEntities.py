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
        self.tokens = {}

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
        return self.servers

    def get_clients(self):
        return self.clients

    def print_data(self):
        for client in self.clients.values():
            print(f"client id = {client.id}")
            print(f"client tokens = {[(token.id, token.version, token.owner) for token in client.tokens.values()]}")
            print("\n\n")
