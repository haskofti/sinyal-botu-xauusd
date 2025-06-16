import pandas as pd
import requests
import smtplib from email.message import EmailMessage
from datetime import datetime

INTERVALS = ["15min", "30min", "1h", "4h", "1day"]
API_KEY = "023335a787744744b184cc9ecc6805d2"  # Kendi API anahtarınızla değiştirin
SYMBOL = "XAU/USD"

EMAIL_GONDER = True
EMAIL_ADRESI = "hafi26@gmail.com"  # BURAYI KENDİ ADRESİNLE DEĞİŞTİR

def get_data(interval):
    url = f"https://api.twelvedata.com/time_series?symbol={SYMBOL}&interval={interval}&outputsize=100&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        print(f"[{interval}] API hatası veya veri yok:", data)
        return None

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.set_index("datetime", inplace=True)
    df = df.astype(float)
    return df

def calculate_indicators(df):
    df["ma20"] = df["close"].rolling(window=20).mean()
    df["ma50"] = df["close"].rolling(window=50).mean()
    df["ma100"] = df["close"].rolling(window=100).mean()
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema100"] = df["close"].ewm(span=100).mean()
    df["rsi14"] = 100 - (100 / (1 + df["close"].pct_change().rolling(window=14).mean()))
    df["momentum"] = df["close"] - df["close"].shift(10)
    df["macd"] = df["close"].ewm(span=12).mean() - df["close"].ewm(span=26).mean()
    df["signal"] = df["macd"].ewm(span=9).mean()
    df["bollinger_mid"] = df["close"].rolling(20).mean()
    df["bollinger_std"] = df["close"].rolling(20).std()
    df["upper_band"] = df["bollinger_mid"] + 2 * df["bollinger_std"]
    df["lower_band"] = df["bollinger_mid"] - 2 * df["bollinger_std"]
    df["adx"] = abs(df["close"].diff()).rolling(14).mean()
    df["roc"] = df["close"].pct_change(periods=10)
    df["willr"] = (df["close"] - df["low"].rolling(14).min()) / (df["high"].rolling(14).max() - df["low"].rolling(14).min())
    return df

def generate_signal(df, interval):
    latest = df.iloc[-1]
    sinyal_sayisi = 0

    if latest["ma20"] > latest["ma50"]: sinyal_sayisi += 1
    if latest["ema20"] > latest["ema50"]: sinyal_sayisi += 1
    if latest["ma50"] > latest["ma100"]: sinyal_sayisi += 1
    if latest["ema50"] > latest["ema100"]: sinyal_sayisi += 1
    if latest["rsi14"] < 30: sinyal_sayisi += 1
    if latest["momentum"] > 0: sinyal_sayisi += 1
    if latest["macd"] > latest["signal"]: sinyal_sayisi += 1
    if latest["close"] > latest["upper_band"]: sinyal_sayisi += 1
    if latest["adx"] > 20: sinyal_sayisi += 1
    if latest["roc"] > 0: sinyal_sayisi += 1
    if latest["willr"] > -0.8: sinyal_sayisi += 1

    if sinyal_sayisi >= 6:
        entry = latest["close"]
        tp = entry + (entry * 0.01)
        sl = entry - ((tp - entry) / 4)
        return f"[{interval}] AL\nGiriş: {entry:.2f}\nTP: {tp:.2f}\nSL: {sl:.2f}"
    return f"[{interval}] Sinyal Yok"

def send_email(content):
    if not EMAIL_GONDER:
        return
    sender = "hafi26@gmail.com"
    password = "jxdb eksm rumw huqb"  # Gmail uygulama şifresi girilmeli
    receiver = "hafi26@gmail.com"

    try:
        msg = EmailMessage()
        msg.set_content(content)
        msg["Subject"] = "XAUUSD Çoklu Zaman Sinyal"
        msg["From"] = sender
        msg["To"] = receiver
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("Mail başarıyla gönderildi.")
    except Exception as e:
        print("Mail gönderilemedi:", e)

if __name__ == "__main__":
    rapor = f"Sinyal Raporu ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n"
    for interval in INTERVALS:
        df = get_data(interval)
        if df is not None:
            df = calculate_indicators(df)
            rapor += generate_signal(df, interval) + "\n"
    print(rapor)
    send_email(rapor)
    "mail sorunu düzeltmesi yapıldı"
