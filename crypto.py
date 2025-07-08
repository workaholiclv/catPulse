import requests
import pandas as pd
from ta.trend import SMAIndicator

def get_price_data(coin='bitcoin', days=7):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    r = requests.get(url, params=params).json()
    prices = r['prices']
    df = pd.DataFrame(prices, columns=["ts", "price"])
    df['price'] = df['price'].astype(float)
    return df

def get_analysis():
    coins = ['bitcoin', 'ethereum', 'solana']
    text = "📈 Анализ монет:
"
    for coin in coins:
        df = get_price_data(coin)
        sma = SMAIndicator(df['price'], window=3).sma_indicator().iloc[-1]
        current = df['price'].iloc[-1]
        signal = "✅ ЛОНГ" if current > sma else "⚠️ ШОРТ"
        text += f"\n{coin.upper()} — ${current:.2f} → {signal}"
    return text