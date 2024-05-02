import aiomysql

async def get_connection():
    connection = await aiomysql.connect(
        host="localhost",
        user="root",
        password="",
        db="farmerapp",
        cursorclass=aiomysql.DictCursor
    )
    return connection

async def close_connection(connection):
    if connection:
        connection.close()
