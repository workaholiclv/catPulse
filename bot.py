import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from crypto import (
    get_top_coins,
    get_analysis,
    calculate_profit,
    get_strategy,
    news,
    add_alert,
    remove_alert,
    check_alerts,
    load_alerts,
    save_alerts,
    get_current_price,
)

# 🌍 Ielādē .env failu
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Nav iestatīts TELEGRAM_BOT_TOKEN .env failā")

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Čau! Esmu kripto-kaķis🐾, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts BTC > BTC - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
        "🆕 /setalert BTC 70000 - Jauns brīdinājums\n"
        "❌ /removealert BTC 70000 - Dzēst brīdinājumu \n"
        "📰 /news BTC - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts BTC > BTC - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
        "🆕 /setalert BTC 70000 - Jauns brīdinājums\n"
        "❌ /removealert BTC 70000 - Dzēst brīdinājumu \n"
        "📰 /news BTC - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    coins = context.args or get_top_coins(10)
    text = get_analysis(coins)
    await update.message.reply_text(text)

async def profit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    coins = context.args or get_top_coins(10)
    text = calculate_profit(coins)
    await update.message.reply_text(text)

async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    coins = context.args
    if not coins:
        await update.message.reply_text("Lūdzu, norādi vismaz vienu monētu pēc komandas, piem., /strategy BTC ETH")
        return
    text = get_strategy(coins)
    await update.message.reply_text(text)

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lūdzu norādi monētu, piem., /news BTC")
        return
    symbol = context.args[0]
    text = await news(symbol)
    await update.message.reply_text(text)

async def setalert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Lūdzu, izmanto: /setalert COIN PRICE (piem., /setalert BTC 50000)")
        return
    coin = args[0].upper()
    try:
        price = float(args[1])
    except ValueError:
        await update.message.reply_text("Lūdzu, ievadi derīgu cenu, piemēram, 50000")
        return
    add_alert(user_id, coin, price)
    await update.message.reply_text(f"✅ Brīdinājums iestatīts: {coin} pie {price} USD")

async def removealert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Lūdzu, izmanto: /removealert COIN PRICE")
        return
    coin = args[0].upper()
    try:
        price = float(args[1])
    except ValueError:
        await update.message.reply_text("Lūdzu, ievadi derīgu cenu.")
        return

    remove_alert(user_id, coin, price)
    await update.message.reply_text(f"✅ Brīdinājums par {coin} pie {price} USD noņemts.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f"Update {update} caused error: {context.error}")

# --- Асинхронная фоновая проверка алертов ---
async def alert_checker(application: Application):
    while True:
        try:
            check_alerts(application.bot)
        except Exception as e:
            logger.error(f"Kļūda alertu pārbaudē: {e}")
        await asyncio.sleep(60)

# --- Главная функция запуска ---
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.bot_data["alerts"] = load_alerts() or {}

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze))
    application.add_handler(CommandHandler("profit", profit))
    application.add_handler(CommandHandler("strategy", strategy))
    application.add_handler(CommandHandler("news", news_command))
    application.add_handler(CommandHandler("setalert", setalert_command))
    application.add_handler(CommandHandler("removealert", removealert_command))

    application.add_error_handler(error_handler)

    # Запуск фоновой проверки алертов
    application.post_init = lambda app: asyncio.create_task(alert_checker(app))

    application.run_polling()

if __name__ == "__main__":
    main()
