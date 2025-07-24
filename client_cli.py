import socket
import threading
import sys
from constants.config import * 

class CLIBotClient:
    def __init__(self, server_ip, server_port, username="bot_user"):
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_addr = (server_ip, server_port)
        self.socket = None
        self.username = username
        self.connected = False

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(self.server_addr)
            self.socket.send(self.username.encode(FORMAT))
            response = self.socket.recv(HEADER).decode(FORMAT)

            if response == USERNAME_ACCEPTED:
                print(f"[INFO] Connected to {self.server_ip}:{self.server_port} as {self.username}")
                self.connected = True
                return True
            elif response == USERNAME_TAKEN:
                print("[ERROR] Username taken.")
            else:
                print("[ERROR] Server rejected connection.")
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
        return False

    def start(self):
        if self.connect():
            threading.Thread(target=self.receive_loop, daemon=True).start()
            self.send_loop()

    def receive_loop(self):
        while self.connected:
            try:
                msg = self.socket.recv(HEADER).decode(FORMAT)
                if not msg:
                    break
                elif "/USERS_WHO_TYPING:" in msg : 
                    pass
                else : 
                    print(f"\n[SERVER] {msg.strip()}")
            except Exception as e:
                print(f"[ERROR] Receiving failed: {e}")
                break
        self.disconnect()

    def send_loop(self):
        try:
            while self.connected:
                message = input("> ")
                if message.lower() in ["exit", "quit"]:
                    self.disconnect()
                    break
                self.socket.send(message.encode(FORMAT))
        except KeyboardInterrupt:
            self.disconnect()
        except Exception as e:
            print(f"[ERROR] Sending failed: {e}")
            self.disconnect()

    def disconnect(self):
        if self.connected:
            try:
                self.socket.send(DISCONNECT_MESSAGE.encode(FORMAT))
            except Exception as e:
                print(f"[WARN] Could not send disconnect message: {e}")
            finally:
                try:
                    self.socket.close()
                except:
                    pass
            print("[INFO] Disconnected.")
            self.connected = False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python cli_bot_client.py <server_ip> <port> [username]")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3] if len(sys.argv) > 3 else "bot_user"

    bot = CLIBotClient(server_ip=ip, server_port=port, username=username)
    bot.start()
