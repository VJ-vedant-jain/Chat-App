import socket
import threading


ipAd = str(input("Enter IP address - "))
poAd = int(input("Enter Port number - "))

HEADER = 1024
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'

ADDR = (ipAd, poAd)

username = input("Enter Username - ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

if not username:
    exit()

def receive_messages():
    while True:
        try:
            message = client.recv(2048).decode('utf-8')
            if message:
                print(message)
        except:
            break

def send_message():
    print('                                     ')
    userInput = input("Enter your message - ")
    msg = f"[{username}] : {userInput}"
    if msg:
        message = msg.encode('utf-8')
        msg_length = len(message)
        send_length = str(msg_length).encode('utf-8')
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)
        if msg == DISCONNECT_MESSAGE:
            client.close()

threading.Thread(target=receive_messages, daemon=True).start()

while True:
    send_message()
