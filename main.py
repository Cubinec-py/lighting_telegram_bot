import ast
import os
import ipaddress
import asyncio

from aiogram.exceptions import TelegramNetworkError
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from time import time

from bot_db.mycloud_db import db_table_val, user_data, user_id, delete_user_ip
from dotenv.main import load_dotenv

load_dotenv()

token = os.environ.get('BOT_TOKEN')
dp = Dispatcher()
bot = Bot(token, parse_mode="HTML")


@dp.message(Command(commands=["start"]))
async def welcome(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Добавить адрес для отслеживания света"),
        types.KeyboardButton(text="Сделать разовую проверку наличия света")
    )
    builder.row(
        types.KeyboardButton(
            text="Cписок моих адресов",
            callback_data='ip_list'))
    await message.answer(
        "Привет, здесь ты можешь проверить наличие СветОчка у тебя дома.\n"
        "Выбери действие в меню",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@dp.message(Command(commands=["help"]))
async def help_text_command(message: types.Message):
    await message.answer(
        "Свой ip адрес можно узнать тут https://2ip.ua"
    )


@dp.message(lambda message: message.text ==
            "Добавить адрес для отслеживания света")
async def help_text_message(message: types.Message):
    await message.answer(
        "Для того что б добавить адрес для отслеживания света, введи /add и нужный адрес от 0.0.0.0 до 255.255.255.255 плюс название адреса\n"
        "Тыкни /help что б узнать свой ip адрес"
    )


@dp.message(lambda message: message.text ==
            "Сделать разовую проверку наличия света")
async def check_lighting(message: types.Message):
    await message.answer(
        "Для того что б проверить есть ли где угодно свет, просто введи /ip и нужный адрес от 0.0.0.0 до 255.255.255.255\n"
        "Тыкни /help что б узнать свой ip адрес"
    )


@dp.message(Command(commands=['ip_list']))
@dp.message(lambda message: message.text == "Cписок моих адресов")
async def list_of_user_ips(message: types.Message):
    user_ips = await user_data(message.chat.id)
    builder = InlineKeyboardBuilder()
    if len(user_ips) != 0:
        for ip in user_ips:
            builder.add(types.InlineKeyboardButton(
                text=f"{ip[1]} - {ip[2]}",
                callback_data=f"ip {ip[1]} {ip[0]}")
            )
            builder.add(types.InlineKeyboardButton(
                text="❌",
                callback_data="['del', '" + str(ip[0]) + "']")
            )
        builder.adjust(2)
        await message.answer(
            "Это список твоих адресов по которым постоянно отслеживаеться наличие света.\n"
            "Нажми на адрес для разовой проверки или нажми ❌ для удаления адреса.",
            reply_markup=builder.as_markup()
        )
    else:
        await message.answer(
            "У вас нет ни одного адреса для отслеживания света.\n"
            "Введи /add и нужный адрес от 0.0.0.0 до 255.255.255.255 плюс название адреса для его отслеживания"
        )


@dp.message(Command(commands=['add']))
async def add_ip_to_db(message: types.Message):
    try:
        if ipaddress.ip_address(
                message.text.split()[1]) and len(
                message.text.split()) >= 3:
            message_to_user = await message.answer('Немного времени и адрес будет добавлен')
            result = await icmp_ping(message.text.split()[1])
            now_time_sec = time()
            if 'Похоже' in result:
                await db_table_val(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    user_ip=''.join(message.text.split()[1]),
                    description_ip=' '.join(message.text.split()[2:]),
                    time_check=now_time_sec,
                    light_status=0
                )
                await message_to_user.edit_text(
                    "Адрес успешно добавлен для мониторинга света"
                )
            else:
                await db_table_val(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    user_ip=''.join(message.text.split()[1]),
                    description_ip=' '.join(message.text.split()[2:]),
                    time_check=now_time_sec,
                    light_status=1
                )
                await message_to_user.edit_text(
                    "Адрес успешно добавлен для мониторинга света"
                )
        else:
            await message.answer(
                "Неверный формат добавления адреса, введи /add и нужный адрес от 0.0.0.0 до 255.255.255.255 плюс название адреса"
            )
    except ValueError:
        await message.answer(
            "Неверный формат добавления адреса, введи /add и нужный адрес от 0.0.0.0 до 255.255.255.255 плюс название адреса"
        )


async def icmp_ping(ip):
    process = await asyncio.create_subprocess_shell(
        f"ping {ip} -c 4", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    print(stdout.decode())
    if process.returncode == 0:
        return 'Похоже свет есть, тебе повезло'
    elif 'Destination Host Unreachable' in stdout.decode():
        return 'Похоже свет есть, тебе повезло'

    return "Света нет, надо что-то думать"


async def icmp_check(message: types.Message):
    ip = message.split()[1]
    user = await user_id(message.split()[2])
    waiting_message = await bot.send_message(chat_id=user, text=f"Проверка света по адресу {ip} ...")
    try:
        result = await icmp_ping(ip)
        if result:
            await waiting_message.edit_text(f"Проверка света по адресу {ip}:\n{result}")
        else:
            await waiting_message.edit_text(f"Проверка света по адресу {ip}:\nНет результата")
    except Exception as e:
        await waiting_message.edit_text(f"Проверка света по адресу {ip}:\n{e}")


@dp.message(Command(commands=['ip']))
async def icmp_command_check(message: types.Message):
    try:
        if ipaddress.ip_address(message.text.split('/ip ')[1]):
            ip = message.text.split('/ip ')[1]
            message_answer = await message.answer(f"Проверка света по адресу {ip} ...")
            try:
                result = await icmp_ping(ip)
                if result:
                    await message_answer.edit_text(f"Проверка света по адресу {ip}:\n{result}")
                else:
                    await message_answer.edit_text(f"Проверка света по адресу {ip}:\nНет результата")
            except Exception as e:
                await message_answer.edit_text(f"Проверка света по адресу {ip}:\n{e}")

    except IndexError:
        await message.answer(
            "Неправильный формат, /ip затем полный диапазон IP-адресации – это адреса от 0.0.0.0 до 255.255.255.255"
        )
    except ValueError:
        await message.answer(
            "Неправильный формат, полный диапазон IP-адресации – это адреса от 0.0.0.0 до 255.255.255.255"
        )


@dp.callback_query(lambda call: True)
async def callback_inline(call):
    if call.data.startswith("['del'"):
        await delete_user_ip(ast.literal_eval(call.data)[1])
        await call.message.answer(
            "Адрес успешно удален"
        )
        await list_of_user_ips(call.message)
    if call.data.startswith("ip"):
        await icmp_check(call.data)


@dp.message()
async def unknown_message(message: types.Message):
    await message.answer(
        "Я подрос, но все равно ещё туповатый, я не понимаю команду '%s', прости🥺"
        % message.text
    )

if __name__ == '__main__':
    try:
        dp.run_polling(bot)
    except TelegramNetworkError:
        print('Нет интернет соединения, бот не включен!')
