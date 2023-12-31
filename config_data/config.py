import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv(find_dotenv())

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Список команд и их описание"),
    ("search_low_price", "Поиск дешёвые билеты "),
    ("search_month", "поиск билеты в течение месяца"),
    ("search_non_stop_tickets", "поиск самых дешевых билетов без пересадок"),
    ("cancel", "Отмена поиска"),
    ("history", "История поиска")
)
