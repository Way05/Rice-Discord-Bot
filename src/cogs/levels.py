import discord
from discord import app_commands
from discord.ext import commands

def getXPToNextLevel(level):
    return round(100 * level ** 1.5)

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

async def setup(bot):
    await bot.add_cog(Levels(bot))