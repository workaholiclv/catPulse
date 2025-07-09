import requests

COINPAPRIKA_API = "https://api.coinpaprika.com/v1"

def get_coin_id(symbol):
    """Atrod monētas ID pēc simbolu."""
    try:
        response = requests.get(f"{COINPAPRIKA_API}/coins")
        response.raise_for_status()
        coins = response.json()
        for coin in coins:
            if coin["symbol"].upper() == symbol.upper() and coin["type"] == "coin":
                return coin["id"]
        return None
    except Exception as e:
        print(f"Kļūda meklējot ID priekš {symbol}: {e}")
        return None

def get_price_data(symbol):
    """Atgriež pilnus datus par monētu no Coinpaprika."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        print(f"Nevarēja atrast ID priekš {symbol}")
        return None
    try:
        response = requests.get(f"{COINPAPRIKA_API}/tickers/{coin_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Kļūda iegūstot cenu datus priekš {symbol}: {e}")
        return None

def get_top_coins(limit=10):
    """Atgriež top monētu simbolus pēc Coinpaprika ranga."""
    try:
        response = requests.get(f"{COINPAPRIKA_API}/coins")
        response.raise_for_status()
        coins = response.json()
        coins_filtered = [c for c in coins if c.get("rank") and c.get("type") == "coin"]
        coins_sorted = sorted(coins_filtered, key=lambda x: x["rank"])
        return [coin["symbol"].upper() for coin in coins_sorted[:limit]]
    except Exception as e:
        print(f"Kļūda iegūstot top monētas: {e}")
        return []

def get_analysis(coins=None):
    """Sniedz tirgus analīzi par monētām."""
    if not coins:
        coins = get_top_coins()
    output = "📊 *Tirgus analīze:*\n\n"
    for symbol in coins:
        data = get_price_data(symbol)
        if not data:
            output += f"🔸 {symbol}: ❌ Neizdevās iegūt datus\n"
            continue
        try:
            price = data["quotes"]["USD"]["price"]
            change_24h = data["quotes"]["USD"]["percent_change_24h"]
            output += f"🔸 {symbol}: ${price:.2f} ({change_24h:+.2f}%)\n"
        except KeyError:
            output += f"🔸 {symbol}: ❌ Nepilni dati\n"
    return output

def get_profit(coins=None):
    """Sniedz ieteikumus par pozīcijām (long/short) pēc 24h cenu izmaiņām."""
    if not coins:
        coins = get_top_coins()
    output = "💰 *Pozīciju ieteikumi:*\n\n"
    for symbol in coins:
        data = get_price_data(symbol)
        if not data:
            output += f"{symbol}: ❌ Neizdevās iegūt datus\n"
            continue
        try:
            change_24h = data["quotes"]["USD"]["percent_change_24h"]
            if change_24h > 3:
                pos = "📈 Ilgā pozīcija (pirkt un turēt)"
            elif change_24h < -3:
                pos = "📉 Īsā pozīcija (pārdot vai spekulēt uz kritumu)"
            else:
                pos = "⚖️ Neitrāli"
            output += f"{symbol}: {pos} ({change_24h:+.2f}%)\n"
        except KeyError:
            output += f"{symbol}: ❌ Nepilni dati\n"
    return output

def get_strategy(coins):
    """Sniedz stratēģijas ieteikumus ar papildu analīzi."""
    output = "📈 *Stratēģija:*\n\n"
    for symbol in coins:
        data = get_price_data(symbol)
        if not data:
            output += f"{symbol}: ❌ Neizdevās iegūt datus\n\n"
            continue
        try:
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
                f"• Ieguldi pakāpeniski (DCA — pakāpeniska iegāde pa daļām).\n"
                f"• Pārdod daļu, kad peļņa sasniedz +10% (take profit).\n"
                f"• Izmanto stop-loss — automātisku pārdošanu, ja cena krītas pēc kāpuma.\n\n"
            )
        except KeyError:
            output += f"{symbol}: ❌ Nepilni dati\n\n"
    return output

def get_news(symbol):
    """Mēģina ielādēt jaunākās ziņas par monētu (Coinpaprika neatbalsta ziņas visām monētām)."""
    try:
        coin_id = get_coin_id(symbol)
        if not coin_id:
            return f"❌ Nevarēja atrast {symbol} ziņas."
        response = requests.get(f"{COINPAPRIKA_API}/coins/{coin_id}/events")
        response.raise_for_status()
        events = response.json()
        if not events:
            return f"ℹ️ Nav jaunāko ziņu priekš {symbol}."
        news_text = f"📰 *Jaunākās ziņas par {symbol.upper()}:*\n\n"
        for event in events[:5]:
            news_text += f"• {event.get('title', 'Bez virsraksta')}\n  {event.get('description', '')}\n\n"
        return news_text
    except Exception as e:
        print(f"Kļūda ielādējot ziņas priekš {symbol}: {e}")
        return "❌ Neizdevās ielādēt jaunākās ziņas."
