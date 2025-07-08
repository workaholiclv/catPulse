import datetime
import requests

def get_trending_coins(limit=5):
    url = "https://api.coingecko.com/api/v3/search/trending"
    r = requests.get(url)
    r.raise_for_status()
    return [item["item"]["id"] for item in r.json()["coins"][:limit]]

def get_price_data(coins):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coins),
        "order": "market_cap_desc",
        "per_page": len(coins),
        "page": 1,
        "sparkline": False
    }
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def get_analysis(coins=None):
    if coins is None:
        coins = get_trending_coins()
    data = get_price_data(coins)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    text = f"📊 Анализ на {today}:

"
    for coin in data:
        sym = coin["symbol"].upper()
        price = coin["current_price"]
        ch = coin.get("price_change_percentage_24h")
        if ch is None:
            trend = "❓ Нет данных"
        elif ch > 2:
            trend = "📈 Рост"
        elif ch < -2:
            trend = "🔻 Падение"
        else:
            trend = "⚖️ Нейтрально"
        text += f"{sym}: ${price:.2f} ({ch:+.2f}%) — {trend}
"
    return text

def get_profit_suggestion(coins=None):
    if coins is None:
        coins = get_trending_coins()
    data = get_price_data(coins)
    text = "📈 Оценка потенциала:

"
    for c in data:
        sym = c["symbol"].upper()
        price = c["current_price"]
        ch = c.get("price_change_percentage_24h")
        if ch is None:
            signal = "❓ Недостаточно данных"
        elif ch > 3:
            signal = "🟢 LONG"
        elif ch < -3:
            signal = "🔴 SHORT"
        else:
            signal = "⚪ Нейтрально"
        text += f"{sym}: ${price:.2f} ({ch:+.2f}%) — {signal}
"
    return text
