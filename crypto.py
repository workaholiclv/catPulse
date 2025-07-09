import requests
import time
import json
import os

COINPAPRIKA_API = "https://api.coinpaprika.com/v1"
ALERTS_FILE = "alerts.json"

alerts = {}

def load_alerts():
    global alerts
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r") as f:
            alerts = json.load(f)

def save_alerts():
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f)


def get_price(coin_id):
    try:
        url = f"{COINPAPRIKA_API}/tickers/{coin_id}"
        response = requests.get(url)
        data = response.json()
        return data["quotes"]["USD"]["price"]
    except Exception:
        return None


def get_news():
    return (
        "*📰 Jaunākās kripto ziņas:*\n"
        "- Bitcoin pārsniedz 70 000 USD\n"
        "- Ethereum ETF apstiprināts\n"
        "- Binance atver jaunu biržu Eiropā"
    )


def analyze_market():
    return (
        "*📊 Tirgus analīze:*\n"
        "BTC izskatās bullish virs 68k\n"
        "ETH turas virs 3.5k\n"
        "Dominance pieaug, bet altcoini stagnē"
    )


def check_alerts(bot=None, user_id=None, manual=False):
    global alerts
    if manual and user_id:
        user_alerts = alerts.get(str(user_id), [])
        if not user_alerts:
            return "🔕 Tev nav uzstādītu brīdinājumu."
        results = ["*🔔 Tavs cenu brīdinājumu status:*"]
        for alert in user_alerts:
            coin = alert["coin"]
            target_price = alert["price"]
            current = get_price(coin)
            if current:
                results.append(f"{coin.upper()}: {current:.2f} USD (mērķis: {target_price})")
        return "\n".join(results) if results else "🔕 Nav pieejamu datu."

    if not bot:
        return

    for uid, user_alerts in alerts.items():
        for alert in user_alerts:
            coin = alert["coin"]
            target_price = alert["price"]
            current = get_price(coin)
            if current and current >= target_price:
                try:
                    bot.send_message(
                        chat_id=int(uid),
                        text=f"🚨 {coin.upper()} sasniedza {current:.2f} USD (mērķis bija {target_price})"
                    )
                except Exception:
                    pass

    time.sleep(30)
    check_alerts(bot=bot)


def set_alert(user_id, coin, price):
    user_id = str(user_id)
    if user_id not in alerts:
        alerts[user_id] = []
    alerts[user_id].append({"coin": coin.lower(), "price": float(price)})
    save_alerts()
    return f"🔔 Alerte uzstādīta: {coin.upper()} ≥ {price} USD"


def remove_alert(user_id, coin):
    user_id = str(user_id)
    coin = coin.lower()
    if user_id in alerts:
        alerts[user_id] = [a for a in alerts[user_id] if a["coin"] != coin]
        if not alerts[user_id]:
            del alerts[user_id]
        save_alerts()
        return f"🗑️ Alerte noņemta: {coin.upper()}"
    return f"❗ Tev nav uzstādīts brīdinājums par {coin.upper()}"


def get_profit(update, context):
    try:
        args = context.args
        if len(args) != 3:
            return "❗ Lietošana: /profit <coin> <buy_price> <amount>"

        coin = args[0].lower()
        buy_price = float(args[1])
        amount = float(args[2])
        current_price = get_price(coin)

        if not current_price:
            return f"❌ Neizdevās iegūt {coin.upper()} cenu."

        profit = (current_price - buy_price) * amount
        return f"💸 Peļņa par {coin.upper()}: {profit:.2f} USD"
    except Exception:
        return "❗ Neizdevās aprēķināt. Pārbaudi ievades datus."


def get_strategy():
    return (
        "*📈 Stratēģijas idejas:*\n"
        "- DCA (Dollar Cost Averaging)\n"
        "- Swing trading ar RSI indikatoru\n"
        "- Long ETH + short altcoini\n"
        "- HODL top 3 coinus līdz 2026"
    )
