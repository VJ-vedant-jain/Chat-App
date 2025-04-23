import socket
import threading, os
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QListWidgetItem, QInputDialog
from PyQt5.QtCore import QTimer
from constants.config import *
from sql.manageSQL import add_message, load_chat
import sql.utils as serverUtil 
from ui.server.ui_server import ServerWindow

users_typing = []
banned_ips = []

class ChatServerGUI(ServerWindow):
    def __init__(self):
        """
        Initializes the chat server GUI
        Sets up button actions and starts a timer to refresh user list and prepares logging.
        """
        super().__init__()
        
        self.server = None
        self.server_thread = None
        self.running = False
        
        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)
        self.cmd_button.clicked.connect(self.execute_command)
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_user_list_ui)
        self.update_timer.start(1000)
        
        if not os.path.exists('logs'):
            os.makedirs('logs')
        with open('logs/log_server.txt', 'w') as file:
            file.write("")
            
        self.log_display.append("Server application started")

    def append_chat(self, message):
        """
        Adds a line to the Chat Log area in the GUI.
        """
        self.chat_display.append(message)

    def append_log(self, message):
        """
        Adds log messages to server's log display area
            message - (str) The message to display
        """
        self.log_display.append(message)
        
    def update_user_list_ui(self):
        """
        Updates the list of connected users shown in GUI
        """
        if self.server and hasattr(self.server, 'clients'):
            self.users_list.clear()
            for user in self.server.clients.values():
                self.users_list.addItem(user)

    def start_server(self):
        """
        Starts the chat server on port selected from the GUI SpinBox
        Literally the grandpa
        """
        port = self.port_input.value()
        try:
            self.server = ChatServer(port=port, gui=self)
            self.server_thread = threading.Thread(target=self.server.start, daemon=True)
            self.server_thread.start()
            self.running = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("Status: Running")
            self.status_label.setStyleSheet("QLabel { color: green; }")
            self.append_log(f"Server listening on {port}")
        except Exception as e:
            self.append_log(f"Failed to start server: {str(e)}")

    def stop_server(self):
        """
        Stops the running server and updates GUI to show that the server is no longer running
        Grandpa killer
        """
        if self.server and self.server.server_socket:
            self.server.server_socket.close()
            self.server = None
            self.running = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_label.setText("Status: Not Running")
            self.status_label.setStyleSheet("QLabel { color: red; }")
            self.append_log("Server stopped")
        else:
            self.append_log("No server running")

    def execute_command(self):
        """
        Executes commands entered into the GUi input box
        Some of em are /kick, /list, /ban, etc
        """
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
            
        self.append_log(f"Command: {cmd}")
        self.cmd_input.clear()
        
        if cmd == "/list":
            if self.server and hasattr(self.server, 'clients'):
                self.append_log("Connected users:")
                for user in self.server.clients.values():
                    self.append_log(f"- {user}")
            else:
                self.append_log("Server not running")
                
        elif cmd.startswith("/kick "):
            username = cmd.split(" ", 1)[1]
            self.kick_user(username)
                
        elif cmd == "/abort-server":
            self.stop_server()
            
        elif cmd == '/clear-all':
            self.clear_all_messages()
                
        elif cmd == '/prune':
            try:
                noOfMessagesPruned = int(QInputDialog.getInt(self, "Prune Messages", "Enter the number of messages:", 10)[0])
                serverUtil.prune(noOfMessagesPruned)
                self.append_log(f"Pruned {noOfMessagesPruned} messages.")
            except:
                self.append_log("Input value must be a number.")
                
        elif cmd.startswith("/ban "):
            username = cmd.split(" ", 1)[1]
            self.ban_user(username)
                
        else:
            self.append_log("Unknown command.")

    def kick_user(self, username):
        """
        Disconnects user from server depending on their username
            username - (str) The username of user to be kicked
        """
        if not self.server or not hasattr(self.server, 'clients'):
            self.append_log("Server not running")
            return
            
        for conn, user in self.server.clients:
            if user == username:
                conn.send(DISCONNECT_KICK_MESSAGE.encode(FORMAT))
                self.append_log(f"Kicked {username}")
                return
                    
        self.append_log("User not found")

    def ban_user(self, username):
        """
        Bans a user by adding their IP address to a list of banned ips
        Banned users cannot join back into the server, they are automatically kicked when they try to connect
            username - (str) Username of user to ban
        """
        if not self.server or not hasattr(self.server, 'clients'):
            self.append_log("Server not running")
            return
            
        banned_ip = None
        target_conn = None
        
        for conn, name in list(self.server.clients.items()):
            if name == username:
                ip, _ = conn.getpeername()
                banned_ip = ip
                target_conn = conn
                break
                    
        if banned_ip:
            banned_ips.append(banned_ip)
            self.append_log(f"Banned user with IP {banned_ip}")
            target_conn.send(BAN_MESSAGE.encode(FORMAT))
        else:
            self.append_log(f"User {username} not found to be banned")

    def clear_all_messages(self):
        """
        Clears all chat history from server's database after confirming with the user
        """
        reply = QMessageBox.question(self, "Clear Messages", 
                                     "Are you sure you want to clear all messages?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            serverUtil.purge()
            self.append_log("Database purged")


class ChatServer:
    def __init__(self, port, host=socket.gethostbyname(socket.gethostname()), gui=None):
        """
        Initializes the chat server with given port, host and GUI for the admin
            port - (int) The port number the server will listen on
            host - (str) Host IP address, default being the IP address of local machine
            gui - (ServerWindow, optional) GUI instance to update with server events
        """
        self.port = port
        self.host = host
        self.addr = (self.host, self.port)
        self.server_socket = None
        self.clients = {}
        self.gui = gui

    def start(self):
        """
        Starts the server, listens for incoming connections and starts a thread for each user
        Runs for the entirety of the life of the server
        Grandma
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.addr)
        self.server_socket.listen()

        self.log_debug(f"Server listening on {self.host}:{self.port}")

        try:
            while True:
                conn, addr = self.server_socket.accept()
                self.log_debug(f"New connection from {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            self.log_debug(f"Server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def update_user_list(self):
        """
        Updates list of connected users on server and broadcasts it to all connected users
        """
        user_list = list(self.clients.values())
        self.broadcast(f"{USER_LIST_UPDATE}:{','.join(user_list)}")

    def update_users_typing_list(self):
        """
        Updates list of currently typing users and broadcasts it to all users
        """
        user_typing_list = list(users_typing)
        self.broadcast(f"{IS_TYPING_LIST}:{', '.join(user_typing_list)}")

    def broadcast(self, message):
        """
        Broadcasts a message to all clients, handling disconnections 
            message - (str) message to broadcast
        """
        if not message.startswith(f"{IS_TYPING_LIST}"):
            self.log_debug(f"Broadcasting: {message}")
        disconnected_clients = []

        for client in list(self.clients.keys()):
            try:
                client.send(message.encode(FORMAT))
            except Exception:
                self.log_debug(f"Failed to send message to {self.clients.get(client, 'unknown')}")
                disconnected_clients.append(client)

        for client in disconnected_clients:
            if client in self.clients:
                del self.clients[client]

        if disconnected_clients:
            self.update_user_list()
        
        if self.gui and not message.startswith((USER_LIST_UPDATE, IS_TYPING_LIST)):
            self.gui.append_chat(message)

        if not message.startswith((USER_LIST_UPDATE, IS_TYPING_LIST)):
            add_message(message)

    def handle_client(self, conn, addr):
        """
        Handles comms with connected client. Includes receiving messages, processing em, and handling client disconnects
        Also kicks user if he has been banned previously
            conn - (socket) connection object of the client
            addr - (tuple) address of the client (IP, port)
        """
        ip, _ = addr
        if ip in banned_ips:
            conn.send(DISCONNECT_KICK_MESSAGE.encode(FORMAT))
            conn.close()
            self.log_debug(f"Banned user with ip {ip} tried joining. Rejected")
            return

        username = self.register_username(conn)
        if not username:
            return

        self.clients[conn] = username
        self.update_user_list()

        self.log_debug(f"User {username} registered from {addr}")

        chat_history = load_chat()
        fixed_history = []
        for msg in chat_history:
            if msg.startswith("[[") and "]:]: " in msg:
                fixed_msg = msg.replace("[[", "[").replace("]:]: ", "]: ")
                fixed_history.append(fixed_msg)
            else:
                fixed_history.append(msg)
        
        full_history = "\n".join(fixed_history)
        conn.send(full_history.encode(FORMAT))

        if self.gui and fixed_history:
            for line in fixed_history:
                self.gui.append_chat(line)

        try:
            while True:
                message = conn.recv(HEADER).decode(FORMAT)
                if not message:
                    break

                if message == DISCONNECT_MESSAGE:
                    self.log_debug(f"User {username} disconnected")
                    break

                self.process_message(conn, username, message)

        except Exception as e:
            self.log_debug(f"Error handling client {username}: {e}")
        finally:
            if conn in self.clients:
                del self.clients[conn]
            self.update_user_list()
            conn.close()
            self.log_debug(f"Connection with {username} closed")

    def register_username(self, conn):
        """
        Registers a username for new clients by checking if its already been taken or not
        If taken, client will be prompted to enter a different one.
            conn - (socket) Connection object of the client
        
            returns str or none: Registered username, or none if registration fails
        """
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
                self.log_debug(f"Error during username registration: {e}")
                return None

    def process_message(self, conn, sender, message):
        """
        Processes received messages from clients, identifying some special commands like whisper, dm, broadcasts, etc
            conn - (socket) Connection object of client
            sender - (str) Username of sender
            message - (str) Message to process
        """
        words = message.strip().split()

        if len(words) >= 3 and words[0] == WHISPER_CMD:
            self.handle_whisper(conn, sender, words[1], ' '.join(words[2:]))
        elif len(words) >= 3 and words[0] == DM_CMD:
            self.handle_direct_message(conn, sender, words[1], ' '.join(words[2:]))
        elif len(words) >= 2 and words[0] == IS_TYPING:
            user = ' '.join(words[1:])
            if user not in users_typing:
                users_typing.append(user)
            self.update_users_typing_list()
        elif len(words) >= 2 and words[0] == NOT_TYPING:
            user = ' '.join(words[1:])
            if user in users_typing:
                users_typing.remove(user)
            self.update_users_typing_list()
        else:
            self.broadcast(f"[{sender}]: {message}")

    def handle_whisper(self, sender_conn, sender_name, recipient_name, message):
        """
        Sends whisper from one user to another
            sender_conn - (socket) Connection object of sender
            sender_name - (str) username of sender
            recipient_name - (str) username of recepient
            message - (str) Message to be sent to recipient
        """
        if recipient_name not in self.clients.values():
            sender_conn.send(f"User {recipient_name} not found.".encode(FORMAT))
            return

        self.log_debug(f"Whisper from {sender_name} to {recipient_name}: {message}")

        for client, name in self.clients.items():
            if name == recipient_name:
                client.send(f"[Whisper from {sender_name}]: {message}".encode(FORMAT))
                sender_conn.send(f"[Whisper to {recipient_name}]: {message}".encode(FORMAT))
                break

    def handle_direct_message(self, sender_conn, sender_name, recipient_name, message):
        """
        Sends a DM from one user to another
            sender_conn - (socket) Connection object of sender
            sender_name - (str) username of sender
            recipient_name - (str) username of recepient
            message - (str) Message to be sent to recipient
        """
        if recipient_name not in self.clients.values():
            sender_conn.send(f"User {recipient_name} not found.".encode(FORMAT))
            return

        self.log_debug(f"DM from {sender_name} to {recipient_name}: {message}")

        for client, name in self.clients.items():
            if name == recipient_name:
                client.send(f"DM [{sender_name}]: {message}".encode(FORMAT))
                break

    def log_debug(self, message):
        """
        Logs a debug message to server's log file and updates gui with message
            message - (str) Message to log
        """
        with open('logs/log_server.txt', 'a') as file:
            file.write(message + "\n\n")
            
        if self.gui:
            self.gui.append_log(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    server_gui = ChatServerGUI()
    server_gui.show()
    sys.exit(app.exec_())