import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from crypto import get_analysis, get_profit, get_strategy
from dotenv import load_dotenv

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN nav iestatīts. Lūdzu, iestatiet to vides mainīgajā.")

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "👋 Sveiki! Esmu kripto-kaķis🐾, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
    )

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

def main():
    updater = Updater(TOKEN)
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
