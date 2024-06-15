from datetime import datetime, time

import requests
from dotenv import load_dotenv
import os

from telebot import TeleBot

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
PAYLOAD = {'from_date': 0}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

bot = TeleBot(TELEGRAM_TOKEN)


def check_tokens():
    environment_variable = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    missing_variables = []
    for variable in environment_variable:
        if variable not in os.environ:
            missing_variables.append(variable)
    if missing_variables:
        return  missing_variables


try:
    check_tokens()
except Exception as e:
    print(f'Missing environment variables', e)
else:
    print(f'Environment variables found')


def send_message(bot, message):
    message = 'Hi, I`m practicum!'
    bot.send_message(TELEGRAM_CHAT_ID, message)
send_message(bot, message='Hi, I`m practicum!')


print(datetime.now())

def get_api_answer(timestamp):
    response = requests.get(ENDPOINT, headers=HEADERS, params=PAYLOAD)
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
        return response_json
print(get_api_answer())


# def check_response(response):
#     ...
#
#
# def parse_status(homework):
#     ...
#
#     return f'Изменился статус проверки работы "{homework_name}". {verdict}'
#
#
# def main():
#     """Основная логика работы бота."""
#
#     ...
#
#     # Создаем объект класса бота
#     bot = TeleBot(token=telegram_token)
#     timestamp = int(time.time())
#
#     ...
#
#     while True:
#         try:
#
#             ...
#
#         except Exception as error:
#             message = f'Сбой в работе программы: {error}'
#             ...
#         ...
#
#
# if __name__ == '__main__':
#     main()
