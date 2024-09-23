import mysql.connector
from secrets import TOKEN, DB


def dbquery(query: str, params: list[str] = [], fetchOne: bool = False) -> None:
    db = mysql.connector.connect(
        host = DB["host"],
        user = DB["user"],
        password = DB["password"],
        database = DB["database"],
        port = DB["port"]
    )
    
    mycursor = db.cursor()
    mycursor.execute(query)

    try:
        if fetchOne:
            result = mycursor.fetchone()
        else:   
            result = mycursor.fetchall()
    except:
        result = None 
    
    return result
    