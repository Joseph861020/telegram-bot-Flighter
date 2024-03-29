from datetime import datetime
import requests
from telebot import custom_filters, types
import config_data.config
from database.history_db import db_create
from loader import bot
from states.get_states import MyStates
from database.city_finder import find_country_code

API_URL = 'https://api.travelpayouts.com/v1/prices/cheap'


@bot.message_handler(commands=['search_low_price'])
def start_search_low_price(message):
    bot.set_state(message.from_user.id, MyStates.origin, message.chat.id)
    bot.send_message(message.chat.id, "*Введите город вылета:*", parse_mode="Markdown")


@bot.message_handler(state=MyStates.origin)
def get_destination(message):
    bot.send_message(message.chat.id, "*Введите город прилета:*", parse_mode="Markdown")
    bot.set_state(message.from_user.id, MyStates.destination, message.chat.id)


@bot.message_handler(state=MyStates.destination)
def get_depart_date(message):
    bot.send_message(message.chat.id, "*Введите дата вылета:*", parse_mode="Markdown")
    bot.set_state(message.from_user.id, MyStates.departure_at, message.chat.id)


@bot.message_handler(state=MyStates.departure_at)
def ready_to_answer(message):
    try:
        """Функция для сбора и обработка воды пользователя и подготовка get request и отправка результат пользователю"""
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['departure_at'] = message.text
            db_create(message.chat.id, message.text)
            currency = 'rub'
            limit = 30
            token = config_data.config.API_KEY
            sorting = 'price'
            origin = data['origin']
            destination = data['destination']
            departure_at = data['departure_at']

            params = {
                'origin': origin,
                'destination': destination,
                'departure_at': departure_at,
                'currency': currency,
                'limit': limit,
                'token': token,
                'sorting': sorting,

            }

            response = requests.get('https://api.travelpayouts.com/v1/prices/cheap?', params=params)

            if 200 <= response.status_code <= 399:
                result = response.json()
                with open('received_data.json', 'w+') as file:
                    file.write(str(result))
                    if file.__sizeof__() > 0:
                        trips = next(iter([result['data']]))
                        for flights in trips.values():
                            for flight in flights.values():
                                departure = ''.join(filter(str.isalnum, departure_at))
                                keyboard = types.InlineKeyboardMarkup()
                                url_btn = types.InlineKeyboardButton(text="Ссылка на билет",
                                                                     url=f'https://www.aviasales.ru/search/{origin}{departure}{destination}1\n\n')
                                keyboard.add(url_btn)
                                bot.send_message(message.chat.id, f"Цена: {flight['price']} рублей\n"
                                                                  f"Авиакомпания: {flight['airline']}\n"
                                                                  f"Туда: {origin} --> {destination} ({datetime.strptime(flight['departure_at'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y %H:%M')})\n"
                                                                  f"Обратно: {destination} --> {origin} ({datetime.strptime(flight['return_at'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y %H:%M')})\n",
                                                 reply_markup=keyboard)

                    else:
                        bot.send_message(message.chat.id, "*Нет доступных билетов на выбранные даты.*",
                                         parse_mode="MarkDown")
            else:
                print(response)
                bot.send_message(message.chat.id, "*Ошибка при запросе к API. Попробуйте позже.*",
                                 parse_mode="MarkDown")
        bot.delete_state(message.from_user.id, message.chat.id)

    except Exception as e:
        # Log the exception
        print(f"Error: {e}")
        bot.send_message(message.chat.id, "*Произошла ошибка при обработке запроса. Попробуйте позже.*", parse_mode="Markdown")

    finally:
        bot.delete_state(message.from_user.id, message.chat.id)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())


