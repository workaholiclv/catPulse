import datetime
import requests
import os

COIN_SYMBOLS_CACHE = {}

def get_trending_coins(limit=5):
    """Получает трендовые монеты с CoinGecko (поисковые тренды)."""
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()["coins"]
    trending = [coin["item"]["id"] for coin in data[:limit]]
    return trending

def get_price_data(coins):
    """Получает цены и изменение за 24ч для списка монет."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coins),
        "order": "market_cap_desc",
        "per_page": len(coins),
        "page": 1,
        "sparkline": False
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_analysis(coins=None):
    """Основная функция: получает анализ по трендовым или заданным монетам."""
    # Если монеты не переданы явно — берём из трендов
    if coins is None:
        coins = get_trending_coins()

    data = get_price_data(coins)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    text = f"📊 Анализ рынка на {today}:\n\n"

    for coin in data:
        coin_id = coin["id"]
        symbol = coin["symbol"].upper()
        COIN_SYMBOLS_CACHE[coin_id] = symbol

        price = coin["current_price"]
        change = coin["price_change_percentage_24h"]

        if change is None:
            trend = "❓ Нет данных"
        elif change > 2:
            trend = "📈 Явный рост"
        elif change < -2:
            trend = "🔻 Падение"
        else:
            trend = "⚖️ Нейтрально"

        text += f"{symbol}: ${price:.2f} ({change:+.2f}%) — {trend}\n"

    return text
