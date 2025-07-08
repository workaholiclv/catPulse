import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from crypto import get_analysis, get_profit, get_strategy

# Glabājam lietotāja monētas
user_coins = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "👋 Sveiki! Esmu kripto-kaķis🐈‍⬛, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
        "📌 *Komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "📊 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "🧠 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
    )

def help_command(update: Update, context: CallbackContext) -> None:
    start(update, context)

def analyze(update: Update, context: CallbackContext) -> None:
    args = context.args
    if args:
        coins = [coin.strip().upper() for coin in ",".join(args).split(",")]
    else:
        coins = get_top_trending_coins(5)
    analysis = get_analysis(coins)
    update.message.reply_text(f"📈 Analīze:\n{analysis}")

def profit(update: Update, context: CallbackContext) -> None:
    args = context.args
    if args:
        coins = [coin.strip().upper() for coin in ",".join(args).split(",")]
    else:
        coins = get_top_trending_coins(5)
    profit_text = get_profit(coins)
    update.message.reply_text(f"📊 Profita iespējas:\n{profit_text}")

def strategy(update: Update, context: CallbackContext) -> None:
    args = context.args
    if not args:
        update.message.reply_text("⚠️ Lūdzu, norādi vismaz vienu monētu pēc komandas. Piemērs: /strategy BTC,ETH")
        return
    coins = [coin.strip().upper() for coin in ",".join(args).split(",")]
    strategies = get_strategy(coins)
    update.message.reply_text(f"🧠 Stratēģijas:\n{strategies}")

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("ERROR: TELEGRAM_BOT_TOKEN nav iestatīts.")

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("analyze", analyze))
    dispatcher.add_handler(CommandHandler("profit", profit))
    dispatcher.add_handler(CommandHandler("strategy", strategy))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
