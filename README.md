## Телеграм бот для поиска отелей

Данный бот позволяет легко найти подходящий отель в любом городе мира!

**Технологии**

 - Python
 - PyTelegramBotApi
 - requests
 - sqlite3

**Описание функций**
 - /lowprice - вывод самых недорогих отелей в выбранном городе
 - /highprice - вывод самых дорогих отелей в выбранном городе
 - /bestdeal - выбор отелей по цене и дальности от центра
 - /history - вывод истории поиска
 - /help - поиск в работе
 - при выборе диапазона дат проживания перед и после тире ставится пробел

## Первый запуск

 1. Установите все необходимые библиотеки - `pip install -r requirements.txt`
 2. Установите токены в файл `config.py`
     1. `TELEGRAM_TOKEN` - TelegramBotApi Token
     2. `HOTELS_TOKEN` - HotelsApi Token
 3. Запустите бота - `python3 main.py`

**Количество запросов на сайте ограничено 500 шт.**

## Версия Python
Бот написан с использованием Python версии `3.11.1`

### Примеры использования API

#### Получение списка доступных отелей

```python
import requests

url = "https://hotels4.p.rapidapi.com/properties/v2/list"

payload = {
	"currency": "USD",
	"eapid": 1,
	"locale": "en_US",
	"siteId": 300000001,
	"destination": { "regionId": "6054439" },
	"checkInDate": {
		"day": 10,
		"month": 10,
		"year": 2022
	},
	"checkOutDate": {
		"day": 15,
		"month": 10,
		"year": 2022
	},
	"rooms": [
		{
			"adults": 2,
			"children": [{ "age": 5 }, { "age": 7 }]
		}
	],
	"resultsStartingIndex": 0,
	"resultsSize": 200,
	"sort": "PRICE_LOW_TO_HIGH",
	"filters": { "price": {
			"max": 150,
			"min": 100
		} }
}
headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "your_hotels_api_token",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
```

#### Поиск города

```python
import requests

url = "https://hotels4.p.rapidapi.com/locations/v3/search"

querystring = {"q":"new york","locale":"en_US","langid":"1033","siteid":"300000001"}

headers = {
	"X-RapidAPI-Key": "your_hotels_api_token",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())
```

#### Получение подробной информации об отеле

```python
import requests

# Установите ваш токен HotelsAPI
HOTELS_TOKEN = "your_hotels_api_token"

# URL для получения подробной информации об отеле
url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

# Идентификатор отеля
hotel_id = "9209612"

# Тело запроса
payload = {
    "currency": "USD",
    "locale": "en_US",
    "propertyId": hotel_id
}

# Заголовки запроса
headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": HOTELS_TOKEN,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

# Отправка запроса и получение ответа
response = requests.post(url, json=payload, headers=headers).json()

# Вывод ответа
print(response)
```

### Примечание

- Замените `"your_hotels_api_token"` на ваш собственный ключ API, полученный на сайте RapidAPI.
- `hotel_id` должен быть заменен на действительный идентификатор отеля, для которого вы хотите получить подробную информацию.

Этот запрос возвращает JSON-ответ с детальной информацией об отеле, включая описание, фотографии, удобства, цены и другие данные.