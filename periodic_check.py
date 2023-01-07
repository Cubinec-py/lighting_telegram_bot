import asyncio
import os

from time import time
import datetime

from aiogram import Bot

from bot_db.mycloud_db import all_ips, update_status
from dotenv.main import load_dotenv

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

TOKEN = os.environ.get('TOKEN')
bot = Bot(TOKEN, parse_mode="HTML")


async def async_ping(ip):
    process = await asyncio.create_subprocess_shell(
        f"ping {ip} -c 4", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        return ip, 0
    elif 'Destination Host Unreachable' in stdout.decode():
        return ip, 0

    return ip, 1


async def periodic_ip_check_task():
    while True:
        values = await all_ips()
        if values:
            coroutines = [async_ping(ip[0]) for ip in values]
            ip_check_status = await asyncio.gather(*coroutines)
            lst = list(zip(values, ip_check_status))
            now_time = time()
            for a, b in lst:
                ip, status, id, user_id, time_sec, ip_descrip = a
                ip_checked, status_new = b
                time_difference = datetime.timedelta(seconds=int(now_time - time_sec))
                if status_new == 0 and status == 1:
                    time_period = time_difference
                    print(f'Status of {ip}: {status} old - Status of just checked ip {ip_checked}: {status_new}')
                    await update_status(0, now_time, id)
                    await bot.send_message(
                        chat_id=user_id,
                        text=f"Свет по адресу {ip_descrip} появился, его не было {time_period} 😱"
                    )
                elif status_new == 1 and status == 0:
                    time_period = time_difference
                    print(f'Status of {ip}: {status} old - Status of just checked ip {ip_checked}: {status_new}')
                    await update_status(1, now_time, id)
                    await bot.send_message(
                        chat_id=user_id,
                        text=f"Свет по адресу {ip_descrip} пропал, он был {time_period} 🥺"
                    )
                else:
                    pass

        await asyncio.sleep(20)


loop = asyncio.get_event_loop()
task = loop.create_task(asyncio.run(periodic_ip_check_task()))

try:
    loop.run_until_complete(task)
except asyncio.CancelledError:
    pass
