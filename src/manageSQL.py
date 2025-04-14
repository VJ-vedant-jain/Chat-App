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
    parts = sent.strip().split()

    if parts[0].startswith("!"):
        return  

    username = parts[0]
    message = ' '.join(parts[1:])

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
            LIMIT 64
        '''
    )
    messages = mycursor.fetchall()
    print("Loaded messages from DB:", messages)
    messages.reverse()

    list_messages = []
    for username, message in messages:
        mes = f"[{username}]: {message}"
        list_messages.append(mes)

    return list_messages