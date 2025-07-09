import os
import threading
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from crypto import get_news, analyze_market, check_alerts, get_profit, get_strategy

# 🌍 Ielādē .env failu
load_dotenv()

# Получаем токен из переменных среды (например, Railway Variables)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# 📒 Logger konfigurācija
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "👋 Sveiki! Esmu kripto-kaķis🐾, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts BTC > BTC - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
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
        "📰 /news BTC - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
    )


def news_command(update: Update, context: CallbackContext):
    text = get_news()
    update.message.reply_text(text, parse_mode="Markdown")


def analyze_command(update: Update, context: CallbackContext):
    text = analyze_market()
    update.message.reply_text(text, parse_mode="Markdown")


def alerts_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = check_alerts(user_id=user_id, manual=True)
    update.message.reply_text(text, parse_mode="Markdown")


def profit_command(update: Update, context: CallbackContext):
    text = get_profit(update, context)
    update.message.reply_text(text, parse_mode="Markdown")


def strategy_command(update: Update, context: CallbackContext):
    text = get_strategy()
    update.message.reply_text(text, parse_mode="Markdown")


def error(update: object, context: CallbackContext):
    print(f"⚠️ Update {update} вызвал ошибку: {context.error}")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # 🔌 Komandu apstrāde
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("news", news_command))
    dp.add_handler(CommandHandler("analyze", analyze_command))
    dp.add_handler(CommandHandler("alerts", alerts_command))
    dp.add_handler(CommandHandler("profit", profit_command))
    dp.add_handler(CommandHandler("strategy", strategy_command))

    # ⚠️ Kļūdu apstrāde
    dp.add_error_handler(error)

    # ⏰ Startē brīdinājumu pārbaudes pavedienu
    thread = threading.Thread(target=check_alerts, args=(updater.bot,), daemon=True)
    thread.start()

    # 🚀 Startē botu
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
