import os
import threading
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
from crypto import (
    get_news,
    analyze_market,
    calculate_profit,
    get_strategy,
    set_alert,
    remove_alert,
    get_user_alerts,
    check_alerts
)

# 🌍 Ielādē .env failu
load_dotenv()

# 📝 Žurnāls
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# 🗞️ /news komanda
def news(update: Update, context: CallbackContext) -> None:
    text = get_news()
    update.message.reply_text(text)

# 📈 /analyze komanda
def analyze(update: Update, context: CallbackContext) -> None:
    text = analyze_market()
    update.message.reply_text(text)

# 💰 /profit komanda
def profit(update: Update, context: CallbackContext) -> None:
    try:
        args = context.args
        if len(args) != 2:
            raise ValueError("Nepareizs parametru skaits.")
        buy = float(args[0])
        sell = float(args[1])
        result = calculate_profit(buy, sell)
        update.message.reply_text(f"💰 Peļņa: {result}%")
    except Exception:
        update.message.reply_text("❌ Lietošana: /profit <buy_price> <sell_price>")

# 🎯 /strategy komanda
def strategy(update: Update, context: CallbackContext) -> None:
    text = get_strategy()
    update.message.reply_text(f"🎯 Stratēģija:\n{text}")

# 🔔 /setalert komanda
def setalert(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.effective_user.id
        args = context.args
        if len(args) != 2:
            raise ValueError("Nepareizs parametru skaits.")
        coin = args[0].upper()
        price = float(args[1])
        msg = set_alert(user_id, coin, price)
        update.message.reply_text(f"🔔 {msg}")
    except Exception:
        update.message.reply_text("❌ Lietošana: /setalert <coin> <price>")

# ❌ /removealert komanda
def removealert(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.effective_user.id
        args = context.args
        if len(args) != 1:
            raise ValueError("Nepareizs parametru skaits.")
        coin = args[0].upper()
        msg = remove_alert(user_id, coin)
        update.message.reply_text(f"🗑️ {msg}")
    except Exception:
        update.message.reply_text("❌ Lietošana: /removealert <coin>")

# 🔔 /alerts komanda
def alerts(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    msg = get_user_alerts(user_id)
    update.message.reply_text(msg)

# ⚠️ Kļūdu apstrāde
def error(update: object, context: CallbackContext) -> None:
    logger.warning(f'Update {update} izraisīja kļūdu: {context.error}')

# 🚀 Startē botu
def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("news", news))
    dispatcher.add_handler(CommandHandler("analyze", analyze))
    dispatcher.add_handler(CommandHandler("profit", profit))
    dispatcher.add_handler(CommandHandler("strategy", strategy))
    dispatcher.add_handler(CommandHandler("alerts", alerts))
    dispatcher.add_handler(CommandHandler("setalert", setalert))
    dispatcher.add_handler(CommandHandler("removealert", removealert))
    dispatcher.add_error_handler(error)

    # 🔁 Startē pārbaudes thread
    thread = threading.Thread(target=check_alerts, args=(updater.bot,), daemon=True)
    thread.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


if __name__ == "__main__":
    main()
