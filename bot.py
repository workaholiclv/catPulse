import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from crypto import get_analysis, get_profit_suggestion

CUSTOM_COINS = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Привет! Я крипто‑бот.

"
        "Команды:
"
        "/analysis — анализ рынка
"
        "/profit — оценки прибыли и сигналы
"
        "/setcoins BTC ETH — задать свои монеты
"
    )
    await update.message.reply_text(text)

async def analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = CUSTOM_COINS if CUSTOM_COINS else None
    text = get_analysis(coins)
    await update.message.reply_text(text)

async def profit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = CUSTOM_COINS if CUSTOM_COINS else None
    text = get_profit_suggestion(coins)
    await update.message.reply_text(text)

async def setcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CUSTOM_COINS
    coins = [c.lower() for c in context.args]
    if coins:
        CUSTOM_COINS = coins
        await update.message.reply_text(f"✅ Монеты установлены: {', '.join(CUSTOM_COINS).upper()}")
    else:
        await update.message.reply_text("⚠️ Укажи монеты: /setcoins BTC ETH")

def main():
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analysis", analysis))
    app.add_handler(CommandHandler("profit", profit))
    app.add_handler(CommandHandler("setcoins", setcoins))
    app.run_polling()

if __name__ == "__main__":
    main()
