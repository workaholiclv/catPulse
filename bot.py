import os
import logging
import threading
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from crypto import (
    get_analysis,
    get_profit,
    get_strategy,
    alerts,
    check_alerts,
    get_news,
    get_top_trending_coins
)

# Получаем токен из переменных среды (например, Railway Variables)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "👋 Sveiki! Esmu kripto-kaķis🐾, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
        "📌 *Pieejamās komandas:*\n"
        "📈 /analyze – analīze par monētām vai top trendiem, ja nav norādīts\n"
        "💰 /profit – ieteikumi LONG/SHORT, vai top trendi, ja nav norādīts\n"
        "📈 /strategy – investīciju stratēģijas, jānorāda monētas (piem. BTC,ETH)\n"
        "🔔 /alerts SYMBOL CENA - iestata cenu, pie kuras saņemt paziņojumu (piem., /alerts BTC 65000)\n"
        "📰 /news SYMBOL - rāda jaunākās ziņas par monētu (piem., /news BTC)\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
      )
    update.message.reply_text(text)

def help_command(update: Update, context: CallbackContext):
    start(update, context)

def parse_coins(args):
    if not args:
        return None
    coins = [coin.strip().upper() for coin in ' '.join(args).split(',') if coin.strip()]
    return coins if coins else None

def analyze(update: Update, context: CallbackContext):
    coins = parse_coins(context.args)
    text = get_analysis(coins)
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def profit(update: Update, context: CallbackContext):
    coins = parse_coins(context.args)
    text = get_profit(coins)
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def strategy(update: Update, context: CallbackContext):
    coins = parse_coins(context.args)
    if not coins:
        update.message.reply_text("❗️Lūdzu, norādi vismaz vienu monētu, piemēram: /strategy BTC,ETH")
        return
    text = get_strategy(coins)
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def news(update: Update, context: CallbackContext):
    coins = parse_coins(context.args)
    if not coins or len(coins) != 1:
        update.message.reply_text("❗️Lūdzu, norādi vienu monētu, piemēram: /news BTC")
        return
    text = get_news(coins[0])
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def alert(update: Update, context: CallbackContext):
    if len(context.args) != 2:
        update.message.reply_text("❗️Izmanto: /alert MONĒTA CENA\nPiemērs: /alert BTC 70000")
        return

    coin = context.args[0].upper()
    try:
        price = float(context.args[1])
    except ValueError:
        update.message.reply_text("❗️Cenai jābūt skaitlim. Piemērs: /alert BTC 70000")
        return

    user_id = update.message.chat_id
    if user_id not in alerts:
        alerts[user_id] = []
    alerts[user_id].append({"coin": coin, "price": price})
    update.message.reply_text(f"🔔 Brīdinājums uzstādīts: {coin} sasniedz ${price:.2f}")

def check_alerts(bot):
    import time
    while True:
        for user_id, user_alerts in list(alerts.items()):
            for alert in user_alerts[:]:
                coin = alert['coin']
                price = get_current_price(coin)
                if price is None:
                    continue
                if price >= alert['price']:
                    msg = f"⚠️ {coin} ir sasniedzis ${price:.2f} (mērķis ${alert['price']:.2f})"
                    bot.send_message(chat_id=user_id, text=msg)
                    user_alerts.remove(alert)
            if not user_alerts:
                del alerts[user_id]
        time.sleep(900)  # ik pēc 15 minūtēm

def error(update: Update, context: CallbackContext):
    logger.warning(f'Update {update} izraisīja kļūdu: {context.error}')

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("analyze", analyze))
    dispatcher.add_handler(CommandHandler("profit", profit))
    dispatcher.add_handler(CommandHandler("strategy", strategy))
    dispatcher.add_handler(CommandHandler("news", news))
    dispatcher.add_handler(CommandHandler("alert", alert))

    dispatcher.add_error_handler(error)

    # Start alert checking in background
    threading.Thread(target=check_alerts, args=(updater.bot,), daemon=True).start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
