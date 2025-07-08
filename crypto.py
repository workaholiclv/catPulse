import requests

_symbol_to_id_cache = {}

def load_symbol_to_id_map():
    global _symbol_to_id_cache
    if _symbol_to_id_cache:
        return _symbol_to_id_cache
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        _symbol_to_id_cache = {item['symbol'].upper(): item['id'] for item in data}
    else:
        _symbol_to_id_cache = {}
    return _symbol_to_id_cache

def get_coin_id(symbol):
    symbol = symbol.upper()
    symbol_map = load_symbol_to_id_map()
    return symbol_map.get(symbol)

def get_price_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': '1',
        'interval': 'hourly'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_top_trending_coins(limit=5):
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        coins = data.get('coins', [])
        symbols = [coin['item']['symbol'].upper() for coin in coins[:limit]]
        return symbols
    return []

def get_analysis(coins):
    results = []
    for coin in coins:
        coin_id = get_coin_id(coin)
        if not coin_id:
            results.append(f"⚠️ {coin}: Nav atrasts CoinGecko ID.")
            continue
        data = get_price_data(coin_id)
        if not data:
            results.append(f"⚠️ {coin}: Neizdevās iegūt datus.")
            continue
        prices = [p[1] for p in data.get('prices', [])]
        if len(prices) < 2:
            results.append(f"⚠️ {coin}: Nepietiekami dati analīzei.")
            continue
        start_price = prices[0]
        end_price = prices[-1]
        change_pct = ((end_price - start_price) / start_price) * 100
        trend = "augšupejoša 📈" if change_pct > 0 else "lejupslīdoša 📉"
        results.append(f"📊 {coin}: Cena pēdējās 24h {trend} par {change_pct:.2f}%.")
    return "\n".join(results)

def get_profit(coins):
    results = []
    for coin in coins:
        coin_id = get_coin_id(coin)
        if not coin_id:
            results.append(f"⚠️ {coin}: Nav atrasts CoinGecko ID.")
            continue
        # Простая логика для примера, можно расширить
        data = get_price_data(coin_id)
        if not data:
            results.append(f"⚠️ {coin}: Neizdevās iegūt datus.")
            continue
        prices = [p[1] for p in data.get('prices', [])]
        if len(prices) < 2:
            results.append(f"⚠️ {coin}: Nepietiekami dati profita aprēķinam.")
            continue
        start_price = prices[0]
        end_price = prices[-1]
        change_pct = ((end_price - start_price) / start_price) * 100

        if change_pct > 1:
            advice = "ilga pozīcija (LONG) ieteicama 🔥"
        elif change_pct < -1:
            advice = "īsa pozīcija (SHORT) ieteicama ❄️"
        else:
            advice = "nav skaidras tendences, uzmanies ⚠️"

        results.append(f"💡 {coin}: {advice} ({change_pct:.2f}% pārmaiņas pēdējās 24h)")
    return "\n".join(results)

def get_strategy(coins):
    results = []
    for coin in coins:
        results.append(
            f"📈 {coin}: Stratēģija — ieguldīt pakāpeniski (DCA), izmantot take profit pie +10% un trailing stop."
        )
    return "\n".join(results)
