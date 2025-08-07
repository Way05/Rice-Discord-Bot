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

    # await bot.get_channel(1290759844797612042).send(f"<@&{1295377234508644352}> OPEN YOUR GIFTS <:angry:1399203078728581141><:angry:1399203078728581141><:angry:1399203078728581141>")

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
    "<:rice_spin:1391523995916046490>"
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
        await message.delete()
        for word in censored:
            if word in message.content.lower():
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

@bot.tree.command(name="daily", description="Claim your daily rations")
@app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id, i.user.id))
async def daily(interaction: discord.Interaction):
    cursor = await bot.db.cursor()
    await cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)", (interaction.user.id,))
    res = await cursor.fetchone()
    if res[0] == 0:
        await interaction.response.send_message("Please register your user using ```/register``` first.")
    else:
        await cursor.execute("UPDATE users SET rice = rice + 2500 WHERE user_id = ?", (interaction.user.id,))
        await bot.db.commit()
        await interaction.response.send_message(f"{interaction.user.mention} claimed their daily 2500 rice!")
    await cursor.close()

@daily.error
async def daily_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"You can only claim your daily rations once every 24 hours. Try again in {error.retry_after:.0f} seconds.", ephemeral=True)

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
    elif res[0] == 0:
        await interaction.response.send_message(f"{interaction.user.mention} bonked {user.mention}, but they had no rice to steal <:look:1386023536300396594>")

    await cursor.execute(f"UPDATE users SET rice = rice - {riceToSteal} WHERE user_id = ?", (user.id,))
    await cursor.execute(f"UPDATE users SET rice = rice + {riceToSteal} WHERE user_id = ?", (interaction.user.id,))
    await bot.db.commit()
    await cursor.close()
    await interaction.response.send_message(f"{interaction.user.mention} bonked {user.mention} and stole {riceToSteal} of their rice. <:look:1386023536300396594>")

@bot.tree.command(name="gamble", description="Gamble with your rice")
async def gamble(interaction: discord.Interaction, amount: int):
    cursor = await bot.db.cursor()
    await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (interaction.user.id,))
    res = await cursor.fetchone()
    if res is None:
        await interaction.response.send_message("Please register your user using ```/register``` before gambling.")
    money = res[0]
    
    if amount > money:
        await interaction.response.send_message(f"You don't have enough rice to gamble {amount} rice.")
    elif amount <= 0:
        await interaction.response.send_message(f"You cannot gamble {amount} rice.")
    else:
        roll = random.randint(1, 10)
        money -= amount
        if roll == 1:
            win = round(amount * 5 * random.randint(1, 5))
            money += win
            await interaction.response.send_message(f"You gambled {amount} rice and won {win} rice! You now have {money} rice.")
        else:
            await interaction.response.send_message(f"You lost {amount} rice. You now have {money} rice left.")

        await cursor.execute("UPDATE users SET rice = ? WHERE user_id = ?", (money, interaction.user.id))
        await bot.db.commit()

    await cursor.close()

@bot.tree.command(name="donate", description="donate your rice")
async def donate(interaction: discord.Interaction, user: discord.Member, amount: int):
    cursor = await bot.db.cursor()
    await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (user.id,))
    res = await cursor.fetchone()
    if res is None:
        await interaction.response.send_message(f"{user.name} is not registered in the DB")
        return
    await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (interaction.user.id,))
    res = await cursor.fetchone()
    if res is None:
        await interaction.response.send_message(f"{interaction.user.mention} is not registered in the DB")
        return
    if amount > res[0]:
        await interaction.response.send_message("you do not have enough rice to donate")
        return
    if amount <= 0:
        await interaction.response.send_message("you cannot donate 0 or negative rice")
        return

    await cursor.execute(f"UPDATE users SET rice = rice - {amount} WHERE user_id = ?", (interaction.user.id,))
    await cursor.execute(f"UPDATE users SET rice = rice + {amount} WHERE user_id = ?", (user.id,))
    await bot.db.commit()
    await cursor.close()
    await interaction.response.send_message(f"{interaction.user.mention} donated {amount} rice to {user.mention}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
asyncio.run(bot.db.close())