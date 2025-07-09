import os
from dotenv import load_dotenv  # 🌍 Ielādē .env failu

load_dotenv()  # 🌍 Ielādē .env faila saturu vides mainīgajos

import logging
import threading
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)
from crypto import (
    get_analysis,
    get_profit,
    get_strategy,
    get_news,
    check_alerts,
)

# Получаем токен из переменных среды (например, Railway Variables)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# 📒 Logger konfigurācija
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "👋 Sveiki! Esmu kripto-kaķis🐾, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts BTC > BTC - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
        "📰 /news BTC - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
      )
    update.message.reply_text(text)

# ℹ️ Komanda: /help
def help_command(update: Update, context: CallbackContext):
    text = (
        "ℹ️ *Palīdzība:*\n\n"
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts BTC > 65000 - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
        "📰 /news BTC - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
    )
    update.message.reply_text(text, parse_mode=MARKDOWN)

def parse_coins(args):
    if not args:
        return []
    coins_str = ' '.join(args)
    coins = [c.strip().upper() for c in coins_str.split(",") if c.strip()]
    return coins

def analyze(update: Update, context: CallbackContext):
    coins = parse_coins(context.args)
    text = get_analysis(coins)
    update.message.reply_text(text, parse_mode=MARKDOWN)

def profit(update: Update, context: CallbackContext):
    coins = parse_coins(context.args)
    text = get_profit(coins)
    update.message.reply_text(text, parse_mode=MARKDOWN)

def strategy(update: Update, context: CallbackContext):
    coins = parse_coins(context.args)
    if not coins:
        update.message.reply_text("Lūdzu, norādi vismaz vienu monētu, piemēram: /strategy BTC,ETH")
        return
    text = get_strategy(coins)
    update.message.reply_text(text, parse_mode=MARKDOWN)

def news(update: Update, context: CallbackContext):
    coins = parse_coins(context.args)
    if not coins:
        update.message.reply_text("Lūdzu, norādi monētu, piemēram: /news BTC")
        return
    text = get_news(coins[0])
    update.message.reply_text(text, parse_mode=MARKDOWN)

def alert(update: Update, context: CallbackContext):
    args = context.args
    if len(args) != 2:
        update.message.reply_text("Lūdzu, lieto formātu: /alert MONĒTA CENA\nPiemēram: /alert BTC 20000")
        return
    coin = args[0].upper()
    try:
        price = float(args[1])
    except ValueError:
        update.message.reply_text("Cena jānorāda skaitliskā formātā, piem., 20000")
        return
    add_alert(update.effective_user.id, coin, price)
    update.message.reply_text(f"⚠️ Brīdinājums iestatīts: {coin} sasniegt {price} USD")

def alerts_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_alerts = alerts.get(user_id)
    if not user_alerts:
        update.message.reply_text("Tev nav iestatītu brīdinājumu.")
        return
    text = "📋 Tavi brīdinājumi:\n"
    for alert in user_alerts:
        text += f"• {alert['coin']} - {alert['price']} USD\n"
    update.message.reply_text(text)

def error(update: Update, context: CallbackContext):
    print(f'Update {update} izraisīja kļūdu: {context.error}')

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("analyze", analyze))
    dp.add_handler(CommandHandler("profit", profit))
    dp.add_handler(CommandHandler("strategy", strategy))
    dp.add_handler(CommandHandler("alert", alert))
    dp.add_handler(CommandHandler("alerts", alerts_command))
    dp.add_error_handler(error)

    # Start alerts checking thread
    from crypto import check_alerts
    thread = threading.Thread(target=check_alerts, args=(updater.bot,), daemon=True)
    thread.start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
