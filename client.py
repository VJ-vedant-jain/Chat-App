import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, ttk
from config import *

class ChatClient:
    def __init__(self, server_ip="localhost", server_port=PORT):
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_addr = (server_ip, server_port)
        self.username = None
        self.socket = None
        self.connected = False
        self.message_queue = []
        self.last_sent_messages = []
        self.root = None
        self.chat_box = None
        self.message_entry = None
        self.user_dropdown = None
        self.dm_windows = {}

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(self.server_addr)
            while True:
                self.username = simpledialog.askstring("Username", "Enter your username")
                if not self.username:
                    self.socket.close()
                    return False
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

    def disconnect(self):
        if self.connected:
            try:
                self.socket.send(DISCONNECT_MESSAGE.encode(FORMAT))
                self.connected = False
                self.socket.close()
            except Exception:
                pass

    def start_receiving(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while True:
            try:
                message = self.socket.recv(PORT).decode(FORMAT)
                if not message:
                    break
                messages = message.split("\n")
                for msg in messages:
                    self.message_queue.append(msg)
            except:
                print("Error receiving message.")
                break

    def process_message_queue(self):
        try:
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
        except Exception:
            pass
        if self.root and self.root.winfo_exists():
            self.root.after(100, self.process_message_queue)

    def handle_direct_message(self, message):
        try:
            parts = message.split("]: ", 1)
            if len(parts) != 2:
                return
            sender_part = parts[0]
            if not sender_part.startswith("DM ["):
                return
            sender = sender_part[4:].strip('[]')
            if sender != self.username and sender not in self.dm_windows:
                self.create_dm_window(sender)
            if sender in self.dm_windows:
                self.display_dm_message(sender, message)
            elif sender != self.username:
                self.create_dm_window(sender)
                self.display_dm_message(sender, message)
        except Exception:
            pass

    def display_message(self, message):
        if self.chat_box:
            self.chat_box.config(state=tk.NORMAL)
            self.chat_box.insert(tk.END, message + '\n')
            self.chat_box.config(state=tk.DISABLED)
            self.chat_box.yview(tk.END)

    def display_dm_message(self, target, message):
        if target in self.dm_windows:
            dm_info = self.dm_windows[target]
            chat_box = dm_info['chat_box']
            chat_box.config(state=tk.NORMAL)
            chat_box.insert(tk.END, message + '\n')
            chat_box.config(state=tk.DISABLED)
            chat_box.yview(tk.END)

    def update_user_dropdown(self, user_list):
        if self.user_dropdown:
            current_selection = self.user_dropdown.get()
            self.user_dropdown['values'] = ["Global Chat"] + user_list
            if current_selection not in user_list and current_selection != "Global Chat":
                self.user_dropdown.set("Global Chat")

    def send_message(self, message):
        try:
            if message.startswith(f"{DM_CMD} "):
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    return
                recipient, msg_content = parts[1], parts[2]
                self.socket.send(f"{DM_CMD} {recipient} {msg_content}".encode(FORMAT))
                self.last_sent_messages.append(f"DM [{recipient}]: {msg_content}")
            else:
                self.socket.send(message.encode(FORMAT))
        except Exception:
            pass

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title(f"Chat App - {self.username}")
        self.root.geometry("700x500")

        left_frame = tk.Frame(self.root, width=150)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text="Chat with:").pack(anchor=tk.W, pady=(0, 5))
        self.user_dropdown = ttk.Combobox(left_frame, state="readonly")
        self.user_dropdown.pack(anchor=tk.N, fill=tk.X)
        self.user_dropdown.set("Global Chat")

        dm_button = tk.Button(left_frame, text="Open DM", command=self.open_selected_dm)
        dm_button.pack(anchor=tk.N, fill=tk.X, pady=5)

        main_frame = tk.Frame(self.root)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        self.chat_box = scrolledtext.ScrolledText(main_frame, state=tk.DISABLED, wrap=tk.WORD)
        self.chat_box.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.message_entry = tk.Entry(main_frame, font=("Arial", 10))
        self.message_entry.pack(padx=5, pady=5, fill=tk.X)

        send_button = tk.Button(main_frame, text="Send", command=self.send_from_main)
        send_button.pack(pady=5)

        self.root.after(100, self.process_message_queue)

    def send_from_main(self):
        message = self.message_entry.get()
        if message:
            self.send_message(message)
            self.message_entry.delete(0, tk.END)

    def open_selected_dm(self):
        selected = self.user_dropdown.get()
        if selected != "Global Chat":
            self.create_dm_window(selected)

    def create_dm_window(self, target):
        if target in self.dm_windows:
            return

        dm_window = tk.Toplevel(self.root)
        dm_window.title(f"DM with {target}")
        dm_window.geometry("400x400")

        dm_window.grid_rowconfigure(0, weight=1)
        dm_window.grid_columnconfigure(0, weight=1)

        chat_box = scrolledtext.ScrolledText(dm_window, state=tk.DISABLED, wrap=tk.WORD)
        chat_box.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        entry = tk.Entry(dm_window, font=("Arial", 10))
        entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        def send_dm():
            message = entry.get()
            if message:
                self.send_message(f"{DM_CMD} {target} {message}")
                self.display_dm_message(target, f"You -> {target}: {message}")
                entry.delete(0, tk.END)

        send_button = tk.Button(dm_window, text="Send", command=send_dm)
        send_button.grid(row=1, column=1, padx=5, pady=5)

        self.dm_windows[target] = {"window": dm_window, "chat_box": chat_box}

    def start(self):
        if self.connect():
            self.setup_gui()
            self.start_receiving()
            self.root.mainloop()

if __name__ == "__main__":
    SERVER_IP = str(input("Enter server-ip: "))
    client = ChatClient(server_ip=SERVER_IP)
    client.start()