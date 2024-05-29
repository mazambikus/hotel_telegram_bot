import requests

url = "https://hotels4.p.rapidapi.com/locations/v2/search"

querystring = {"query": "new york", "locale": "en_US", "currency": "USD"}

headers = {
    "X-RapidAPI-Key": "fd147e9d15mshf1ca6d56c13a788p155468jsn1193f4f67510",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

# Проверка статуса ответа и его текста
print("Status Code:", response.status_code)
print("Response Text:", response.text)

try:
    data = response.json()
    destination_id = data['suggestions'][0]['entities'][0]['destinationId']
    print(destination_id)
except requests.exceptions.JSONDecodeError as e:
    print("JSON Decode Error:", e)
except Exception as e:
    print("An error occurred:", e)

#print(response.json())

url1 = "https://hotels4.p.rapidapi.com/properties/list"

querystring = {"destinationId":destination_id,
               "pageNumber":"1","pageSize":"25",
               "checkIn":"2024.5.18","checkOut":"2024.5.31",
               "adults1":"1","sortOrder":"PRICE",
               "locale":"en_US","currency":"USD"}

headers = {
	"X-RapidAPI-Key": "fd147e9d15mshf1ca6d56c13a788p155468jsn1193f4f67510",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response1 = requests.get(url1, headers=headers, params=querystring)

print(response1.json())


{
    "currency": "USD",
    "eapid": 1,
    "locale": "en_US",
    "siteId": 300000001,
    "propertyId": "9209612",
    "checkInDate": {
        "day": 6,
        "month": 10,
        "year": 2022
    },
    "checkOutDate": {
        "day": 9,
        "month": 10,
        "year": 2022
    },
    "destination": {
        "coordinates": {
            "latitude": 12.24959,
            "longitude": 109.190704
        },
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