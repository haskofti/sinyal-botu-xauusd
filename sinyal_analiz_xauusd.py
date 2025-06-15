import pandas as pd
import requests
from datetime import datetime

def get_data():
    url = "https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=1h&outputsize=100&apikey=023335a787744744b184cc9ecc6805d2"
    response = requests.get(url)
    data = response.json()
   
    if "values" not in data:
        print("API Hatası veya sınır aşıldı:", data)
        exit()

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.set_index("datetime", inplace=True)
    df = df.astype(float)
    return df

def generate_signal(df):
    df["ma20"] = df["close"].rolling(window=20).mean()
    df["ma50"] = df["close"].rolling(window=50).mean()

    if df["ma20"].iloc[-1] > df["ma50"].iloc[-1]:
        entry = df["close"].iloc[-1]
        tp = entry + (entry * 0.01)
        sl = entry - ((tp - entry) / 4)
        return f"AL\nGiriş: {entry:.2f}\nTake Profit: {tp:.2f}\nStop Loss: {sl:.2f}"
    else:
        return "Sinyal Yok"

if __name__ == "__main__":
    df = get_data()
    sinyal = generate_signal(df)
    print(f"{datetime.now()}:\n{sinyal}")