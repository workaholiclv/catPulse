import os
import threading
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
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
    alerts, 
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
        "❌ /removealert BTC - Dzēst brīdinājumu \n"
        "📰 /news BTC - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
      )
    update.message.reply_text(text)

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts BTC > BTC - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
        "🆕 /setalert BTC 70000 - Jauns brīdinājums\n"
        "❌ /removealert BTC - Dzēst brīdinājumu \n"
        "📰 /news BTC - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
    )

def analyze(update: Update, context: CallbackContext):
    coins = [c.upper() for c in context.args] if context.args else get_top_coins(10)
    text = get_analysis(coins)
    update.message.reply_text(text)

def profit(update: Update, context: CallbackContext):
    coins = [c.upper() for c in context.args] if context.args else get_top_coins(10)
    text = calculate_profit(coins)
    update.message.reply_text(text)

def strategy(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Lūdzu, norādi vismaz vienu monētu piemēram:\n/strategy BTC ETH")
        return
    coins = [c.upper() for c in context.args]
    text = get_strategy(coins)
    update.message.reply_text(text)

def news(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Lūdzu, norādi monētu piemēram:\n/news BTC")
        return
    coin = context.args[0].upper()
    text = get_news(coin)
    update.message.reply_text(text)

def alerts_command(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    user_alerts = context.bot_data.get("alerts", {})
    alerts_for_user = user_alerts.get(user_id, [])
    if not alerts_for_user:
        update.message.reply_text("🚫 Tev nav iestatītu cenu brīdinājumu.")
        return
    text = "🔔 Tavi cenu brīdinājumi:\n"
    for alert in alerts_for_user:
        text += f"• {alert['coin'].upper()} pie {alert['price']} USD\n"
    update.message.reply_text(text)

def alert_add(update: Update, context: CallbackContext):
    if len(context.args) != 2:
        update.message.reply_text("Lūdzu, izmanto formātu: /alert_add monēta cena\nPiemērs: /alert_add BTC 30000")
        return
    coin = context.args[0].upper()
    try:
        price = float(context.args[1])
    except ValueError:
        update.message.reply_text("Cena jāievada kā skaitlis, piem. 30000")
        return
    user_id = update.message.from_user.id
    add_alert(user_id, coin, price)
    update.message.reply_text(f"✅ Brīdinājums iestatīts: {coin} pie {price} USD")

def alert_remove(update: Update, context: CallbackContext):
    if len(context.args) != 2:
        update.message.reply_text("Lūdzu, izmanto formātu: /alert_remove monēta cena\nPiemērs: /alert_remove BTC 30000")
        return
    coin = context.args[0].upper()
    try:
        price = float(context.args[1])
    except ValueError:
        update.message.reply_text("Cena jāievada kā skaitlis, piem. 30000")
        return
    user_id = update.message.from_user.id
    remove_alert(user_id, coin, price)
    update.message.reply_text(f"✅ Brīdinājums noņemts: {coin} pie {price} USD")

def error(update: Update, context: CallbackContext):
    logger.warning(f'Update {update} izraisīja kļūdu: {context.error}')

def main():
    load_alerts()
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.bot_data["alerts"] = alerts

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("analyze", analyze))
    dispatcher.add_handler(CommandHandler("profit", profit))
    dispatcher.add_handler(CommandHandler("strategy", strategy))
    dispatcher.add_handler(CommandHandler("news", news))
    dispatcher.add_handler(CommandHandler("alerts", alerts_command))
    dispatcher.add_handler(CommandHandler("alert_add", alert_add))
    dispatcher.add_handler(CommandHandler("alert_remove", alert_remove))

    dispatcher.add_error_handler(error)

    # Start alerts checker thread
    thread = threading.Thread(target=check_alerts, args=(updater.bot,), daemon=True)
    thread.start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
