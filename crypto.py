import requests
import datetime

def get_trending_coins():
    """Iegūst populārākās monētas no CoinGecko (ID formātā)"""
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        coins = [item['item']['id'] for item in data.get('coins', [])]
        return coins
    return []

def get_price_data(coins):
    """
    Iegūst cenu un izmaiņu datus 24h periodā par dotajām monētām
    coins — saraksts ar monētu ID (piemēram, ['bitcoin', 'ethereum'])
    """
    if not coins:
        return []

    ids = ",".join(coins)
    url = (
        f"https://api.coingecko.com/api/v3/coins/markets"
        f"?vs_currency=usd&ids={ids}&order=market_cap_desc&per_page=250&page=1&sparkline=false"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def get_analysis(coins=None):
    if not coins:
        coins = get_trending_coins()
    data = get_price_data(coins)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    text = f"📊 Analīze uz {today}:\n"
    lines = []
    for coin in data:
        sym = coin.get("symbol", "???").upper()
        price = coin.get("current_price", 0)
        ch = coin.get("price_change_percentage_24h")
        if ch is None:
            trend = "❓ Nav datu"
        elif ch > 2:
            trend = "📈 Aug"
        elif ch < -2:
            trend = "🔻 Krīt"
        else:
            trend = "⚖️ Stabils"
        lines.append(f"{sym}: ${price:.2f} ({ch:+.2f}%) — {trend}")
    text += "; ".join(lines)
    return text

def get_profit_suggestion(coins=None):
    if not coins:
        coins = get_trending_coins()
    data = get_price_data(coins)
    text = "📈 Potenciāls:\n"
    lines = []
    for coin in data:
        sym = coin.get("symbol", "???").upper()
        price = coin.get("current_price", 0)
        ch = coin.get("price_change_percentage_24h")
        if ch is None:
            signal = "❓ Nav pietiekami datu"
        elif ch > 3:
            signal = "🟢 Ilgā pozīcija (Pērk)"
        elif ch < -3:
            signal = "🔴 Īsā pozīcija (Pārdod)"
        else:
            signal = "⚪ Neitrāls"
        lines.append(f"{sym}: ${price:.2f} ({ch:+.2f}%) — {signal}")
    text += "; ".join(lines)
    return text
