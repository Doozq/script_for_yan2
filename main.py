import threading
import time
import logging
import random
import json
import asyncio
from datetime import datetime, timedelta

import logger_setup

from work import work_profile
from templates import tournament_templates
# from telethon import TelegramClient, events
# from functools import partial


def load_profiles(file_path="profiles.json"):
    with open(file_path, "r") as f:
        data = json.load(f)
    # Преобразуем значения last_paint и last_claim в объекты datetime
    for profile_id in data:
        data[profile_id]["last_paint"] = datetime.fromisoformat(
            data[profile_id]["last_paint"]
        )
        data[profile_id]["last_claim"] = datetime.fromisoformat(
            data[profile_id]["last_claim"]
        )
        if "sleep_time" in data[profile_id]:
            data[profile_id]["sleep_time"] = datetime.fromisoformat(
                data[profile_id]["sleep_time"]
            )
    return data


# Сохранение обновленных данных об аккаунтах в JSON файл
def save_profiles(data, file_path="profiles.json"):
    # Преобразуем значения last_paint и last_claim обратно в строки
    for profile_id in data:
        data[profile_id]["last_paint"] = data[profile_id]["last_paint"].strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        data[profile_id]["last_claim"] = data[profile_id]["last_claim"].strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        if "sleep_time" in data[profile_id]:
            data[profile_id]["sleep_time"] = data[profile_id]["sleep_time"].strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def load_tanos():
    with open("tanos.json", "r") as f:
        data = json.load(f)
    data["time"] = datetime.fromisoformat(
        data["time"]
    )
    return data

def save_tanos(data):
    data["time"] = data["time"].strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    with open("tanos.json", "w") as f:
        json.dump(data, f, indent=4)

def calculate_day_profit():
    start_profiles = load_profiles("start_profiles.json")
    profiles = load_profiles("profiles.json")
    profit = {}
    for id in profiles:
        profit[id] = {}
        profit[id]["name"] = profiles[id]["name"]
        profit[id]["balance"] = f"{start_profiles[id]["balance"]} -> {profiles[id]["balance"]} (+{profiles[id]["balance"] - start_profiles[id]["balance"]})"
        if profiles[id]["is_max"] != start_profiles[id]["is_max"]:
            profit[id]["is_max"] = f"{start_profiles[id]["is_max"]} -> {profiles[id]["is_max"]}"
    
    with open("profit.json", "w") as f:
        json.dump(profit, f, indent=4)


# Функция для запуска задач в потоках с использованием семафора
def run_work_in_threads(works, profiles, tanos):
    threads = []
    for profile_id in works:
        thread = threading.Thread(target=work_profile, args=(profile_id, profiles, tanos,))
        threads.append(thread)
        thread.start()

    # Ждем завершения всех потоков
    for thread in threads:
        thread.join(timeout=600)
        print(thread.is_alive(), thread._name)


# Проверка и выполнение задач по расписанию
def check_and_run_work(profiles, tanos, start=False):
    work_to_run = []
    now = datetime.now()
    summ = 0
    for profile_id, data in profiles.items():
    #     profiles[profile_id].pop("start", None)
    #     for key in ["temp", "template_place", "my_place", "pixels_to_win", "skip", "start", "direction", "sleep_time"]:
    #         profiles[profile_id].pop(key, None)
    # return
        # if start:  # Случайный отбор для первого запуска за день
        #     if random.randint(0, 1):
        #         continue
        # if int(data["template_place"]) > 70 or (data["pixels_to_win"] != "In the zone" and int(data["pixels_to_win"]) > 50) or data["balance"] > 95000:
        #     continue
        # if int(data["name"]) not in [29]:
        #     continue
        # if not(random.randint(0, 49)) and ((now - data["last_claim"]) >= timedelta(hours=random.uniform(5, 8))):
        # #     work_to_run.append(profile_id)
        # if "sleep_time" not in data:
        #     profiles[profile_id]["sleep_time"] = now + timedelta(hours=random.randint(4, 9))
        # if now > data["sleep_time"] and now - data["sleep_time"] < timedelta(hours=6):
        #     continue
    #     if ("template_place" in data and int(data["template_place"]) > 11): #or ("pixels_to_win" in data and data["pixels_to_win"] != "In the zone" and int(data["pixels_to_win"]) > 35):
    #         continue
    # #     if data["balance"] > 200000:
    # #         print(data["balance"])
    # #         summ += data["balance"]
    # # print(summ)
        if now - data["last_paint"] >= timedelta(hours=random.uniform(1.5, 1.8)):
            work_to_run.append(profile_id)
    random.shuffle(work_to_run)
    run_work_in_threads(work_to_run, profiles, tanos)


# # Ваши данные для доступа к API Telegram
# api_id = '25358379'  # замените на ваш API ID
# api_hash = 'e0ad0b8803af099b2ee37f0099e3844d'  # замените на ваш API Hash
# phone_number = 'YOUR_PHONE_NUMBER'  # ваш номер телефона

# # Создание клиента
# client = TelegramClient('session_name', api_id, api_hash)

# # Функция для отслеживания сообщений в канале
# async def message_handler(event, tanos):
#     try:
#         message = event.message.text
#         if message == "NOT TANOS":
#             tanos["time"] = datetime.now()
#             logging.info("NEW MESSAGE ABOUT TANOS")
#             save_tanos(tanos)
#             tanos["time"] = datetime.fromisoformat(
#                 tanos["time"]
#             )
#     except Exception:
#         pass

# # Функция для запуска клиента Telegram в отдельном потоке
# def telegram_listener(tanos):
#     loop = asyncio.new_event_loop()  # Создание новой петли событий
#     asyncio.set_event_loop(loop)  # Устанавливаем эту петлю как активную в потоке

#     with client:
#         client.add_event_handler(partial(message_handler, tanos=tanos), events.NewMessage)
#         loop.run_until_complete(client.run_until_disconnected())  # Асинхронно запускаем клиента


def main():
    is_started = True
    logging.info("Script is started")
    while True:
        # current_hour = datetime.now().hour
        if False: # 10 <= current_hour <= 15:
            is_started = False
            # calculate_day_profit()
            logging.info("Night - Script is paused")
            time.sleep(random.randint(21600, 23000))

        else:
            profiles = load_profiles()
            tanos = load_tanos()
            # threading.Thread(target=telegram_listener, args=(tanos,), daemon=True).start()

            if not is_started:
                save_profiles(profiles, "start_profiles.json")
                profiles = load_profiles()
                logging.info("Morning - Script is unpaused")
                check_and_run_work(
                    profiles, start=True
                )  # Проверяем и запускаем задачи для аккаунтов, если время истекло
                save_profiles(profiles)
                is_started = True
                logging.info("Pause 17 minutes")
                time.sleep(1000)

            else:
                check_and_run_work(
                    profiles,
                    tanos
                )  # Проверяем и запускаем задачи для аккаунтов, если время истекло
                save_profiles(profiles)
                logging.info("Pause 4-6 minutes")
                time.sleep(random.randint(240, 360))


if __name__ == "__main__":
    main()
