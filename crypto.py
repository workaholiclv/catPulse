import requests
import time

COINPAPRIKA_API = "https://api.coinpaprika.com/v1"

# 🔔 Glabā lietotāju uzstādītos cenu brīdinājumus
alerts = {}  # Piemērs: {"user_id": [{"coin": "BTC", "price": 70000}]}

def add_alert(user_id, coin, price):
    """Pievieno jaunu cenu brīdinājumu konkrētam lietotājam."""
    user_alerts = alerts.get(user_id, [])
    user_alerts.append({"coin": coin.upper(), "price": price})
    alerts[user_id] = user_alerts

def remove_alert(user_id, coin, price):
    """Noņem cenu brīdinājumu."""
    if user_id in alerts:
        alerts[user_id] = [
            alert for alert in alerts[user_id]
            if not (alert["coin"] == coin.upper() and alert["price"] == price)
        ]
        if not alerts[user_id]:
            del alerts[user_id]

def get_top_coins(limit=10):
    """Iegūst top monētas pēc CoinPaprika ranga."""
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
    """Atrod monētas ID pēc tās simbolu."""
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
    """Iegūst cenu un izmaiņu datus par monētu pēc tās simbolu."""
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
    """Ērta funkcija aktuālās cenas iegūšanai."""
    data = get_price_data(symbol)
    if not data:
        return None
    return data["quotes"]["USD"]["price"]

def get_analysis(coins):
    """Sniedz tirgus analīzi izvēlētajām monētām."""
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
    """Sniedz ieteikumus par ilgām vai īsām pozīcijām."""
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
    """Sniedz investīciju stratēģiju ar papildu analīzi."""
    output = "📈 *Stratēģija:*\n\n"
    for symbol in coins:
        data = get_price_data(symbol)
        if not data:
            output += f"{symbol}: ❌ Neizdevās iegūt datus\n\n"
            continue
        q = data["quotes"]["USD"]
        price = q["price"]
        change_24h = q.get("percent_change_24h", 0)
        change_7d = q.get("percent_change_7d", 0)
        change_30d = q.get("percent_change_30d", 0)

        output += (
            f"🔹 {symbol}\n"
            f"💵 Cena: ${price:.2f}\n"
            f"🔄 Izmaiņas: 24h: {change_24h:+.2f}%, 7d: {change_7d:+.2f}%, 30d: {change_30d:+.2f}%\n"
            f"📌 Stratēģija:\n"
            f"• Ieguldi pakāpeniski — tā saucamā DCA metode (Dollar-Cost Averaging), iegādājoties aktīvu pa daļām neatkarīgi no cenas.\n"
            f"• Pārdod daļu, kad peļņa sasniedz +10% (take profit).\n"
            f"• Izmanto stop loss — tas ir aizsardzības mehānisms, kas automātiski pārdod, ja cena sāk krist pēc kāpuma.\n\n"
        )
    return output

def get_news(symbol):
    """Iegūst jaunākās ziņas par monētu."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return f"Nevar atrast ziņas priekš {symbol.upper()}."
    try:
        response = requests.get(f"{COINPAPRIKA_API}/coins/{coin_id}/events")
        response.raise_for_status()
        events = response.json().get("events", [])
        if not events:
            return f"📰 Nav jaunāko ziņu vai notikumu par {symbol.upper()}."
        news_text = f"📰 *Jaunākās ziņas un notikumi par {symbol.upper()}:*\n\n"
        for event in events[:5]:
            title = event.get("title", "Bez virsraksta")
            date = event.get("date_event", "Nav datuma")
            url = event.get("source_url", "")
            news_text += f"• {title} ({date})\n{url}\n\n"
        return news_text
    except Exception:
        return "Neizdevās ielādēt jaunākās ziņas."

def get_current_price(symbol):
    """Vienkārša cenas iegūšana."""
    data = get_price_data(symbol)
    if not data:
        return None
    return data["quotes"]["USD"]["price"]

def check_alerts(bot):
    """Pārbauda alertus un sūta paziņojumus."""
    while True:
        for user_id, user_alerts in list(alerts.items()):
            for alert in user_alerts[:]:
                coin = alert['coin'].lower()
                target_price = alert['price']
                price = get_current_price(coin)
                if price is None:
                    continue
                if price >= target_price:
                    text = f"⚠️ Cena {coin.upper()} sasniedz {price} USD (mērķis {target_price} USD)!"
                    bot.send_message(chat_id=user_id, text=text)
                    user_alerts.remove(alert)  # Noņem alertu pēc paziņojuma
            if not user_alerts:
                del alerts[user_id]
        time.sleep(900)  # 15 minūtes
