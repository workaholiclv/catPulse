import os
import threading
import time
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)
from crypto import (
    get_top_coins,
    get_analysis,
    calculate_profit,
    get_strategy,
    get_news,
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


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "👋 Sveiki! Esmu kripto-kaķis🐾, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
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


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
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


def analyze(update: Update, context: CallbackContext) -> None:
    coins = context.args
    if not coins:
        coins = get_top_coins(10)
    text = get_analysis(coins)
    update.message.reply_text(text)


def profit(update: Update, context: CallbackContext) -> None:
    coins = context.args
    if not coins:
        coins = get_top_coins(10)
    text = calculate_profit(coins)
    update.message.reply_text(text)


def strategy(update: Update, context: CallbackContext) -> None:
    coins = context.args
    if not coins:
        update.message.reply_text(
            "Lūdzu, norādi vismaz vienu monētu pēc komandas, piem., /strategy BTC ETH"
        )
        return
    text = get_strategy(coins)
    update.message.reply_text(text)


def news(update: Update, context: CallbackContext) -> None:
    coins = context.args
    if not coins:
        update.message.reply_text("Lūdzu, norādi monētu pēc komandas, piem., /news BTC")
        return
    text = get_news(coins[0])
    update.message.reply_text(text)


def setalert_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 2:
        update.message.reply_text(
            "Lūdzu, izmanto: /setalert COIN PRICE (piem., /setalert BTC 50000)"
        )
        return
    coin = args[0].upper()
    try:
        price = float(args[1])
    except ValueError:
        update.message.reply_text("Lūdzu, ievadi derīgu cenu, piemēram, 50000")
        return

    alerts = context.bot_data.get("alerts", {})
    add_alert(alerts, user_id, coin, price)
    context.bot_data["alerts"] = alerts
    save_alerts(alerts)

    update.message.reply_text(f"✅ Brīdinājums iestatīts: {coin} pie {price} USD")


def removealert_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 2:
        update.message.reply_text(
            "Lūdzu, izmanto: /removealert COIN PRICE (piem., /removealert BTC 50000)"
        )
        return
    coin = args[0].upper()
    try:
        price = float(args[1])
    except ValueError:
        update.message.reply_text("Lūdzu, ievadi derīgu cenu.")
        return

    alerts = context.bot_data.get("alerts", {})
    removed = remove_alert(alerts, user_id, coin, price)
    if removed:
        context.bot_data["alerts"] = alerts
        save_alerts(alerts)
        update.message.reply_text(f"✅ Brīdinājums par {coin} pie {price} USD noņemts.")
    else:
        update.message.reply_text("⚠️ Šāds brīdinājums netika atrasts.")


def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Atjauninājums {update} izraisīja kļūdu: {context.error}")


def alert_checker_thread(bot):
    """Запуск проверки алертов в бесконечном цикле с защитой."""
    while True:
        try:
            check_alerts(bot)
        except Exception as e:
            logger.error(f"Kļūda alertu pārbaudē: {e}")
        time.sleep(60)  # проверяем каждую минуту


def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Загружаем alert'ы из файла при старте
    alerts = load_alerts()
    if alerts is None:
        alerts = {}
    dispatcher.bot_data["alerts"] = alerts

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("analyze", analyze))
    dispatcher.add_handler(CommandHandler("profit", profit))
    dispatcher.add_handler(CommandHandler("strategy", strategy))
    dispatcher.add_handler(CommandHandler("news", news))
    dispatcher.add_handler(CommandHandler("setalert", setalert_command))
    dispatcher.add_handler(CommandHandler("removealert", removealert_command))

    dispatcher.add_error_handler(error)

    # Запускаем проверку alert'ов в отдельном потоке
    thread = threading.Thread(target=alert_checker_thread, args=(updater.bot,), daemon=True)
    thread.start()

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
