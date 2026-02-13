import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
import asyncio
import random

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

GUILD_ID = discord.Object(id=1048428980128198677)
GUILD_NONE = None
BOT_ROLE = 1353587896497475678
A_ROLE = 1277078129793437716

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    print("Bot starting...")
    print(f"Logged in as: {bot.user.name}#{bot.user.discriminator}")

    await bot.change_presence(activity=discord.Game('with your rice.'), status=discord.Status.dnd)

    print("Loading cogs...")
    for cog in os.listdir("./src/cogs"):
        if cog.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{cog[:-3]}")
                # print(f"Loaded cog: {cog[:-3]}")
            except Exception as e:
                print(f"Failed to load cog {cog[:-3]}: {e}")
    print("All cogs loaded.")

    try:
        print("Syncing commands...")
        # bot.tree.clear_commands(guild=GUILD_ID)
        # bot.tree.clear_commands(guild=GUILD_NONE)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

    await bot.get_channel(1048428980128198680).send("<:ri:1421658076993421383>")

    print("Setup Complete.")

responses = [
    "I love rice.",
    "我爱米饭。",
    # "Rice is life.",
    # "Rice is the best food.",
    "Rice is my favorite.",
    # "I can't live without rice.",
    # "Rice is the key to happiness.",
    # "Rice is the food of the gods.",
    # "Rice is the best thing ever.",
    "go touch grass",
    "<:stare:1343032007277412424>",
    "<:look:1386023536300396594>",
    "<:tweaking:1386075748741157055>",
    "<:rice_spin:1391523995916046490>",
    "<:ri:1421658076993421383>"
]

filter_enabled = False
censored = os.getenv("CENSORED").split(",")

def is_guild_owner():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == interaction.guild.owner_id
    
    return app_commands.check(predicate)

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    
    if f"<@&{BOT_ROLE}" in message.content or "rice" in message.content.lower():
        random_response = random.choice(responses)
        await message.channel.send(f"{message.author.mention} {random_response}")

    # if filter_enabled and any(word in message.content.lower() for word in censored):
        # message.delete()
        # await message.channel.send(f"{message.author.mention} yu can not say that <:stare:1343032007277412424>")
    if filter_enabled:
        for word in censored:
            if word in message.content.lower():
                await message.delete()
                await message.channel.send(f"{message.author.mention} yu cannot say {word} <:stare:1343032007277412424>")
                return

    await bot.process_commands(message)

@bot.tree.command(name="test")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(content="<:stare:1343032007277412424>")

@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Latency: `{latency}ms`")

@bot.tree.command(name="filter", description="Toggle the filter on or off")
@is_guild_owner()
async def filter(interaction: discord.Interaction):
    global filter_enabled
    filter_enabled = not filter_enabled
    status = "enabled" if filter_enabled else "disabled"
    await interaction.response.send_message(f"brainrot filter is now {status}")

@filter.error
async def filter_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

@bot.tree.command(name="announce", description="send a message")
async def announce(interaction: discord.Interaction, channel: discord.TextChannel, ping: discord.Role | discord.User = None, *, message: str):
    if not ping:
        await bot.get_channel(channel.id).send(message)
    else:
        await bot.get_channel(channel.id).send(f"{ping.mention} {message}")
    await interaction.response.send_message("message successful", ephemeral=True)

@bot.tree.command(name="bonk", description="Bonk a user")
@app_commands.describe(user="The user to bonk")
async def bonk(interaction: discord.Interaction, user: discord.Member):
    cursor = await bot.db.cursor()
    await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (user.id,))
    res = await cursor.fetchone()
    if res is None:
        await interaction.response.send_message(f"{interaction.user.mention} bonked {user.mention} <:look:1386023536300396594>")
    
    riceToSteal = 100
    if res[0] < riceToSteal and res[0] > 0:
        riceToSteal = res[0]
    elif res[0] <= 0:
        await interaction.response.send_message(f"{interaction.user.mention} bonked {user.mention}, but they had no rice to steal <:look:1386023536300396594>")

    await cursor.execute(f"UPDATE users SET rice = rice - {riceToSteal} WHERE user_id = ?", (user.id,))
    await cursor.execute(f"UPDATE users SET rice = rice + {riceToSteal} WHERE user_id = ?", (interaction.user.id,))
    await bot.db.commit()
    await cursor.close()
    await interaction.response.send_message(f"{interaction.user.mention} bonked {user.mention} and stole {riceToSteal} of their rice. <:look:1386023536300396594>")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
asyncio.run(bot.db.close())