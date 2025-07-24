import mysql.connector

PASSWORD = input("Enter your SQL password - ")

# Step 1: First, connect to MySQL without specifying a database.
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password=PASSWORD
)

mycursor = db.cursor()

# Step 2: Create the database if it doesn't exist
mycursor.execute('CREATE DATABASE IF NOT EXISTS chatApp;')

# Step 3: Close the connection to reconnect to the newly created database
db.close()

# Step 4: Now, reconnect, but this time specifying the 'chatApp' database
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password=PASSWORD,
    database='chatApp'
)

mycursor = db.cursor()

# Step 5: Create the table if it doesn't exist
mycursor.execute(
    '''
        CREATE TABLE IF NOT EXISTS global_chat (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50),
            message VARCHAR(1000)
        );
    '''
)

# Function to add a message to the database
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

# Function to load the last 24 messages from the database
def load_chat():
    mycursor.execute(
        '''
            SELECT username, message 
            FROM global_chat 
            ORDER BY id DESC 
            LIMIT 24
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
