import os
from telegram.ext import Updater, CommandHandler
from crypto import get_analysis, get_profit_suggestion, get_trending_coins

user_coins = {}

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="🤖 Привет! Я крипто-кот. Команды:\n"
                                  "/analyze — анализ монет\n"
                                  "/profit — идеи для LONG/SHORT\n"
                                  "/setcoins BTC ETH — задать монеты")

def analyze(update, context):
    chat_id = update.effective_chat.id
    coins = user_coins.get(chat_id)
    text = get_analysis(coins)
    context.bot.send_message(chat_id=chat_id, text=text)

def profit(update, context):
    chat_id = update.effective_chat.id
    coins = user_coins.get(chat_id)
    text = get_profit_suggestion(coins)
    context.bot.send_message(chat_id=chat_id, text=text)

def set_user_coins(update, context):
    chat_id = update.effective_chat.id
    coins = context.args
    if coins:
        user_coins[chat_id] = coins
        context.bot.send_message(chat_id, f"✅ Монеты заданы: {' '.join(coins)}")
    else:
        context.bot.send_message(chat_id, "⚠️ Укажи монеты после команды, например:\n/setcoins BTC ETH")

def main():
    token = os.getenv("BOT_TOKEN")
    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("analyze", analyze))
    dp.add_handler(CommandHandler("profit", profit))
    dp.add_handler(CommandHandler("setcoins", set_user_coins))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
