import asyncio
import aiomysql
import os
import ssl

from dotenv.main import load_dotenv

load_dotenv()

loop = asyncio.new_event_loop()
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.load_verify_locations(cafile='/etc/ssl/cert.pem')


async def connect_db():
    try:
        connection = await aiomysql.connect(
            host=os.environ.get('HOST'),
            port=3306,
            user=os.environ.get('USERNAME'),
            password=os.environ.get('PASSWORD'),
            db=os.environ.get('BOT_DB'),
            loop=loop,
            ssl=ctx
        )
        cursor = await connection.cursor()
        return cursor
    except aiomysql.Error as error:
        raise error


async def all_ips():
    try:
        cursor = await connect_db()
        await cursor.execute('SELECT user_ip, light_status, id, user_id, time_check, description_ip FROM bot_db')
        result = await cursor.fetchall()
        await cursor.close()
        return result
    except aiomysql.Error as error:
        raise error


async def db_table_val(user_id: int, username: str, user_ip: str, description_ip: str, time_check, light_status):
    try:
        cursor = await connect_db()
        await cursor.execute(
            f'INSERT INTO bot_db (user_id, username, user_ip, description_ip, time_check, light_status) '
            f'VALUES ({user_id}, "{username}", "{user_ip}", "{description_ip}", {time_check}, {light_status})'
        )
        await cursor.commit()
        await cursor.close()
        return print(f'Добавлен пользователь {username} с адресом {user_ip} для отслеживания')
    except aiomysql.Error as error:
        raise error


async def user_data(user_id: int):
    try:
        cursor = await connect_db()
        await cursor.execute(f'SELECT id, user_ip, description_ip FROM bot_db WHERE user_id={user_id}')
        result = await cursor.fetchall()
        await cursor.close()
        return result
    except aiomysql.Error as error:
        raise error


async def user_id(id: int):
    try:
        cursor = await connect_db()
        await cursor.execute(f'SELECT user_id FROM bot_db WHERE id={id}')
        result = await cursor.fetchone()
        await cursor.close()
        return int(*result)
    except aiomysql.Error as error:
        raise error


async def delete_user_ip(id: int):
    try:
        cursor = await connect_db()
        await cursor.execute(f'DELETE FROM bot_db WHERE id={id}')
        await cursor.commit()
        await cursor.close()
    except aiomysql.Error as error:
        raise error


async def update_status(status, now_time_sec, id):
    try:
        cursor = await connect_db()
        await cursor.execute(f'UPDATE bot_db SET light_status = {status}, time_check = {now_time_sec} WHERE id = {id}')
        await cursor.commit()
        await cursor.close()
    except aiomysql.Error as error:
        raise error
