import discord
from bot_token import discord_bot
from discord.commands import Option

intents = discord.Intents.default()
intents.messages = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} ist Online")

user_data = {}  # Dictionary zur Speicherung von Benutzerdaten

@bot.event
async def on_message(message):
    if message.author.id not in user_data:
        user_data[message.author.id] = {"message_count": 1, "level": 1, "messages_needed": 5}
    else:
        user_data[message.author.id]["message_count"] += 1
        # Wenn die Anzahl der Nachrichten das benötigte Level erreicht hat
        if user_data[message.author.id]["message_count"] >= user_data[message.author.id]["messages_needed"]:
            user_data[message.author.id]["level"] += 1
            user_data[message.author.id]["messages_needed"] = user_data[message.author.id]["level"] * 5
            user_data[message.author.id]["message_count"] = 0
            # Vorherige Levelrolle entfernen
            await remove_previous_level_role(message.author, user_data[message.author.id]["level"])
            # Neue Levelrolle zuweisen
            await assign_level_role(message.author, user_data[message.author.id]["level"])

    #await bot.process_commands(message)

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

@bot.slash_command()
async def message_count(ctx, member: discord.Member):
    message_count = user_data.get(member.id, {}).get("message_count", 0)
    await ctx.respond(f"{member.name} hat {message_count} Nachrichten gesendet.")

@bot.slash_command(description="Zeigt dir dein Level an")
async def level(ctx, user: Option(discord.Member, "Der Benutzer dessen Level du sehen möchtest")):
    level = user_data.get(user.id, {}).get("level", 1)
    await ctx.respond(f"{user} ist auf dem **Level {level}**")

# Verbinde den Bot mit dem Discord-Server
bot.run(discord_bot.token)
