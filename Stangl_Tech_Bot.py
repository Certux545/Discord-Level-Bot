import discord
import asyncio
import json
from bot_token import discord_bot
from discord.commands import Option

intents = discord.Intents.default()
intents.messages = True

bot = discord.Bot(intents=intents)

# Laden der Benutzerdaten beim Start des Bots
user_data = {}  # Dictionary zur Speicherung von Benutzerdaten

async def load_user_data():
    try:
        with open("user_data.json", "r") as file:
            user_data.update(json.load(file))
        print("Benutzerdaten wurden geladen.")
    except FileNotFoundError:
        print("Keine Benutzerdaten gefunden. Neue Datei wird erstellt.")

async def save_user_data():
    try:
        with open("user_data.json", "w") as file:
            json.dump(user_data, file)
        print("Benutzerdaten wurden gespeichert.")
    except Exception as e:
        print("Fehler beim Speichern der Benutzerdaten:", e)

@bot.event
async def on_ready():
    print(f"{bot.user} ist Online")
    # Lade die Benutzerdaten beim Start des Bots
    await load_user_data()
    # Starte den Task, um die Benutzerdaten alle 5 Minuten zu speichern
    bot.loop.create_task(save_user_data_periodically())

async def save_user_data_periodically():
    while True:
        await asyncio.sleep(300)  # Warte 5 Minuten
        # Speichere die Benutzerdaten
        await save_user_data()

@bot.event
async def on_message(message):
    user_id = str(message.author.id)
    if user_id not in user_data:
        user_data[user_id] = {"message_count": 1, "level": 1, "messages_needed": 5}
    else:
        user_data[user_id]["message_count"] += 1
        # Wenn die Anzahl der Nachrichten das benötigte Level erreicht hat
        if user_data[user_id]["message_count"] >= user_data[user_id]["messages_needed"]:
            user_data[user_id]["level"] += 1
            user_data[user_id]["messages_needed"] = user_data[user_id]["level"] * 5
            user_data[user_id]["message_count"] = 0
            # Vorherige Levelrolle entfernen
            await remove_previous_level_role(message.author, user_data[user_id]["level"])
            # Neue Levelrolle zuweisen
            await assign_level_role(message.author, user_data[user_id]["level"])

async def remove_previous_level_role(member, level):
    guild = member.guild
    previous_level_role_name = f"Level {level - 1}"
    previous_level_role = discord.utils.get(guild.roles, name=previous_level_role_name)
    if previous_level_role is not None:
        await member.remove_roles(previous_level_role)

async def assign_level_role(member, level):
    guild = member.guild
    role_name = f"Level {level}"  # Name der Rolle entsprechend des Levels
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        # Rolle existiert nicht, daher erstellen
        role = await guild.create_role(name=role_name)
    # Rolle dem Benutzer zuweisen
    await member.add_roles(role)

@bot.slash_command(description="Zeigt dir dein Level an")
async def level(ctx, user: Option(discord.Member, "Der Benutzer dessen Level du sehen möchtest")):
    user_id = str(user.id)
    user_level_data = user_data.get(user_id, {"level": 1})
    level = user_level_data["level"]
    await ctx.respond(f"{user} ist auf dem **Level {level}**")

@bot.slash_command(description="Speichert die Benutzerdaten manuell")
async def save_data(ctx):
    await save_user_data()
    await ctx.respond("Benutzerdaten wurden manuell gespeichert.")

# Verbinde den Bot mit dem Discord-Server
bot.run(discord_bot.token)
