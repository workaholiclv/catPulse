import os
import threading
import time
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)
from crypto import (
    get_top_coins,
    get_analysis,
    calculate_profit,
    get_strategy,
    news,
    add_alert,
    remove_alert,
    check_alerts,
    load_alerts,
    save_alerts,
    get_current_price,
)

# Загрузка .env
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Nav iestatīts TELEGRAM_BOT_TOKEN .env failā")

# --- Команды ---

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "👋 Sveiki! Esmu kripto-kaķis🐾, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts BTC > BTC - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
        "🆕 /setalert BTC 70000 - Jauns brīdinājums\n"
        "❌ /removealert BTC 70000 - Dzēst brīdinājumu \n"
        "📰 /news BTC - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
    )

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts BTC > BTC - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
        "🆕 /setalert BTC 70000 - Jauns brīdinājums\n"
        "❌ /removealert BTC 70000 - Dzēst brīdinājumu \n"
        "📰 /news BTC - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
    )

def analyze(update: Update, context: CallbackContext) -> None:
    coins = context.args
    if not coins:
        coins = get_top_coins(10)
    text = get_analysis(coins)
    update.message.reply_text(text)

def profit(update: Update, context: CallbackContext) -> None:
    coins = context.args
    if not coins:
        coins = get_top_coins(10)
    text = calculate_profit(coins)
    update.message.reply_text(text)

def strategy(update: Update, context: CallbackContext) -> None:
    coins = context.args
    if not coins:
        update.message.reply_text("Lūdzu, norādi vismaz vienu monētu pēc komandas, piem., /strategy BTC ETH")
        return
    text = get_strategy(coins)
    update.message.reply_text(text)

def news_command(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text("Lūdzu norādi monētu, piem., /news BTC")
        return
    symbol = context.args[0]
    # news в твоём crypto.py должен быть синхронным или если асинхронным - надо адаптировать
    text = news(symbol)  
    update.message.reply_text(text)

def setalert_command(update: Update, context: CallbackContext) -> None:
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
    add_alert(user_id, coin, price)
    update.message.reply_text(f"✅ Brīdinājums iestatīts: {coin} pie {price} USD")

def removealert_command(update: Update, context: CallbackContext) -> None:
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
    count_before = len(alerts.get(str(user_id), []))

    remove_alert(user_id, coin, price)

    count_after = len(alerts.get(str(user_id), []))
    if count_before == count_after:
        update.message.reply_text("⚠️ Šāds brīdinājums netika atrasts.")
    else:
        update.message.reply_text(f"✅ Brīdinājums par {coin} pie {price} USD noņemts.")

def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error: {context.error}")

def alert_checker_thread(bot):
    while True:
        try:
            check_alerts(bot)
        except Exception as e:
            logger.error(f"Kļūda alertu pārbaudē: {e}")
        time.sleep(60)

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    alerts = load_alerts()
    if alerts is None:
        alerts = {}
    dispatcher.bot_data["alerts"] = alerts

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("analyze", analyze))
    dispatcher.add_handler(CommandHandler("profit", profit))
    dispatcher.add_handler(CommandHandler("strategy", strategy))
    dispatcher.add_handler(CommandHandler("news", news_command))
    dispatcher.add_handler(CommandHandler("setalert", setalert_command))
    dispatcher.add_handler(CommandHandler("removealert", removealert_command))

    dispatcher.add_error_handler(error)

    thread = threading.Thread(target=alert_checker_thread, args=(updater.bot,), daemon=True)
    thread.start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
