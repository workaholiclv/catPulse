import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from crypto import get_analysis, get_profit_suggestion

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Убедись, что переменная окружения правильно задана

user_coins = {}  # user_id -> список символов монет

def start(update: Update, context: CallbackContext):
    welcome_text = (
        "Sveiki! Es esmu Tavs CryptoBot.\n\n"
        "Komandas:\n"
        "/setcoins SYMBOLS - iestata monētas (var vairākas caur komatu, piem. BTC,ETH,CRO)\n"
        "/analyze - rāda pašreizējo analīzi par iestatītajām monētām\n"
        "/profit - rāda ieteikumus par ilgo vai īso pozīciju\n"
        "/help - palīdzība\n"
    )
    update.message.reply_text(welcome_text)

def help_command(update: Update, context: CallbackContext):
    help_text = (
        "Lietošana:\n"
        "/setcoins SYMBOLS - iestata monētas tavu analīzei\n"
        "/analyze - saņem analīzi par šīm monētām\n"
        "/profit - saņem ieteikumus LONG/SHORT stratēģijām\n"
        "Piemērs:\n"
        "/setcoins BTC,ETH,CRO"
    )
    update.message.reply_text(help_text)

def setcoins(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not context.args:
        update.message.reply_text("Lūdzu, norādi vismaz vienu monētu simbolu, piemēram: /setcoins BTC,ETH")
        return
    # Парсим символы, удаляем пробелы, приводим к верхнему регистру
    text = " ".join(context.args)
    symbols = [s.strip().upper() for s in text.split(",") if s.strip()]
    user_coins[user_id] = symbols
    update.message.reply_text(f"Iestatītas monētas: {', '.join(symbols)}\nLai saņemtu analīzi, izmanto /analyze")

def analyze(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    symbols = user_coins.get(user_id)
    if not symbols:
        update.message.reply_text("Monētas nav iestatītas. Izmanto /setcoins komandu, piemēram: /setcoins BTC,ETH")
        return
    text = get_analysis(symbols)
    update.message.reply_text(text)

def profit(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    symbols = user_coins.get(user_id)
    if not symbols:
        update.message.reply_text("Monētas nav iestatītas. Izmanto /setcoins komandu, piemēram: /setcoins BTC,ETH")
        return
    text = get_profit_suggestion(symbols)
    update.message.reply_text(text)

def main():
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN nav iestatīts.")
        return
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("setcoins", setcoins))
    dp.add_handler(CommandHandler("analyze", analyze))
    dp.add_handler(CommandHandler("profit", profit))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
