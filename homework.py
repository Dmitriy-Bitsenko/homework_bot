from http import HTTPStatus

import logging
import sys
import time

import requests
import telegram
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Функция проверки доступности переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot: TeleBot, message: str):
    """Функция отправляет сообщение в Telegram чат."""
    logging.debug(f"Отправка боту: {bot} сообщения: {message}")
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        logging.debug("Успешная отправка сообщения в Telegram")
    except telegram.error.TelegramError as error:
        logging.error(f"Ошибка при отправке сообщения: {error}")
        raise telegram.error.TelegramError


def get_api_answer(timestamp: int):
    """Функция делает запрос к единственному эндпоинту API-сервиса."""
    payload = {"from_date": timestamp}
    logging.debug(f"{ENDPOINT}, headers {HEADERS}, params{payload}, timeout=5")
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=payload, timeout=5
        )
    except requests.RequestException as error:
        raise ConnectionError(f"Ошибка при запросе к API: {error}") from error
    status_code = homework_statuses.status_code
    if status_code != HTTPStatus.OK:
        raise ConnectionError(f"Ответ сервера: {status_code}")

    return homework_statuses.json()


def check_response(response):
    """Функция проверяет ответ API на соответствие документации."""
    logging.debug(f"Начинается проверка ответа API: {response}")
    if not isinstance(response, dict):
        raise TypeError("Данные приходят не в виде словаря")
    if "homeworks" not in response:
        raise KeyError("Нет ключа 'homeworks'")
    if "current_date" not in response:
        raise KeyError("Нет ключа 'current_date'")
    if not isinstance(response["homeworks"], list):
        raise TypeError("Данные приходят не в виде списка")

    return response.get("homeworks")


def parse_status(homework):
    """Функция извлекает статус о конкретной домашней работе."""
    logging.debug("Начали парсинг статуса")
    homework_name = homework.get("homework_name")
    if not homework_name:
        raise KeyError("Нет ключа 'homework_name'")
    status = homework.get("status")
    if not status:
        raise KeyError("Нет ключа 'status'")
    verdict = HOMEWORK_VERDICTS.get(status)
    if not verdict:
        raise KeyError("API возвращает недокументированный статус")
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_message(bot, message, prev_message) -> str:
    """Функция отправляет сообщение боту, если оно изменилось.
    Функция возвращает сообщение, которые уже было отправлено.
    """
    if message != prev_message:
        send_message(bot, message)
    else:
        logging.debug("Повтор сообщения, не отправляется боту")
    return message


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical("Отсутствует токен")
        sys.exit()

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                for homework in homeworks:
                    send_message(bot, parse_status(homework))
            else:
                logger.debug('Программа сработала штатно.')
        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}')
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    main()
