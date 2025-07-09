import os
import threading
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
)

from crypto import (
    get_top_coins,
    get_analysis,
    calculate_profit,
    get_strategy,
    get_news,
    add_alert,
    remove_alert,
    check_alerts,
    load_alerts,
    alerts, 
)

# 🌍 Ielādē .env failu
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Nav iestatīts TELEGRAM_BOT_TOKEN .env failā")

def check_alerts(bot):
    while True:
        alerts = bot.dispatcher.bot_data.get("alerts", {})
        for user_id, user_alerts in list(alerts.items()):
            for alert in user_alerts[:]:  # копия списка, чтобы безопасно удалять
                coin = alert['coin'].lower()
                target_price = alert['price']
                price = get_current_price(coin)
                if price is None:
                    continue
                if price >= target_price:
                    text = f"⚠️ Cena {coin.upper()} sasniedz {price:.2f} USD (mērķis {target_price} USD)!"
                    bot.send_message(chat_id=user_id, text=text)
                    user_alerts.remove(alert)
            if not user_alerts:
                del alerts[user_id]
        time.sleep(900)  # 15 минут

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "👋 Sveiki! Esmu kripto-kaķis🐾, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts BTC > BTC - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
        "🆕 /setalert BTC 70000 - Jauns brīdinājums\n"
        "❌ /removealert BTC - Dzēst brīdinājumu \n"
        "📰 /news BTC - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
      )
    update.message.reply_text(text)

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts BTC > BTC - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
        "🆕 /setalert BTC 70000 - Jauns brīdinājums\n"
        "❌ /removealert BTC - Dzēst brīdinājumu \n"
        "📰 /news BTC - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
    )

# Команда /analyze
def analyze(update: Update, context: CallbackContext):
    coins = context.args
    if not coins:
        coins = get_top_coins(10)
    text = get_analysis(coins)
    update.message.reply_text(text)

# Команда /profit
def profit(update: Update, context: CallbackContext):
    coins = context.args
    if not coins:
        coins = get_top_coins(10)
    text = get_profit(coins)
    update.message.reply_text(text)

# Команда /strategy
def strategy(update: Update, context: CallbackContext):
    coins = context.args
    if not coins:
        update.message.reply_text("Lūdzu, norādi vismaz vienu monētu pēc komandas, piem., /strategy BTC ETH")
        return
    text = get_strategy(coins)
    update.message.reply_text(text)

# Команда /news
def news(update: Update, context: CallbackContext):
    coins = context.args
    if not coins:
        update.message.reply_text("Lūdzu, norādi monētu pēc komandas, piem., /news BTC")
        return
    text = get_news(coins[0])
    update.message.reply_text(text)

# Команда /setalert COIN PRICE
def setalert_command(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Lūdzu, izmanto: /setalert COIN PRICE (piem., /setalert BTC 50000)")
        return
    coin = args[0].upper()
    try:
        price = float(args[1])
    except ValueError:
        update.message.reply_text("Lūdzu, ievadi derīgu cenu, piemēram, 50000")
        return

    alerts = context.bot_data.get("alerts", {})
    user_alerts = alerts.get(user_id, [])
    user_alerts.append({"coin": coin, "price": price})
    alerts[user_id] = user_alerts
    context.bot_data["alerts"] = alerts
    update.message.reply_text(f"✅ Brīdinājums iestatīts: {coin} pie {price} USD")

# Команда /removealert COIN PRICE
def removealert_command(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Lūdzu, izmanto: /removealert COIN PRICE")
        return
    coin = args[0].upper()
    try:
        price = float(args[1])
    except ValueError:
        update.message.reply_text("Lūdzu, ievadi derīgu cenu.")
        return

    alerts = context.bot_data.get("alerts", {})
    user_alerts = alerts.get(user_id, [])
    before_count = len(user_alerts)
    user_alerts = [a for a in user_alerts if not (a["coin"] == coin and a["price"] == price)]
    after_count = len(user_alerts)

    if before_count == after_count:
        update.message.reply_text("⚠️ Šāds brīdinājums netika atrasts.")
    else:
        alerts[user_id] = user_alerts
        context.bot_data["alerts"] = alerts
        update.message.reply_text(f"✅ Brīdinājums par {coin} pie {price} USD noņemts.")

def error(update: Update, context: CallbackContext):
    logger.warning(f"Atjauninājums {update} izraisīja kļūdu: {context.error}")

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Инициализация alerts в bot_data
    dispatcher.bot_data["alerts"] = {}

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("analyze", analyze))
    dispatcher.add_handler(CommandHandler("profit", profit))
    dispatcher.add_handler(CommandHandler("strategy", strategy))
    dispatcher.add_handler(CommandHandler("news", news))
    dispatcher.add_handler(CommandHandler("setalert", setalert_command))
    dispatcher.add_handler(CommandHandler("removealert", removealert_command))

    dispatcher.add_error_handler(error)

    # Запускаем проверку alert'ов в отдельном потоке
    thread = threading.Thread(target=check_alerts, args=(updater.bot,), daemon=True)
    thread.start()

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
