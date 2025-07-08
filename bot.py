import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from crypto import get_analysis, get_profit, get_strategy, get_top_trending_coins

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

def help_command(update: Update, context: CallbackContext):
    start(update, context)

def analyze(update: Update, context: CallbackContext):
    coins = []
    if context.args:
        coins = [coin.strip().upper() for coin in " ".join(context.args).split(",")]
    else:
        coins = get_top_trending_coins(5)
    text = get_analysis(coins)
    update.message.reply_text(text)

def profit(update: Update, context: CallbackContext):
    coins = []
    if context.args:
        coins = [coin.strip().upper() for coin in " ".join(context.args).split(",")]
    else:
        coins = get_top_trending_coins(5)
    text = get_profit(coins)
    update.message.reply_text(text)

def strategy(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Lūdzu, norādi vismaz vienu monētu, piem., /strategy BTC,ETH")
        return
    coins = [coin.strip().upper() for coin in " ".join(context.args).split(",")]
    text = get_strategy(coins)
    update.message.reply_text(text)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("analyze", analyze))
    dp.add_handler(CommandHandler("profit", profit))
    dp.add_handler(CommandHandler("strategy", strategy))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
