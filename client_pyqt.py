import socket
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QComboBox, QLabel, QDialog
)
from PyQt6.QtCore import QTimer, Qt
from config import *
import sys

class DMWindow(QDialog):
    def __init__(self, target, send_dm_callback, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"DM with {target}")
        self.resize(400, 300)
        self.send_dm_callback = send_dm_callback
        self.target = target

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)

        self.entry = QLineEdit()
        self.entry.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_box)
        layout.addWidget(self.entry)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def send_message(self):
        message = self.entry.text().strip()
        if message:
            self.send_dm_callback(self.target, message)
            self.chat_box.append(f"You -> {self.target}: {message}")
            self.entry.clear()

    def display_message(self, message):
        self.chat_box.append(message)


class ChatClient(QMainWindow):
    def __init__(self, server_ip, server_port):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_addr = (server_ip, server_port)

        self.username = None
        self.socket = None
        self.connected = False
        self.message_queue = []
        self.dm_windows = {}

        self.setWindowTitle("Chat Client")
        self.resize(700, 500)

        self.setup_gui()

        if self.connect():
            self.start_receiving()
            self.timer = QTimer()
            self.timer.timeout.connect(self.process_message_queue)
            self.timer.start(100)
        else:
            self.close()

    def setup_gui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()

        # Left panel
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Chat with:"))

        self.user_dropdown = QComboBox()
        self.user_dropdown.addItem("Global Chat")
        left_panel.addWidget(self.user_dropdown)

        self.dm_button = QPushButton("Open DM")
        self.dm_button.clicked.connect(self.open_selected_dm)
        left_panel.addWidget(self.dm_button)

        layout.addLayout(left_panel, 1)

        # Right panel
        right_panel = QVBoxLayout()

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        right_panel.addWidget(self.chat_box)

        self.message_entry = QLineEdit()
        self.message_entry.returnPressed.connect(self.send_from_main)
        right_panel.addWidget(self.message_entry)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_from_main)
        right_panel.addWidget(self.send_button)

        layout.addLayout(right_panel, 4)

        central_widget.setLayout(layout)

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(self.server_addr)
            while True:
                from PyQt6.QtWidgets import QInputDialog
                username, ok = QInputDialog.getText(self, "Username", "Enter your username:")
                if not ok:
                    self.socket.close()
                    return False
                self.username = username
                self.socket.send(self.username.encode(FORMAT))
                response = self.socket.recv(HEADER).decode(FORMAT)
                if response == USERNAME_ACCEPTED:
                    self.connected = True
                    return True
                elif response == USERNAME_TAKEN:
                    continue
                else:
                    self.socket.close()
                    return False
        except Exception:
            if self.socket:
                self.socket.close()
            return False

    def start_receiving(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while self.connected:
            try:
                message = self.socket.recv(HEADER).decode(FORMAT)
                if not message:
                    break
                messages = message.split("\n")
                for msg in messages:
                    self.message_queue.append(msg)
            except:
                break

    def process_message_queue(self):
        while self.message_queue:
            message = self.message_queue.pop(0)
            if message.startswith(f"{USER_LIST_UPDATE}:"):
                user_list = message[len(f"{USER_LIST_UPDATE}:"):].split(',')
                if self.username in user_list:
                    user_list.remove(self.username)
                self.update_user_dropdown(user_list)
            elif message.startswith("DM "):
                self.handle_direct_message(message)
            else:
                self.display_message(message)

    def update_user_dropdown(self, user_list):
        current = self.user_dropdown.currentText()
        self.user_dropdown.clear()
        self.user_dropdown.addItem("Global Chat")
        self.user_dropdown.addItems(user_list)
        if current in user_list:
            self.user_dropdown.setCurrentText(current)
        else:
            self.user_dropdown.setCurrentText("Global Chat")

    def send_from_main(self):
        message = self.message_entry.text().strip()
        if message:
            self.send_message(message)
            self.message_entry.clear()

    def send_dm_callback(self, target, message):
        try:
            self.socket.send(f"{DM_CMD} {target} {message}".encode(FORMAT))
        except:
            pass

    def send_message(self, message):
        try:
            if message.startswith(f"{DM_CMD} "):
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    return
                recipient, msg_content = parts[1], parts[2]
                self.send_dm_callback(recipient, msg_content)
            else:
                self.socket.send(message.encode(FORMAT))
        except:
            pass

    def display_message(self, message):
        self.chat_box.append(message)

    def handle_direct_message(self, message):
        try:
            parts = message.split("]: ", 1)
            if len(parts) != 2:
                return
            sender_part = parts[0]
            if not sender_part.startswith("DM ["):
                return
            sender = sender_part[4:].strip('[]')
            if sender not in self.dm_windows:
                self.create_dm_window(sender)
            self.dm_windows[sender].display_message(message)
        except:
            pass

    def open_selected_dm(self):
        selected = self.user_dropdown.currentText()
        if selected != "Global Chat":
            self.create_dm_window(selected)

    def create_dm_window(self, target):
        if target not in self.dm_windows:
            dm_window = DMWindow(target, self.send_dm_callback)
            self.dm_windows[target] = dm_window
            dm_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ip = input("Enter server IP: ")
    port = int(input("Enter port: "))
    client = ChatClient(server_ip=ip, server_port=port)
    client.show()
    sys.exit(app.exec())
