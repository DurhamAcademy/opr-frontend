import socket


class SocketClient:
    def __init__(self, host='localhost', port=55001):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")

    def send_command(self, command):
        if self.client_socket:
            self.client_socket.sendall(command.encode('utf-8'))
            # response = self.client_socket.recv(1024)
            # return response.decode('utf-8')
            return
        else:
            return "Not connected to server"

    def close(self):
        if self.client_socket:
            self.client_socket.close()
            print("Connection closed")