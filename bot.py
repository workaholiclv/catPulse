import os
from telegram.ext import Updater, CommandHandler
from crypto import get_analysis, get_profit_suggestion, get_trending_coins

user_coins = {}

def start(update, context):
    welcome_text = (
        "👋 Sveiki! Esmu kripto-kaķis🐈‍⬛, kas palīdzēs tev ar monētu 🪙 analīzi.\n\n"
         "📌 Pieejamās komandas:\n"
        "/start — parādīt šo sveicienu\n"
        "/analyze — saņemt pašreizējo analīzi par populārākajām vai tavām monētām\n"
        "/profit — ieteikumi ilgajām (long) un īsajām (short) pozīcijām\n"
        "/setcoins [monētas] — iestatīt savas monētas analīzei\n"
        "/strategy — ieguldījumu stratēģiju apraksts\n\n"
        "⚡ Piemērs lietošanai:\n"
        "/setcoins bitcoin, ethereum, dogecoin\n"
        "Pēc monētu iestatīšanas es uzreiz nosūtīšu analīzi un tirdzniecības signālus.\n\n"
        "Ja monētas netiek iestatītas, analīze tiek veikta par aktuālajām tendencēm."
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)

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
    if context.args:
        coins_str = " ".join(context.args)
        coins_list = [coin.strip() for coin in coins_str.split(",") if coin.strip()]
        if coins_list:
            user_coins[chat_id] = coins_list
            context.bot.send_message(chat_id, f"✅ Monētas iestatītas: {', '.join(coins_list)}")
            analysis = get_analysis(coins_list)
            profit = get_profit_suggestion(coins_list)
            context.bot.send_message(chat_id, analysis)
            context.bot.send_message(chat_id, profit)
            return
    context.bot.send_message(chat_id, "⚠️ Lūdzu, norādi monētas pēc komandas, piemēram:\n/setcoins bitcoin, ethereum")

def strategy(update, context):
    text = (
        "📊 Ieguldījumu stratēģijas:\n\n"
        "1️⃣ LONG (Pozīcija ilgtermiņā):\n"
        "- Pērk aktīvu, cerot uz tā cenu pieaugumu.\n"
        "- Stop-loss parasti tiek iestatīts 5-10% zem pirkuma cenas.\n"
        "- Take-profit var iestatīt +10-30% atkarībā no mērķa.\n\n"
        "2️⃣ SHORT (Pozīcija īstermiņā, cenu krituma gadījumā):\n"
        "- Aizņemas aktīvu pārdošanai, cerot to vēlāk atpirkt lētāk.\n"
        "- Stop-loss ierobežo zaudējumus, piemēram, +5-10% virs pārdošanas cenas.\n"
        "- Take-profit fiksē peļņu cenu krišanas gadījumā, piemēram, -10-30%.\n\n"
        "⚠️ Vienmēr izmanto stop-loss, lai kontrolētu riskus.\n"
        "🧠 Pirms stratēģiju izmantošanas rūpīgi analizē tirgu un jaunākās ziņas."
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("Nav iestatīta BOT_TOKEN mainīgā vide. Pievieno sava bota tokenu!")
    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("analyze", analyze))
    dp.add_handler(CommandHandler("profit", profit))
    dp.add_handler(CommandHandler("setcoins", set_user_coins))
    dp.add_handler(CommandHandler("strategy", strategy))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
