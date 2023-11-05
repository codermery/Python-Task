import requests
import pandas as pd
import datetime

# Yetkilendirme bilgileri
username = "365"
password = "1"
auth_headers = {
    "Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
    "Content-Type": "application/json"
}

# Yetkilendirme isteğini yap
auth_url = "https://api.baubuddy.de/index.php/login"
auth_payload = {
    "username": username,
    "password": password
}
auth_response = requests.post(auth_url, json=auth_payload, headers=auth_headers)

if auth_response.status_code == 200:
    # Yetkilendirme başarılı, erişim belirtecini al
    access_token = auth_response.json()["oauth"]["access_token"]

    # CSV dosyasını yükleyip JSON formatına çevirme
    input_csv = pd.read_csv("vehicles.csv", delimiter=';', skipinitialspace=True, na_values=[''])
    input_json = input_csv.to_json(orient="records")

    # Sunucuya JSON veriyi gönderme
    url = 'http://127.0.0.1:5000/api/upload'  # Sunucunun çalıştığı URL'yi buraya girin
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post(url, data=input_json, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Sunucudan gelen JSON veriyi işleme
        df = pd.DataFrame(data)

        # Veriyi CSV olarak dönüştürme
        df.to_excel("processed_data.xlsx")
    else:
        print("Sunucu ile iletişim hatası:", response.status_code)
else:
    print("Yetkilendirme hatası:", auth_response.status_code)
