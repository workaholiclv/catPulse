import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from crypto import get_analysis, get_profit, get_strategy

# Glabājam lietotāja monētas
user_coins = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "👋 Sveiki! Esmu kripto-kaķis🐈‍⬛, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
        "📌 *Pieejamās komandas:*\n"
        "💰 /setcoins – iestata monētas (var vairākas caur komatu, piem. BTC,ETH,CRO)\n"
        "📈 /analyze – rāda pašreizējo analīzi par iestatītajām monētām\n"
        "📊 /profit – rāda ieteikumus par ilgo vai īso pozīciju\n"
        "🧠 /strategy – parāda investīciju stratēģijas\n"
        "❓ /help – palīdzība",
        parse_mode='Markdown'
    )

def help_command(update: Update, context: CallbackContext) -> None:
    start(update, context)

def set_coins(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if context.args:
        coins = [coin.strip().upper() for coin in ",".join(context.args).split(",")]
        user_coins[user_id] = coins
        update.message.reply_text(f"💰 Iestatītas monētas: {', '.join(coins)}")

        analysis = get_analysis(coins)
        profit = get_profit(coins)
        update.message.reply_text(f"📈 Analīze:\n{analysis}")
        update.message.reply_text(f"📊 Profita iespējas:\n{profit}")
    else:
        update.message.reply_text("⚠️ Lūdzu, ievadi monētas. Piemērs: /setcoins BTC,ETH")

def analyze(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    coins = user_coins.get(user_id)
    if not coins:
        update.message.reply_text("⚠️ Vispirms iestati monētas ar /setcoins")
        return
    analysis = get_analysis(coins)
    update.message.reply_text(f"📈 Analīze:\n{analysis}")

def profit(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    coins = user_coins.get(user_id)
    if not coins:
        update.message.reply_text("⚠️ Vispirms iestati monētas ar /setcoins")
        return
    profit = get_profit(coins)
    update.message.reply_text(f"📊 Profita iespējas:\n{profit}")

def strategy(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    coins = user_coins.get(user_id)
    if not coins:
        update.message.reply_text("⚠️ Vispirms iestati monētas ar /setcoins")
        return
    strategies = get_strategy(coins)
    update.message.reply_text(f"🧠 Stratēģijas:\n{strategies}")

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("ERROR: TELEGRAM_BOT_TOKEN nav iestatīts.")

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("setcoins", set_coins))
    dispatcher.add_handler(CommandHandler("analyze", analyze))
    dispatcher.add_handler(CommandHandler("profit", profit))
    dispatcher.add_handler(CommandHandler("strategy", strategy))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
