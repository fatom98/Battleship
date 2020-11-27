import socket
import threading
import os


class TCP:
    def __init__(self):
        self.clients_list = list()
        self.message = ""
        self.match = 0
        self.connect()

    def connect(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        IP = "192.168.1.49"
        PORT = 54321
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.bind((IP, PORT))
        self.soc.listen(5)

        print("Listening for connection")
        self.threat()

    def threat(self):
        while True:
            client = so, (ip, port) = self.soc.accept()
            if client not in self.clients_list:
                self.clients_list.append(client)
            print(f'{ip} connected from {port}')

            thread = threading.Thread(target=self.receive, args=(so, ))
            thread.start()

    def receive(self, so):

        while True:
            self.message = so.recv(1024)
            self.broadcast(so)

    def broadcast(self, so):

        for client in self.clients_list:
            soc = client[0]
            if soc is not so:
                soc.send(self.message)


if __name__ == '__main__':
    TCP()
