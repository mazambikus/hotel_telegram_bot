import sqlite3


def register(message):
    '''
    Регистрирует пользователя в базе данных.

    Args:
        message: Объект сообщения от Telegram, содержащий информацию о пользователе.
    '''
    insert_data = [(message.from_user.id, '')]

    with sqlite3.connect('database/database.db') as db:
        cursor = db.cursor()

        query = '''INSERT INTO users(id, history) VALUES(?, ?) '''

        cursor.executemany(query, insert_data)
        db.commit()


def update_data(data: dict(), id=None, table='users'):
    '''
    Обновляет данные в базе данных.

    Args:
        data (dict): Словарь в формате {колонна: значение}.
        id (int): ID пользователя, данные которого нужно обновить. Если None, обновляются данные для всех пользователей.
        table (str): Название таблицы, в которой производится обновление данных.
    '''

    with sqlite3.connect('database/database.db') as db:
        cursor = db.cursor()

        if id is not None:
            for key in data:
                update_data = (data[key], id)

                query = f'UPDATE {table} SET {key} = ? where id = ?'
                cursor.execute(query, update_data)

        else:
            for key in data:
                update_data = (data[key],)

                query = f'UPDATE {table} SET {key} = ?'
                cursor.execute(query, update_data)

        db.commit()


def get_data(id=None, table='users'):
    '''
    Получает данные из базы данных.

    Args:
        id (int): ID пользователя, данные которого нужно получить. Если None, возвращаются данные всех пользователей.
        table (str): Название таблицы, из которой нужно получить данные.

    Returns:
        list: Список кортежей с данными из базы данных.
    '''

    with sqlite3.connect('database/database.db') as db:
        cursor = db.cursor()

        if id is not None:
            select_query = f'SELECT * from {table} where id = ?'
            cursor.execute(select_query, (id,))

        if id is None:
            select_query = f'SELECT * from {table}'
            cursor.execute(select_query)

        data = cursor.fetchall()

        return data
