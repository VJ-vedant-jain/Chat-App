import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, ttk
from config import *

class ChatClient:
    """
    A class for clients
    """

    def __init__(self, server_port, server_ip="localhost"):
        """
        Initializing many many stuffs :skull:
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_addr = (server_ip, server_port)
        self.username = None
        self.socket = None
        self.connected = False
        self.message_queue = []
        self.root = None
        self.chat_box = None
        self.message_entry = None
        self.user_dropdown = None
        self.dm_windows = {}

    def connect(self):
        """
        Connects the user to the server
        1. asks user for username and conveys it to server and checks response of server if username taken or nah
        2. but uhh if any error comes (sadly) then just closes the program :)
        """
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
        """
        Disconnects user from server through the disconnect message
        """
        if self.connected:
            try:
                self.socket.send(DISCONNECT_MESSAGE.encode(FORMAT))
                self.connected = False
                self.socket.close()
            except Exception:
                pass

    def start_receiving(self):
        """
        just as it sounds. starts a thread to receive messages cuz well python cant do multiple tings at the same time :/
        """
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        """
        receives messages from server and adds them to the queue to send messages so well... we can send them?
        """
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
        """
        well if there is some tings in the message queue, it sends them to the server... maybe?
        """
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
        """
        so if when the user receives message from server startin with "DM [<username>]" 
        then if the dm window exists, sends message there and if it doesn't exist, well, it creates one and then sends.
        """
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
        """
        appends received message to the chat_box (foooorrrr global chat)?
        """
        if self.chat_box:
            self.chat_box.config(state=tk.NORMAL)
            self.chat_box.insert(tk.END, message + '\n')
            self.chat_box.config(state=tk.DISABLED)
            self.chat_box.yview(tk.END)

    def display_dm_message(self, target, message):
        """
        appends received message to dm_window maybe
        if the DM window doesn't exist, it's created inside `handle_direct_message()`
        """
        if target in self.dm_windows:
            dm_info = self.dm_windows[target]
            chat_box = dm_info['chat_box']
            chat_box.config(state=tk.NORMAL)
            chat_box.insert(tk.END, message + '\n')
            chat_box.config(state=tk.DISABLED)
            chat_box.yview(tk.END)

    def update_user_dropdown(self, user_list):
        """
        updates user dropdown, if selected user... leaves... sets selection to Global Chat
        """
        if self.user_dropdown:
            current_selection = self.user_dropdown.get()
            self.user_dropdown['values'] = ["Global Chat"] + user_list
            if current_selection not in user_list and current_selection != "Global Chat":
                self.user_dropdown.set("Global Chat")

    def send_message(self, message):
        """
        checks if the message HAS the DM_CMD if yes, sends the DM
        if no, its goes to the server to decide if its a whispher or broadcast and sends accordingly
        """
        try:
            if message.startswith(f"{DM_CMD} "):
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    return
                recipient, msg_content = parts[1], parts[2]
                self.socket.send(f"{DM_CMD} {recipient} {msg_content}".encode(FORMAT))
            else:
                self.socket.send(message.encode(FORMAT))
        except Exception:
            pass

    def setup_gui(self):
        """
        does the gui *magic*
        """
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
        self.message_entry.bind("<Return>", lambda event: self.send_from_main())

        send_button = tk.Button(main_frame, text="Send", command=self.send_from_main)
        send_button.pack(pady=5)

        self.root.after(100, self.process_message_queue)

    def send_from_main(self):
        """
        collects message from the message entry and then uhh passes it to the send_message() function and well its job is done
        """
        message = self.message_entry.get()
        if message:
            self.send_message(message)
            self.message_entry.delete(0, tk.END)

    def open_selected_dm(self):
        """
        opens the dm window user selects :)
        """
        selected = self.user_dropdown.get()
        if selected != "Global Chat":
            self.create_dm_window(selected)

    def create_dm_window(self, target):
        """
        Creates the dm window for chatting :)
        """
        if target in self.dm_windows:
            self.dm_windows.pop(target)

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
            """
            sends uhh dm?
            """
            message = entry.get()
            if message:
                self.send_message(f"{DM_CMD} {target} {message}")
                self.display_dm_message(target, f"You -> {target}: {message}")
                entry.delete(0, tk.END)


        entry.bind("<Return>", lambda event: send_dm())
        send_button = tk.Button(dm_window, text="Send", command=send_dm)
        send_button.grid(row=1, column=1, padx=5, pady=5)

        self.dm_windows[target] = {"window": dm_window, "chat_box": chat_box}

    def start(self):
        """
        starts the server :/
        """
        if self.connect():
            self.setup_gui()
            self.start_receiving()
            self.root.mainloop()

if __name__ == "__main__":
    SERVER_IP = str(input("Enter server-ip: "))
    PORT = int(input("Enter server-port: "))
    client = ChatClient(server_ip=SERVER_IP, server_port=PORT)
    client.start()