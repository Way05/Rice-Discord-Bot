import discord
from discord import app_commands
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from gemini import getResponse

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

GUILD_ID = discord.Object(id=1048428980128198677)

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
        synced = await bot.tree.sync(guild=GUILD_ID)
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

    print("Setup Complete.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if "rice" in message.content.lower():        await message.channel.send(f"{message.author.mention} <:stare:1343032007277412424>")

    await bot.process_commands(message)

@bot.tree.command(name="test", guild=GUILD_ID)
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(content="<:stare:1343032007277412424>")

@bot.command(name="ask", description="ask gemini anything")
async def ask(ctx, *, message):
    await ctx.defer()
    loading = await ctx.send("Thinking...")
    req = getResponse(message)
    await loading.delete()
    await ctx.send(req)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)