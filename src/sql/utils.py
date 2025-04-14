import mysql.connector

def purge(password):
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password=password,
        database='chatApp'
    )
    mycursor = db.cursor()
    mycursor.execute("DELETE FROM global_chat")
    db.commit()
    db.close()
    print("All messages have been deleted.")

def prune(password):
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password=password,
        database='chatApp'
    )
    mycursor = db.cursor()

    mycursor.execute('''
        DELETE FROM global_chat
        WHERE id NOT IN (
            SELECT id FROM (
                SELECT id FROM global_chat
                ORDER BY id DESC
                LIMIT 100
            ) AS latest
        );
    ''')
    
    db.commit()
    db.close()
    print("Chat has been pruned to the newest 100 messages.")


PASSWORD = str(input("Enter mySQL password: "))

print("------------------------")
print("Enter 1 to purge the whole chat history")
print("Enter 2 to prune chat history to newest 100 messages")
while True:
    try:
        option = int(input("Enter option number: "))
    except:
        print("Enter valid input.")
    if option == 1:
        purge(PASSWORD)
        break
    if option ==2:
        prune(PASSWORD)
        break
    print("Enter either 1 or 2")
    