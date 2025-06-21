import random
import logging
import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
from gemini import getResponse

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

GUILD_ID = discord.Object(id=1048428980128198677)
BOT_ROLE = 1353587896497475678

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    print("Bot starting...")

    await bot.change_presence(activity=discord.Game('with your rice.'), status=discord.Status.dnd)

    try:
        print("Syncing commands...")
        synced = await bot.tree.sync(guild=GUILD_ID)
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
    "<:tweaking:1361430610387669134>"
]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if f"<@&{BOT_ROLE}" in message.content or "rice" in message.content.lower():
        random_response = random.choice(responses)
        await message.channel.send(f"{message.author.mention} {random_response}")

    await bot.process_commands(message)

@bot.tree.command(name="test", guild=GUILD_ID)
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(content="<:stare:1343032007277412424>")

@bot.tree.command(name="ping", description="Check the bot's latency", guild=GUILD_ID)
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Latency: {latency}ms")

@bot.tree.command(name="bonk", description="Bonk a user", guild=GUILD_ID)
@app_commands.describe(user="The user to bonk")
async def bonk(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"{interaction.user.mention} bonked {user.mention} <:look:1386023536300396594>")

@bot.tree.command(name="guess", description="Guess the number between 1 and 100 inclusive", guild=GUILD_ID)
@app_commands.rename(guess="number")
async def guess(interaction: discord.Interaction, guess: int):
    await interaction.response.send_message(f"Guess a number between 1 and 100 inclusive.\n{interaction.user.mention}'s guess: {guess}")
    number = random.randint(1, 100)
    if guess < 1 or guess > 100:
        await interaction.followup.send("Number must be between 1 and 100.")
        return
    elif number == guess:
        await interaction.followup.send(f"Correct! The number was {number}.")
    else:
        await interaction.followup.send(f"you suck. it was {number}. gamble again")

@bot.tree.command(name="ask", description="ask gemini anything", guild=GUILD_ID)
async def ask(interaction: discord.Interaction, *, message: str):
    await interaction.response.send_message("Thinking...")
    req = getResponse(message + " (please limit response to 150 words max)")
    await interaction.followup.send(f"**Original question: {message}**")
    await interaction.followup.send(req)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)