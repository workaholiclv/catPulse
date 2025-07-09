import requests
import time

COINPAPRIKA_API = "https://api.coinpaprika.com/v1"

# 🔔 Glabā lietotāju uzstādītos cenu brīdinājumus
alerts = {}  # Piemērs: {"user_id": [{"coin": "BTC", "price": 70000}]}


def get_top_trending_coins(limit=10):
    try:
        response = requests.get(f"{COINPAPRIKA_API}/coins")
        response.raise_for_status()
        coins = response.json()
        active = [coin['symbol'].lower() for coin in coins if coin['type'] == 'coin']
        return active[:limit]
    except Exception as e:
        print(f"Kļūda iegūstot top monētas: {e}")
        return []


def get_top_coins(limit=10):
    try:
        response = requests.get(f"{COINPAPRIKA_API}/coins")
        response.raise_for_status()
        coins = [coin for coin in response.json() if coin.get("rank") and coin["type"] == "coin"]
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


def get_current_price(symbol):
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return None
    try:
        r = requests.get(f"{COINPAPRIKA_API}/tickers/{coin_id}")
        data = r.json()
        return data["quotes"]["USD"]["price"]
    except Exception:
        return None


def check_alerts(bot):
    """Pārbauda lietotāju brīdinājumus un izsūta paziņojumus, ja cena ir sasniegta."""
    while True:
        for user_id, user_alerts in list(alerts.items()):
            for alert in user_alerts[:]:
                coin = alert['coin']
                target = alert['price']
                price = get_current_price(coin)
                if price is None:
                    continue
                if price >= target:
                    bot.send_message(chat_id=user_id,
                                     text=f"⚠️ {coin.upper()} cena sasniedza ${price:.2f} (mērķis: ${target:.2f})")
                    user_alerts.remove(alert)
            if not user_alerts:
                del alerts[user_id]
        time.sleep(900)  # 15 minūtes


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
        output += f"🔸 {symbol.upper()}: ${price:.2f} ({change_24h:+.2f}%)\n"
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
            f"• Izmanto trailing stop vai stop loss — mehānisms, kas automātiski pārdod, ja cena sāk krist.\n\n"
        )
    return output


def get_news(symbol):
    # Coinpaprika diemžēl nenodrošina ziņas — tāpēc fiksējam kļūdu
    return "❗️Šobrīd nav pieejamas ziņas no Coinpaprika API."
