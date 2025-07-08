import requests

_symbol_to_id_cache = {}

def load_symbol_to_id_map():
    global _symbol_to_id_cache
    url = "https://api.coingecko.com/api/v3/coins/list"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        _symbol_to_id_cache = {item['symbol'].upper(): item['id'] for item in data}
    except Exception as e:
        print(f"Error loading symbol to ID map: {e}")
        _symbol_to_id_cache = {}

def get_coin_id(symbol):
    if not _symbol_to_id_cache:
        load_symbol_to_id_map()
    return _symbol_to_id_cache.get(symbol.upper())

def get_price_data(coin_id, days=7):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch price data for {coin_id}: {e}")
        return None

def get_top_trending_coins(n=5):
    url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        coins = [item['item']['symbol'].upper() for item in data.get('coins', [])][:n]
        return coins
    except Exception as e:
        print(f"Failed to fetch trending coins: {e}")
        return []

def get_analysis(coins):
    texts = ["📈 Analīze monētām:"]
    for coin in coins:
        coin_id = get_coin_id(coin)
        if not coin_id:
            texts.append(f"⚠️ {coin}: Nav atrasts CoinGecko ID.")
            continue
        data = get_price_data(coin_id, days=1)
        if not data or 'prices' not in data or len(data['prices']) < 2:
            texts.append(f"⚠️ {coin}: Neizdevās iegūt cenu datus.")
            continue
        start_price = data['prices'][0][1]
        end_price = data['prices'][-1][1]
        change_pct = ((end_price - start_price) / start_price) * 100
        trend = "📈 Pieaug" if change_pct > 0 else "📉 Krīt"
        texts.append(f"• {coin}: Cena mainījusies par {change_pct:.2f}% - {trend}")
    return "\n".join(texts)

def get_profit(coins):
    results = []
    for coin in coins:
        coin_id = get_coin_id(coin)
        if not coin_id:
            results.append(f"⚠️ {coin}: Nav atrasts CoinGecko ID.")
            continue
        data = get_price_data(coin_id)
        if not data or 'prices' not in data or len(data['prices']) < 2:
            results.append(f"⚠️ {coin}: Neizdevās iegūt datus.")
            continue
        prices = [p[1] for p in data['prices']]
        start_price = prices[0]
        end_price = prices[-1]
        change_pct = ((end_price - start_price) / start_price) * 100
        if change_pct > 1:
            advice = "Ilgā pozīcija (LONG) ieteicama 🔥"
        elif change_pct < -1:
            advice = "Īsā pozīcija (SHORT) ieteicama ❄️"
        else:
            advice = "Nav skaidras tendences, uzmanies ⚠️"
        results.append(f"💡 {coin}: {advice} (cenas izmaiņas {change_pct:.2f}%)")
    return "\n".join(results)

def get_strategy(coins):
    texts = ["🧠 Stratēģijas ieteikumi:"]
    for coin in coins:
        coin_id = get_coin_id(coin)
        if not coin_id:
            texts.append(f"⚠️ {coin}: Nav atrasts CoinGecko ID.")
            continue
        data = get_price_data(coin_id, days=30)
        if not data or 'prices' not in data or len(data['prices']) < 2:
            texts.append(f"⚠️ {coin}: Neizdevās iegūt cenu datus.")
            continue
        prices = [p[1] for p in data['prices']]
        start_price = prices[0]
        end_price = prices[-1]
        change_pct = ((end_price - start_price) / start_price) * 100

        if change_pct > 5:
            strategy = ("Ieguldi pakāpeniski, pārdod daļu pie +10% peļņas un izmanto sekojošo stop-loss, lai aizsargātu nopelnīto, ja cena sāk krist."
                        "ar trailing stop, lai nodrošinātu peļņu.")
        elif change_pct < -5:
            strategy = ("Ieteicams apsvērt īso pozīciju (SHORT) vai piesardzīgu ieguldījumu, "
                        "jo cena kritusies vairāk nekā 5%.")
        else:
            strategy = ("Nav skaidras tendences, ieteicams sekot tirgum un izmantot piesardzības pasākumus.")
        texts.append(f"• {coin}: Mēneša cenu izmaiņas {change_pct:.2f}%\n  {strategy}")
    return "\n\n".join(texts)
