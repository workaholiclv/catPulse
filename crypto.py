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
        print(f"load_symbol_to_id_map: Error fetching coins list: {response.status_code}")
        _symbol_to_id_cache = {}
    return _symbol_to_id_cache

def get_coin_id(symbol):
    symbol = symbol.upper()
    symbol_map = load_symbol_to_id_map()
    coin_id = symbol_map.get(symbol)
    if coin_id is None:
        print(f"get_coin_id: No CoinGecko id found for symbol '{symbol}'")
    return coin_id

def get_price_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': '30',  # взять больше данных для стратегии
        'interval': 'daily'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"get_price_data: Failed to fetch data for {coin_id}, status {response.status_code}")
    return None

def get_top_trending_coins(limit=5):
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        coins = data.get('coins', [])
        symbols = [coin['item']['symbol'].upper() for coin in coins[:limit]]
        return symbols
    else:
        print(f"get_top_trending_coins: Failed to fetch trending coins, status {response.status_code}")
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
        results.append(f"📊 {coin}: Cena pēdējās 30 dienās ir {trend} par {change_pct:.2f}%.")
    return "\n".join(results)

def get_profit(coins):
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
        results.append(f"💡 {coin}: {advice} ({change_pct:.2f}% pārmaiņas pēdējās 30 dienās)")
    return "\n".join(results)

def get_strategy(coins):
    results = []
    for coin in coins:
        coin_id = get_coin_id(coin)
        if not coin_id:
            results.append(f"⚠️ {coin}: Nav atrasts CoinGecko ID.")
            continue
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false"
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            results.append(f"⚠️ {coin}: Neizdevās iegūt datus.")
            continue
        data = response.json()
        market_data = data.get("market_data", {})
        pct_24h = market_data.get("price_change_percentage_24h", 0)
        pct_7d = market_data.get("price_change_percentage_7d", 0)
        pct_30d = market_data.get("price_change_percentage_30d", 0)

        text = (f"📈 {coin}: Stratēģija — ieguldi pa daļām, pārdod daļu pie +10% peļņas un izmanto trailing stop, lai aizsargātu nopelnīto, ja cena sāk krist.\n"
                f"Cenas izmaiņas: pēdējās 24h {pct_24h:.2f}%, nedēļā {pct_7d:.2f}%, mēnesī {pct_30d:.2f}%.")
        results.append(text)
    return "\n\n".join(results)
