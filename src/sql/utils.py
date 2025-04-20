import mysql.connector

def purge():
    password = input("Enter MySQL password to confirm.")
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

def prune(number):
    password = input("Enter MySQL password to confirm.")
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password=password,
        database='chatApp'
    )
    mycursor = db.cursor()

    mycursor.execute(f'''
        DELETE FROM global_chat
        WHERE id NOT IN (
            SELECT id FROM (
                SELECT id FROM global_chat
                ORDER BY id DESC
                LIMIT {number}
            ) AS latest
        );
    ''')
    
    db.commit()
    db.close()

if __name__ == "__main__" : 
    print("------------------------")
    print("Enter 1 to purge the whole chat history")
    print("Enter 2 to prune chat history to newest 100 messages")
    while True:
        try:
            option = int(input("Enter option number: "))
        except:
            print("Enter valid input.")
        if option == 1:
            purge()
            break
        if option ==2:
            prune()
            break
        print("Enter either 1 or 2")