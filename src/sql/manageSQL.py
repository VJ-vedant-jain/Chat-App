import mysql.connector

PASSWORD = input("Enter your SQL password - ")

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password=PASSWORD
)

mycursor = db.cursor()

mycursor.execute('CREATE DATABASE IF NOT EXISTS chatApp;')
db.close()

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password=PASSWORD,
    database='chatApp'
)
mycursor = db.cursor()

mycursor.execute(
    '''
        CREATE TABLE IF NOT EXISTS global_chat (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50),
            message VARCHAR(1000)
        );
    '''
)

def add_message(sent):
    if sent.startswith("[") and "]: " in sent:
        username_end = sent.find("]: ")
        username = sent[1:username_end]
        message = sent[username_end + 3:]
    else:
        parts = sent.strip().split(" ", 1)
        username = parts[0]
        message = parts[1] if len(parts) > 1 else ""
    
    sql = "INSERT INTO global_chat (username, message) VALUES (%s, %s)"
    values = (username, message)
    
    mycursor.execute(sql, values)
    db.commit()


def load_chat():
    mycursor.execute(
        '''
            SELECT username, message 
            FROM global_chat 
            ORDER BY id DESC 
            LIMIT 100
        '''
    )
    messages = mycursor.fetchall()
    messages.reverse()

    list_messages = []
    for username, message in messages:
        mes = f"[{username}]: {message}"
        list_messages.append(mes)

    return list_messages