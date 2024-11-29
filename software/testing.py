from security import encryption

def test_db():
    from database import Database
    
    with Database(db='bearhouse_capital', user='sonny', password=encryption.load_and_decrypt(), host='localhost', port='5432') as db:
        db.cursor.execute('SELECT * FROM SHAREHOLDERS')
        users = db.cursor.fetchall()
        print(users)
    
test_db()