import requests
import time

COINPAPRIKA_API = "https://api.coinpaprika.com/v1"

# Кеш для маппинга символов в id
_symbol_to_id_cache = {}

def load_symbol_to_id_map():
    global _symbol_to_id_cache
    try:
        response = requests.get(f"{COINPAPRIKA_API}/coins")
        response.raise_for_status()
        coins = response.json()
        # Сохраняем только монеты типа "coin"
        _symbol_to_id_cache = {
            coin['symbol'].lower(): coin['id']
            for coin in coins if coin['type'] == 'coin'
        }
    except Exception as e:
        print(f"Kļūda ielādējot simbolu un ID mapi: {e}")

def get_coin_id(symbol):
    symbol = symbol.lower()
    if not _symbol_to_id_cache:
        load_symbol_to_id_map()
    return _symbol_to_id_cache.get(symbol)

def get_top_trending_coins(limit=10):
    """Возвращает топ монет по росту за 24 часа"""
    try:
        response = requests.get(f"{COINPAPRIKA_API}/tickers")
        response.raise_for_status()
        tickers = response.json()
        # Фильтруем и сортируем по изменению за 24 часа по убыванию
        coins = [t for t in tickers if t['rank'] and t['rank'] > 0]
        sorted_coins = sorted(coins, key=lambda x: x['quotes']['USD']['percent_change_24h'], reverse=True)
        top_symbols = [coin['symbol'].upper() for coin in sorted_coins[:limit]]
        return top_symbols
    except Exception as e:
        print(f"Kļūda iegūstot top monētas: {e}")
        return []

def get_price_data(symbol):
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return None
    try:
        response = requests.get(f"{COINPAPRIKA_API}/tickers/{coin_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Kļūda iegūstot cenu datus priekš {symbol}: {e}")
        return None

def get_current_price(symbol):
    data = get_price_data(symbol)
    if not data:
        return None
    return data["quotes"]["USD"]["price"]

alerts = {}  # Piemēram, {"user_id": [{"coin": "btc", "price": 65000}]}

def check_alerts(bot):
    """Pārbauda alertus un sūta paziņojumus (vajadzētu izsaukt atsevišķā pavedienā vai plānotājā)."""
    while True:
        for user_id, user_alerts in list(alerts.items()):
            for alert in user_alerts:
                coin = alert['coin'].lower()
                target_price = alert['price']
                price = get_current_price(coin)
                if price is None:
                    continue
                if price >= target_price:
                    text = f"⚠️ Cena {coin.upper()} sasniedz {price} USD (mērķis {target_price} USD)!"
                    try:
                        bot.send_message(chat_id=user_id, text=text)
                    except Exception as e:
                        print(f"Kļūda sūtot ziņu: {e}")
                    user_alerts.remove(alert)
            if not user_alerts:
                del alerts[user_id]
        time.sleep(900)  # 15 minūtes

def get_news(symbol):
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return "❌ Nevar atrast monētu."
    try:
        r = requests.get(f"{COINPAPRIKA_API}/coins/{coin_id}/events")
        r.raise_for_status()
        events = r.json()
        news_text = f"📰 Jaunākās ziņas par {symbol.upper()}:\n\n"
        # Отображаем последние 5 событий
        for event in events.get('events', [])[:5]:
            news_text += f"• {event.get('title', 'Bez nosaukuma')}\n  {event.get('source', {}).get('url', '')}\n\n"
        if news_text.strip() == f"📰 Jaunākās ziņas par {symbol.upper()}:":
            news_text += "Nav pieejamu jaunumus."
        return news_text
    except Exception as e:
        print(f"Kļūda ielādējot jaunākās ziņas: {e}")
        return "Neizdevās ielādēt jaunākās ziņas."

def get_analysis(coins=None):
    if not coins:
        coins = get_top_trending_coins(10)
    output = "📊 *Tirgus analīze:*\n\n"
    for symbol in coins:
        data = get_price_data(symbol)
        if not data:
            output += f"{symbol}: ❌ Neizdevās iegūt datus\n"
            continue
        price = data["quotes"]["USD"]["price"]
        change_24h = data["quotes"]["USD"]["percent_change_24h"]
        output += f"🔸 {symbol}: ${price:.2f} ({change_24h:+.2f}%)\n"
    return output

def get_profit(coins=None):
    if not coins:
        coins = get_top_trending_coins(10)
    output = "💰 *Pozīciju ieteikumi:*\n\n"
    for symbol in coins:
        data = get_price_data(symbol)
        if not data:
            output += f"{symbol}: ❌ Neizdevās iegūt datus\n"
            continue
        change_24h = data["quotes"]["USD"]["percent_change_24h"]
        if change_24h > 3:
            pos = "📈 Ilgā pozīcija (pirkt un turēt)"
        elif change_24h < -3:
            pos = "📉 Īsā pozīcija (pārdot vai spekulēt uz kritumu)"
        else:
            pos = "⚖️ Neitrāli"
        output += f"{symbol}: {pos} ({change_24h:+.2f}%)\n"
    return output

def get_strategy(coins):
    output = "📈 *Stratēģija:*\n\n"
    for symbol in coins:
        data = get_price_data(symbol)
        if not data:
            output += f"{symbol}: ❌ Neizdevās iegūt datus\n"
            continue
        q = data["quotes"]["USD"]
        price = q["price"]
        change_24h = q.get("percent_change_24h", 0)
        change_7d = q.get("percent_change_7d", 0)
        change_30d = q.get("percent_change_30d", 0)

        output += (
            f"🔹 {symbol}\n"
            f"💵 Cena: ${price:.2f}\n"
            f"🔄 24h: {change_24h:+.2f}% | 7d: {change_7d:+.2f}% | 30d: {change_30d:+.2f}%\n"
            f"📌 Stratēģija:\n"
            f"• Ieguldi pakāpeniski — tā saucamā DCA metode (Dollar-Cost Averaging), iegādājoties aktīvu pa daļām neatkarīgi no cenas.\n"
            f"• Pārdod daļu, kad peļņa sasniedz +10% (take profit).\n"
            f"• Izmanto stop loss — tas ir aizsardzības mehānisms, kas automātiski pārdod, ja cena sāk krist pēc kāpuma.\n\n"
        )
    return output
