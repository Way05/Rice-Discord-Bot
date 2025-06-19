import discord
from discord import app_commands
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.all()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    print("Bot starting...")

    await bot.change_presence(activity=discord.Game('eating rice.'), status=discord.Status.dnd)

    try:
        print("Syncing commands...")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

    print("Setup Complete.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if "rice" in message.content.lower():
        # await message.delete()
        await message.channel.send(f"{message.author.mention} <:stare:1343032007277412424>")

    await bot.process_commands(message)

@bot.hybrid_command()
async def test(ctx: discord.Interaction):
    await ctx.defer()   
    await ctx.response.send_message("<:stare:1343032007277412424>", ephemeral=True)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)