import aiohttp
import asyncio
import requests
import json
import time
import os
import re

from telegram.ext import Updater, CommandHandler
from telegram import ParseMode

def escape_markdown(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!\\'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

COINPAPRIKA_API = "https://api.coinpaprika.com/v1"
ALERTS_FILE = "alerts.json"

FMP_API_KEY = os.getenv("FMP_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

alerts = {}

def load_alerts():
    global alerts
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r") as f:
            alerts = json.load(f)
    else:
        alerts = {}

def save_alerts():
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f)

def add_alert(user_id, coin, price):
    user_id = str(user_id)
    coin = coin.lower()
    if user_id not in alerts:
        alerts[user_id] = []
    alerts[user_id].append({"coin": coin, "price": price})
    save_alerts()

def remove_alert(user_id, coin, price):
    user_id = str(user_id)
    coin = coin.lower()
    if user_id in alerts:
        alerts[user_id] = [a for a in alerts[user_id] if not (a["coin"] == coin and a["price"] == price)]
        if not alerts[user_id]:
            del alerts[user_id]
        save_alerts()

def check_alerts(bot):
    while True:
        for user_id, user_alerts in list(alerts.items()):
            for alert in user_alerts[:]:
                coin = alert['coin'].lower()
                target_price = alert['price']
                price = get_current_price(coin)
                if price is None:
                    continue
                if price >= target_price:
                    text = f"⚠️ Cena {coin.upper()} sasniedz {price:.4f} USD (mērķis {target_price} USD)!"
                    try:
                        bot.send_message(chat_id=int(user_id), text=text)
                    except Exception as e:
                        print(f"Error sending alert message: {e}")
                    user_alerts.remove(alert)
            if not user_alerts:
                del alerts[user_id]
        save_alerts()
        time.sleep(900)

def get_top_coins(limit=10):
    try:
        response = requests.get(f"{COINPAPRIKA_API}/coins")
        response.raise_for_status()
        all_coins = response.json()
        coins = [coin for coin in all_coins if coin.get("rank") and coin.get("type") == "coin"]
        sorted_coins = sorted(coins, key=lambda x: x["rank"])
        return [coin["symbol"].upper() for coin in sorted_coins[:limit]]
    except Exception as e:
        print(f"Error in get_top_coins: {e}")
        return []

def get_coin_id(symbol):
    try:
        response = requests.get(f"{COINPAPRIKA_API}/coins")
        response.raise_for_status()
        for coin in response.json():
            if coin["symbol"].upper() == symbol.upper() and coin["type"] == "coin":
                return coin["id"]
        return None
    except Exception as e:
        print(f"Error in get_coin_id: {e}")
        return None

def get_price_data(symbol):
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return None
    try:
        response = requests.get(f"{COINPAPRIKA_API}/tickers/{coin_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error in get_price_data for {symbol}: {e}")
        return None

def get_current_price(symbol):
    data = get_price_data(symbol)
    if not data:
        return None
    return data["quotes"]["USD"]["price"]

def news(symbol):
    url = "https://min-api.cryptocompare.com/data/v2/news/"
    params = {
        "categories": symbol.upper(),
        "lang": "EN"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        news_list = []
        for item in data.get("Data", [])[:5]:
            title = item.get("title", "Bez nosaukuma")
            link = item.get("url", "")
            title_escaped = escape_markdown(title)
            news_list.append(f"• [{title_escaped}]({link})")
        if not news_list:
            return f"Šobrīd nav jaunumu par {symbol}."
        return "\n".join(news_list)
    except Exception as e:
        return f"Kļūda iegūstot ziņas: {e}"

def get_analysis(coins=None):
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
        output += f"🔸 {symbol}: ${price:.4f} ({change_24h:+.2f}%)\n"
    return output

def calculate_profit(coins=None):
    if not coins:
        coins = get_top_coins(10)
    output = "💰 *Pozīciju ieteikumi:*\n\n"
    for symbol in coins:
        data = get_price_data(symbol)
        if not data:
            output += f"{symbol}: ❌ Neizdevās iegūt datus\n"
            continue
        change_24h = data["quotes"]["USD"].get("percent_change_24h", 0)
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
            f"💵 Cena: ${price:.4f}\n"
            f"🔄 24h: {change_24h:+.2f}% | 7d: {change_7d:+.2f}% | 30d: {change_30d:+.2f}%\n"
            f"📌 Stratēģija:\n"
            f"• Ieguldi pa daļām (Dollar-Cost Averaging — DCA), iegādājoties pakāpeniski neatkarīgi no cenas.\n"
            f"• Pārdod daļu, kad peļņa sasniedz +10% (take profit).\n"
            f"• Izmanto stop loss (trailing stop) — aizsardzības mehānisms, kas pārdod, ja cena sāk krist pēc kāpuma.\n\n"
        )
    return output

def news_command(update, context):
    chat_id = update.effective_chat.id
    try:
        symbol = context.args[0].upper() if context.args else "XRP"
        news_text = news_cryptocompare(symbol)
        context.bot.send_message(chat_id=chat_id, text=news_text, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        context.bot.send_message(chat_id=chat_id, text=f"Kļūda: {e}")

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN nav iestatīts!")

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Команда /news
    dp.add_handler(CommandHandler("news", news_command))

    print("🗞️🐈‍⬛ Kaķis lasa ziņas...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
