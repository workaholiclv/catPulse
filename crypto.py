import requests

COINPAPRIKA_API = "https://api.coinpaprika.com/v1"

def get_top_coins(limit=10):
    try:
        response = requests.get(f"{COINPAPRIKA_API}/coins")
        response.raise_for_status()
        all_coins = response.json()
        coins = [coin for coin in all_coins if coin.get("rank") and coin.get("type") == "coin"]
        sorted_coins = sorted(coins, key=lambda x: x["rank"])
        return [coin["symbol"].upper() for coin in sorted_coins[:limit]]
    except Exception:
        return []

def get_coin_id(symbol):
    try:
        response = requests.get(f"{COINPAPRIKA_API}/coins")
        response.raise_for_status()
        for coin in response.json():
            if coin["symbol"].upper() == symbol.upper() and coin["type"] == "coin":
                return coin["id"]
        return None
    except Exception:
        return None

def get_price_data(symbol):
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return None
    try:
        response = requests.get(f"{COINPAPRIKA_API}/tickers/{coin_id}")
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def get_analysis(coins):
    if not coins:
        coins = get_top_coins(10)
    output = "📊 *Tirgus analīze:*\n\n"
    for symbol in coins:
        data = get_price_data(symbol)
        if not data:
            output += f"{symbol}: ❌ Neizdevās iegūt datus\n"
            continue
        price = data["quotes"]["USD"]["price"]
        change_24h = data["quotes"]["USD"]["percent_change_24h"]
        output += f"🔸 {symbol}: ${price:.2f} ({change_24h:+.2f}%)\n"
    return output

def get_profit(coins):
    if not coins:
        coins = get_top_coins(10)
    output = "💰 *Pozīciju ieteikumi:*\n\n"
    for symbol in coins:
        data = get_price_data(symbol)
        if not data:
            output += f"{symbol}: ❌ Neizdevās iegūt datus\n"
            continue
        change_24h = data["quotes"]["USD"]["percent_change_24h"]
        if change_24h > 3:
            pos = "📈 Ilgā pozīcija (pirkt un turēt)"
        elif change_24h < -3:
            pos = "📉 Īsā pozīcija (pārdot vai spekulēt uz kritumu)"
        else:
            pos = "⚖️ Neitrāli"
        output += f"{symbol}: {pos} ({change_24h:+.2f}%)\n"
    return output

def get_strategy(coins):
    output = "📈 *Stratēģija:*\n\n"
    for symbol in coins:
        data = get_price_data(symbol)
        if not data:
            output += f"{symbol}: ❌ Neizdevās iegūt datus\n"
            continue
        q = data["quotes"]["USD"]
        price = q["price"]
        change_24h = q.get("percent_change_24h", 0)
        change_7d = q.get("percent_change_7d", 0)
        change_30d = q.get("percent_change_30d", 0)

        output += (
            f"🔹 {symbol}\n"
            f"💵 Cena: ${price:.2f}\n"
            f"🔄 24h: {change_24h:+.2f}% | 7d: {change_7d:+.2f}% | 30d: {change_30d:+.2f}%\n"
            f"📌 Stratēģija:\n"
            f"• Ieguldi pakāpeniski — tā saucamā DCA metode (Dollar-Cost Averaging), iegādājoties aktīvu pa daļām neatkarīgi no cenas.\n"
            f"• Pārdod daļu, kad peļņa sasniedz +10% (take profit).\n"
            f"• Izmanto trailing stop — tas ir aizsardzības mehānisms, kas automātiski pārdod, ja cena sāk krist pēc kāpuma.\n\n"
        )
    return output
