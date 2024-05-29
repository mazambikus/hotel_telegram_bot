TELEGRAM_TOKEN = '7086867151:AAGy3fnFx0Y5TB9xHXlgtxYHe35Hc3JZNVk'  # Токен, полученный от BotFather
HOTELS_TOKEN = 'fd147e9d15mshf1ca6d56c13a788p155468jsn1193f4f67510'  # Токен для Hotels API с сайта rapidapi

MAX_HOTELS_COUNT = 10
MAX_PHOTOS_COUNT = 9

import chardet

with open('database/no_city.txt', 'rb') as f:
    result = chardet.detect(f.read())


with open('database/no_city.txt', encoding=result['encoding']) as file:
    no_cities = list(map(lambda x: x.lower(), file.read().split()))
