import random
import logging
import os
import asyncio
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
from gemini import getResponse

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

    print("Setup Complete.")

responses = [
    "I love rice.",
    "Rice is life.",
    "Rice is the best food.",
    "Rice is my favorite.",
    "I can't live without rice.",
    "Rice is the key to happiness.",
    "Rice is the food of the gods.",
    "Rice is the best thing ever.",
    "go touch grass",
    "<:stare:1343032007277412424>",
    "<:look:1386023536300396594>",
    "<:tweaking:1386075748741157055>"
]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if f"<@&{BOT_ROLE}" in message.content or "rice" in message.content.lower():
        random_response = random.choice(responses)
        await message.channel.send(f"{message.author.mention} {random_response}")

    await bot.process_commands(message)

@bot.tree.command(name="test")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(content="<:stare:1343032007277412424>")

@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Latency: {latency}ms")

@bot.tree.command(name="bonk", description="Bonk a user")
@app_commands.describe(user="The user to bonk")
async def bonk(interaction: discord.Interaction, user: discord.Member):
    cursor = await bot.db.cursor()
    await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (user.id,))
    res = await cursor.fetchone()
    if res is None:
        await interaction.response.send_message(f"{interaction.user.mention} bonked {user.mention} <:look:1386023536300396594>")
    
    await cursor.execute("UPDATE users SET rice = rice - 100 WHERE user_id = ?", (user.id,))
    await cursor.execute("UPDATE users SET rice = rice + 100 WHERE user_id = ?", (interaction.user.id,))
    await bot.db.commit()
    await cursor.close()
    await interaction.response.send_message(f"{interaction.user.mention} bonked {user.mention} and stole 100 of their rice. <:look:1386023536300396594>")
    
@bot.tree.command(name="guess", description="Guess the number between 1 and 100 inclusive")
@app_commands.rename(guess="number")
async def guess(interaction: discord.Interaction, guess: int):
    await interaction.response.send_message(f"Guess a number between 1 and 100 inclusive.\n{interaction.user.mention}'s guess: {guess}")
    number = random.randint(1, 100)
    if guess < 1 or guess > 100:
        await interaction.followup.send("Number must be between 1 and 100.")
    elif number == guess:
        cursor = await bot.db.cursor()
        await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (interaction.user.id,))
        res = await cursor.fetchone()
        if res is not None:
            await cursor.execute("UPDATE users SET rice = rice + 10000 WHERE user_id = ?", (interaction.user.id,))
            await bot.db.commit()
            await cursor.close()
        await interaction.followup.send(f"Correct! The number was {number}.")
    else:
        await interaction.followup.send(f"you suck. it was {number}. gamble again")

@bot.tree.command(name="ask", description="ask gemini anything")
async def ask(interaction: discord.Interaction, *, message: str):
    await interaction.response.defer(thinking=True)
    req = getResponse(message + " (please limit response to 150 words max)")
    await interaction.followup.send(f"**Original question: {message}**")
    await interaction.followup.send(req)

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
    else:
        roll = random.randint(1, 10)
        if roll == 1:
            ratio = amount / money
            win = round(money * ratio * 2) * random.randint(1, 5)
            money += win
            await interaction.response.send_message(f"You gambled {amount} rice and won {win} rice! You now have {money} rice.")
        else:
            money -= amount
            await interaction.response.send_message(f"You lost {amount} rice. You now have {money} rice left.")

        await cursor.execute("UPDATE users SET rice = ? WHERE user_id = ?", (money, interaction.user.id))
        await bot.db.commit()

    await cursor.close()

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
asyncio.run(bot.db.close())