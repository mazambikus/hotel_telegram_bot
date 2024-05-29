import requests
import json
from config import HOTELS_TOKEN

url = "https://hotels4.p.rapidapi.com/properties/v2/get-offers"

headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "fd147e9d15mshf1ca6d56c13a788p155468jsn1193f4f67510",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


payload = {
    "currency": "USD",
    "eapid": 1,
    "locale": "en_US",
    "siteId": 300000001,
    "checkInDate": {
        "day": 6,
        "month": 6,
        "year": 2024
    },
    "checkOutDate": {
        "day": 9,
        "month": 6,
        "year": 2024
    },
    "destination": {
        "regionId": "6054439"
    },
    "rooms": [
        {
            "adults": 2,
            "children": [
                {
                    "age": 5
                },
                {
                    "age": 7
                }
            ]
        },
        {
            "adults": 2,
            "children": []
        }
    ]
}

response = requests.post(url, json=payload, headers=headers)


if response.status_code == 200:
    hotels = response.json()
    print(hotels)
else:
    print(f"Error: {response.status_code}, {response.text}")
