from flask import Flask, request, jsonify
import pandas as pd
import requests
import datetime
import os

app = Flask(__name__)

# Yetkilendirme işlemi için kullanıcı adı ve şifre
username = "365"
password = "1"

def get_access_token():
    try:
        url = "https://api.baubuddy.de/index.php/login"
        headers = {
            "Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
            "Content-Type": "application/json"
        }
        data = {
            "username": username,
            "password": password
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            # Başarılı bir yanıt alındı, JSON verisini alabilirsiniz
            return response.json()["oauth"]["access_token"]
        else:
            print("Yetkilendirme hatası:", response.status_code)
            return None
    except Exception as e:
        print("Yetkilendirme hatası:", str(e))
        return None

@app.route('/api/upload', methods=['POST'])
def upload_csv():
    try:
        # Yetkilendirme işlemini yap
        access_token = get_access_token()

        if access_token is not None:
            data = request.json  # Gelen veriyi JSON formatında al
            df = pd.DataFrame(data)  # JSON verisini bir veri çerçevesine dönüştür

            # Dış kaynaktan veri alma
            external_data_url = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"
            external_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            external_data = requests.get(external_data_url, headers=external_headers)
            external_data = external_data.json()

            
            # Veriyi işleme ve eksik sütunları eklemek
            today = datetime.date.today()
            for i, row in df.iterrows():
                if 'hu' in row and not pd.isnull(row['hu']):
                    hu_date = datetime.datetime.strptime(row['hu'], "%Y-%m-%d").date()
                    if (today - hu_date).days <= 90:
                        df.at[i, "color"] = "#007500"  # Yeşil
                    elif (today - hu_date).days <= 365:
                        df.at[i, "color"] = "#FFA500"  # Turuncu
                    else:
                        df.at[i, "color"] = "#b30000"  # Kırmızı

            # İşlenmiş veriyi JSON olarak dön
            records = df.to_dict(orient="records")
            return jsonify(records)
        else:
            return "Yetkilendirme hatası", 401
    except Exception as e:
        return "Sunucu ile iletişim hatası: " + str(e), 500

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
