import requests
import logging
from typing import Optional, List, Dict
from config import HOTELS_TOKEN, TELEGRAM_TOKEN
import buffers
import db
from telebot import TeleBot
from telebot.types import InputMediaPhoto

logging.basicConfig(filename='error.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

bot: TeleBot = TeleBot(TELEGRAM_TOKEN)


def get_region_id(city: str) -> Optional[str]:
    """
    Получает идентификатор региона по названию города.

    Args:
        city (str): Название города.

    Returns:
        Optional[str]: Идентификатор региона или None в случае ошибки.
    """
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": city.title()}
    headers = {"X-RapidAPI-Key": HOTELS_TOKEN,
               "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}

    logging.debug(f"Fetching region ID for city: {city}")

    try:
        response = requests.get(url, headers=headers, params=querystring).json()
        sr = response.get('sr', [])
        logging.debug(f"Response from location search for city {city}: {response}")

        if sr:
            region_id = sr[0].get('gaiaId')
            logging.debug(f"Region ID for {city}: {region_id}")
            return region_id
        else:
            logging.error(f"Empty search results for city: {city}")
            return None
    except requests.RequestException as e:
        logging.error(f"Error fetching region ID for city {city}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None


def get_hotels(id: int) -> List[Dict]:
    """
    Получает список отелей.

    Args:
        id (int): Идентификатор пользователя.

    Returns:
        List[Dict]: Список отелей или пустой список в случае ошибки.
    """
    logging.debug(f"Fetching hotels for user ID: {id}")
    data = buffers.buffer.get(id, {})
    logging.debug(f"User data for ID {id}: {data}")

    if not data:
        logging.error(f"No data found for user ID {id}")
        return []

    region_id = data.get('city', '')
    print(region_id, 'region_id in get_hotels')

    if not region_id:
        logging.error(f"Could not get region ID for city: {data.get('city')}")
        return []

    try:
        year_in, month_in, day_in = map(int, data['checkIn'].split('.'))
        year_out, month_out, day_out = map(int, data['checkOut'].split('.'))
        logging.debug(f"Check-in date: {day_in}-{month_in}-{year_in}, Check-out date: {day_out}-{month_out}-{year_out}")
    except ValueError as e:
        logging.error(f"Error parsing check-in/check-out dates: {e}")
        return []

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": region_id},
        "checkInDate": {"day": day_in, "month": month_in, "year": year_in},
        "checkOutDate": {"day": day_out, "month": month_out, "year": year_out},
        "rooms": [{"adults": 1}],
        "resultsStartingIndex": 0,
        "resultsSize": 200,
        "sort": data.get('sort', '')
    }

    if data['command'] == '/bestdeal':
        payload['sort'] = "DISTANCE"
        payload['filters'] = {
            "price": {"max": data.get('max_p', ''), "min": data.get('min_p', '')}
        }

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": HOTELS_TOKEN,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    logging.debug(f"Payload for hotel search: {payload}")

    try:
        response = requests.post(url, json=payload, headers=headers).json()
        logging.debug(f"Response from hotel search: {response}")
        properties = response.get(
            'data', {}).get('propertySearch', {}).get('properties', [])
        logging.debug(f"Properties found: {properties}")
        return properties if properties else []
    except requests.RequestException as e:
        logging.error(f"Error fetching hotels: {e}")
        return []


def get_detail(hotel_id: str) -> Dict:
    """
    Получает детали отеля.

    Args:
        hotel_id (str): Идентификатор отеля.

    Returns:
        Dict: Детали отеля или пустой словарь в случае ошибки.
    """
    logging.debug(f"Fetching details for hotel ID: {hotel_id}")
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    payload = {"currency": "USD", "locale": "en_US", "propertyId": hotel_id}
    headers = {"content-type": "application/json", "X-RapidAPI-Key": HOTELS_TOKEN,
               "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}

    try:
        response = requests.post(url, json=payload, headers=headers).json()
        logging.debug(f"Response from detail fetch: {response}")
        if response and 'data' in response and 'propertyInfo' in response['data']:
            return response['data']['propertyInfo']
        else:
            logging.error(f"Response does not contain expected data: {response}")
            return {}
    except requests.RequestException as e:
        logging.error(f"Error fetching hotel details: {e}")
        return {}


def send_hotels(id: int):
    """
    Отправляет список отелей пользователю.

    Args:
        id (int): Идентификатор пользователя.
    """
    logging.debug(f"Sending hotels to user ID: {id}")

    try:
        data = buffers.buffer.get(id, {})
        logging.debug(f"User data for sending hotels: {data}")

        if not data:
            bot.send_message(id, 'Не удалось найти подходящие отели \n\nВведите команду /start для запуска бота.')
            return

        hotels = get_hotels(id)

        if not hotels:
            bot.send_message(id, 'Не удалось найти подходящие отели \n\nВведите команду /start для запуска бота.')
            return

        hotels = list(filter(check, hotels))

        if data['command'] == '/highprice':
            hotels = hotels[-data['hotels_count']:]

        if not hotels:
            bot.send_message(id, 'Не удалось найти подходящие отели \n\nВведите команду /start для запуска бота.')
            return

        names_of_hotel = []
        count_of_result = 0

        for hotel in hotels:
            if count_of_result >= data['hotels_count']:
                break

            name = hotel.get('name')
            price_info = hotel.get('price', {}).get('lead', {})
            price = price_info.get('formatted')
            amount = price_info.get('amount')
            distance_info = hotel.get('destinationInfo', {}).get('distanceFromDestination', {})
            distance = float(distance_info.get('value', 0))
            total_price = int(amount) * data['delta'] if amount else 0

            if data['command'] == '/bestdeal':
                if (float(data['min_distance']) > distance or
                        float(data['max_distance']) < distance):
                    continue

            detail = get_detail(hotel['id'])

            if detail:
                address = detail.get(
                    'summary', {}).get('location', {}).get(
                    'address', {}).get('addressLine')
                url = f'https://www.hotels.com/h{hotel["id"]}.Hotel-Information'

                msg = (f'*{name}* \n\n'
                       f'Адрес: *{address}*\n'
                       f'Расстояние до центра *{str(distance)} км* \n\n'
                       f'Цена за ночь: *{price}* \n'
                       f'Сумма для указанных дат: *${total_price}* \n'
                       f'Ссылка на отель для более подробной информации: {url}')

                if buffers.buffer[id].get('load_photo'):
                    photo_urls = [image_box['image']['url'] for image_box
                                  in detail.get('propertyGallery',
                                                {}).get('images',
                                                        [])][:buffers.buffer[id].get('photo_count', 0)]
                    media = []

                    for count, url in enumerate(photo_urls):
                        if count == 0:
                            media.append(InputMediaPhoto(media=url, caption=msg, parse_mode='MARKDOWN'))
                        else:
                            media.append(InputMediaPhoto(media=url))

                    bot.send_media_group(id, media)
                else:
                    bot.send_message(id, msg, parse_mode='MARKDOWN')

                names_of_hotel.append(f'[{name}]({url})')
                count_of_result += 1

        if count_of_result > 0:
            note = f'{data["command"]} --- {data["time"]} --- {", ".join(names_of_hotel)}'
            past = db.get_data(id=id)[0][1].split(';')
            past.append(note)
            db.update_data(data={'history': ';'.join(past)}, id=id)

            if count_of_result < data['hotels_count']:
                bot.send_message(id, f'По вашему запросу было найдено {count_of_result}'
                                     f' подходящих отелей,'
                                     f' вместо указанных вами {data["hotels_count"]}')

            bot.send_message(id, 'Введите команду /start для запуска бота.')
        else:
            bot.send_message(id, 'Не удалось найти подходящие отели \n\nВведите команду /start для запуска бота.')

    except Exception as e:
        logging.error(f"Error in send_hotels function: {e}", exc_info=True)
        bot.send_message(id, 'Произошла непредвиденная ошибка. Попробуйте снова')
        bot.send_message(id, 'Введите команду /start для запуска бота.')


def check(hotel_data: Dict) -> bool:
    """
    Проверяет данные отеля на наличие ненулевой цены.

    Args:
        hotel_data (Dict): Данные отеля.

    Returns:
        bool: Результат проверки.
    """
    return hotel_data.get('price', {}).get('lead', {}).get('formatted') != '$0'
