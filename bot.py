from telegram.ext import Updater, CommandHandler
from crypto import get_analysis
from config import TELEGRAM_TOKEN

def start(update, context):
    update.message.reply_text("Привет! Отправь /analyze чтобы получить свежую аналитику по крипте.")

def analyze(update, context):
    result = get_analysis()
    update.message.reply_text(result)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("analyze", analyze))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()