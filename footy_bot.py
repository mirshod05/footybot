import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
# API Setup
API_KEY = '7af07ae61c2116f90aaa3f1c004f0e1d'
BASE_URL = 'https://v3.football.api-sports.io'

LEAGUES = {
    "1": 39,    # Premier League
    "2": 140,   # La Liga
    "3": 135,   # Serie A
    "4": 78,    # Bundesliga
    "5": 61,    # Ligue 1
    "6": 253,   # MLS
    "7": 307    # Saudi Pro League
}

user_state = {}

headers = {
    'x-apisports-key': API_KEY
    }

def get_stats(name, season, league_id):
    url = f"{BASE_URL}/players"
    params = {
        "search": name,
        "season": season,
        "league": league_id
    }

    response = requests.get(url, headers=headers,params=params)
    data = response.json()
    #print(data)

    if not data['response']:
        return f"No stats found for {name}."

    player = data['response'][0]
    info = player['player']
    stats = player['statistics'][0]

    result = (
        f"Stats for {info['name']}, {info['age']} years old, {info['nationality']}:\n"
        f"Team: {stats['team']['name']}\n"
        f"Appearances: {stats['games']['appearences']}\n"
        f"Goals: {stats['goals']['total']}\n"
        f"Assists: {stats['goals']['assists']}\n"
    )
    return result


# Telegram bot
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_state[chat_id] = {"step": "league"}
    await update.message.reply_text(
        "Hi and welcome to FootyBot!\n"
        "This bot gives you a players league stats from a given season.\n"
        "Choose a league by entering its number:\n"
        "1 - Premier League\n"
        "2 - La Liga\n"
        "3 - Serie A\n"
        "4 - Bundesliga\n"
        "5 - Ligue 1\n"
        "6 - MLS\n"
        "7 - Saudi Pro League\n"
    )

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if chat_id not in user_state:
        user_state[chat_id] = {"step": "league"}
        await update.message.reply_text("Let's start! Choose a league by its number:")
        return
    state = user_state[chat_id]

    if state["step"] == "league":
        if text not in LEAGUES:
            await update.message.reply_text("Please type in a valid league number.")
            return
        state["league_id"] = LEAGUES[text]
        state["step"] = "season"
        await update.message.reply_text("Now enter the season (e.g. 2023 for 23/24):")

    elif state["step"] == "season":
        if not text.isdigit():
            await update.message.reply_text("Enter a valid year up to 2023:")
            return
        state["season"] = int(text)
        state["step"] = "player"
        await update.message.reply_text("Now enter the player's name:")

    elif state["step"] == "player":
        league_id = state["league_id"]
        season = state["season"]
        name = text

        reply = get_stats(name, season, league_id)
        await update.message.reply_text(reply)

        # Reset cycle
        user_state[chat_id] = {"step": "league"}
        await update.message.reply_text(
            "Want to search again? Choose the league:\n"
            "1 - Premier League\n"
            "2 - La Liga\n"
            "3 - Serie A\n"
            "4 - Bundesliga\n"
            "5 - Ligue 1\n"
            "6 - MLS\n"
            "7 - Saudi Pro League\n"
        )
        

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))

print("Bot is running..")
app.run_polling()
