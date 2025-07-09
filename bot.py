import os
import logging
import threading
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from crypto import (
    get_analysis,
    get_profit,
    get_strategy,
    alerts,
    check_alerts,
    get_news,
    get_top_trending_coins
)

# Получаем токен из переменных среды (например, Railway Variables)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "👋 Sveiki! Esmu kripto-kaķis🐾, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts SYMBOL CENA - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
        "📰 /news SYMBOL - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
      )
    update.message.reply_text(text)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "ℹ️ Pieejamās komandas:\n"
        "📊 /analyze - analīze par top 10 kripto\n"
        "💰 /profit - ieteikumi (ilgi/īsi)\n"
        "📈 /strategy SYMBOL[,SYMBOL2] - piemēram: /strategy BTC,ETH\n\n"
        "Nav jāiestata atsevišķi monētas — mēs automātiski izvēlamies populārākās!"
    )

def analyze(update: Update, context: CallbackContext) -> None:
    coins = [coin.upper() for coin in context.args] if context.args else []
    response = get_analysis(coins)
    update.message.reply_text(response)

def profit(update: Update, context: CallbackContext) -> None:
    coins = [coin.upper() for coin in context.args] if context.args else []
    response = get_profit(coins)
    update.message.reply_text(response)

def strategy(update: Update, context: CallbackContext) -> None:
    coins = [coin.upper() for coin in context.args]
    if not coins:
        update.message.reply_text("❗Lūdzu norādi vismaz vienu monētu. Piemēram: /strategy BTC,ETH")
        return
    response = get_strategy(coins)
    update.message.reply_text(response)

def alerts_command(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    args = context.args
    if len(args) != 2:
        update.message.reply_text(
            "ℹ️ Lūdzu, ievadi komandu šādi: /alerts SYMBOL CENA\nPiemērs: /alerts BTC 65000"
        )
        return
    coin = args[0].lower()
    try:
        price = float(args[1])
    except ValueError:
        update.message.reply_text("⚠️ Lūdzu, ievadi derīgu cenu (piem., 65000).")
        return

    if user_id not in alerts:
        alerts[user_id] = []
    alerts[user_id].append({"coin": coin, "price": price})
    update.message.reply_text(f"✅ Tavi alerts par {coin.upper()} pie {price} USD ir iestatīts!")

def news_command(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        update.message.reply_text("ℹ️ Lūdzu, norādi monētu simbolu. Piemērs: /news BTC")
        return
    coin = args[0].lower()
    text = get_news(coin)
    update.message.reply_text(text)

def main():
    if not TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN nav iestatīts.")
        return

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("analyze", analyze))
    dp.add_handler(CommandHandler("profit", profit))
    dp.add_handler(CommandHandler("strategy", strategy))
    dp.add_handler(CommandHandler("alerts", alerts_command))
    dp.add_handler(CommandHandler("news", news_command))

    # Sāk alerts pārbaudes fonā
    alert_thread = threading.Thread(target=check_alerts, args=(updater.bot,), daemon=True)
    alert_thread.start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
