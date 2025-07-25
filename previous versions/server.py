import socket
import threading
from constants.config import *
from sql.manageSQL import add_message, load_chat

class ChatServer:
    def __init__(self, port, host=socket.gethostbyname(socket.gethostname())):
        self.port = port
        self.host = host
        self.addr = (self.host, self.port)
        self.server_socket = None
        self.clients = {}

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.addr)
        self.server_socket.listen()

        print(f"Server listening on {self.host}:{self.port}")

        try:
            while True:
                conn, addr = self.server_socket.accept()
                print(f"New connection from {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def update_user_list(self):
        user_list = list(self.clients.values())
        self.broadcast(f"{USER_LIST_UPDATE}:{','.join(user_list)}")

    def broadcast(self, message):
        print(f"Broadcasting: {message}")
        disconnected_clients = []

        for client in list(self.clients.keys()):
            try:
                client.send(message.encode(FORMAT))
            except Exception:
                print(f"Failed to send message to {self.clients.get(client, 'unknown')}")
                disconnected_clients.append(client)

        for client in disconnected_clients:
            if client in self.clients:
                del self.clients[client]

        if disconnected_clients:
            self.update_user_list()

        add_message(message)
        

    def handle_client(self, conn, addr):
        username = self.register_username(conn)
        if not username:
            return

        self.clients[conn] = username
        self.update_user_list()

        print(f"User {username} registered from {addr}")

        chat_history = load_chat()
        full_history = "\n".join(chat_history)
        conn.send(full_history.encode(FORMAT))

        try:
            while True:
                message = conn.recv(HEADER).decode(FORMAT)
                if not message:
                    break

                if message == DISCONNECT_MESSAGE:
                    print(f"User {username} disconnected")
                    break

                self.process_message(conn, username, message)

        except Exception as e:
            print(f"Error handling client {username}: {e}")
        finally:
            if conn in self.clients:
                del self.clients[conn]
            self.update_user_list()
            conn.close()
            print(f"Connection with {username} closed")

    def register_username(self, conn):
        while True:
            try:
                username = conn.recv(HEADER).decode(FORMAT)
                if not username:
                    return None

                if username in self.clients.values():
                    conn.send(USERNAME_TAKEN.encode(FORMAT))
                else:
                    conn.send(USERNAME_ACCEPTED.encode(FORMAT))
                    return username
            except Exception as e:
                print(f"Error during username registration: {e}")
                return None

    def process_message(self, conn, sender, message):
        words = message.strip().split()

        if len(words) >= 3 and words[0] == WHISPER_CMD:
            self.handle_whisper(conn, sender, words[1], ' '.join(words[2:]))
        elif len(words) >= 3 and words[0] == DM_CMD:
            self.handle_direct_message(conn, sender, words[1], ' '.join(words[2:]))
        else:
            self.broadcast(f"[{sender}]: {message}")

    def handle_whisper(self, sender_conn, sender_name, recipient_name, message):
        if recipient_name not in self.clients.values():
            sender_conn.send(f"User {recipient_name} not found.".encode(FORMAT))
            return

        print(f"Whisper from {sender_name} to {recipient_name}: {message}")

        for client, name in self.clients.items():
            if name == recipient_name:
                client.send(f"[Whisper from {sender_name}]: {message}".encode(FORMAT))
                sender_conn.send(f"[Whisper to {recipient_name}]: {message}".encode(FORMAT))
                break

    def handle_direct_message(self, sender_conn, sender_name, recipient_name, message):
        if recipient_name not in self.clients.values():
            sender_conn.send(f"User {recipient_name} not found.".encode(FORMAT))
            return

        print(f"DM from {sender_name} to {recipient_name}: {message}")

        for client, name in self.clients.items():
            if name == recipient_name:
                client.send(f"DM [{sender_name}]: {message}".encode(FORMAT))
                break

if __name__ == "__main__":
    port = int(input("Enter server-port (user requires it for connection): "))
    server = ChatServer(port=port)
    server.start()