import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    print("Bot running")
    
    try:
        print("Syncing commands")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if "peenar" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} yu are not allowed to say peenar")

    await bot.process_commands(message)

@bot.hybrid_command(name="test", with_app_command=True)
async def test(ctx: commands.Context):
    await ctx.send("<:stare:1343032007277412424>")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)