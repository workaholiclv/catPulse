import requests
import datetime

_symbol_to_id_cache = {}

def load_symbol_to_id_map():
    global _symbol_to_id_cache
    if _symbol_to_id_cache:
        return _symbol_to_id_cache
    url = "https://api.coingecko.com/api/v3/coins/list"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        _symbol_to_id_cache = {item['symbol'].lower(): item['id'] for item in data}
    return _symbol_to_id_cache

def symbols_to_ids(symbols):
    symbol_to_id = load_symbol_to_id_map()
    ids = []
    for sym in symbols:
        sym_lower = sym.lower()
        coin_id = symbol_to_id.get(sym_lower)
        if coin_id:
            ids.append(coin_id)
    return ids

def get_trending_coins():
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        coins = [item['item']['id'] for item in data.get('coins', [])]
        return coins
    return []

def get_price_data(coins):
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

def get_analysis(symbols=None):
    if not symbols:
        coins = get_trending_coins()
    else:
        coins = symbols_to_ids(symbols)
    if not coins:
        return "❌ Nav atrastas derīgas monētas pēc dotajiem simboliem."
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
    text += "\n".join(lines)
    return text

def get_profit_suggestion(symbols=None):
    if not symbols:
        coins = get_trending_coins()
    else:
        coins = symbols_to_ids(symbols)
    if not coins:
        return "❌ Nav atrastas derīgas monētas pēc dotajiem simboliem."
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
    text += "\n".join(lines)
    return text
