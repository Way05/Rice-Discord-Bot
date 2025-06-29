import yfinance as yf
import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('yfinance')
logger.disabled = True
logger.propagate = False

GUILD_ID = discord.Object(id=1048428980128198677)

def parseStockData(ticker):
    res = "You shouldnt be seeing this."

    data = yf.Ticker(ticker)
    if "regularMarketPrice" not in data.info and "currency" not in data.info:
        res = f"{ticker.upper()} not found or no data available."
    else:
        price = data.info["regularMarketPrice"]
        curr = data.info["currency"]
        res = f"The current price of {ticker.upper()} is {price:.2f} {curr}."

    return res

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stock", description="Get stock information for a given ticker symbol.")
    # @app_commands.guilds(discord.Object(id=1048428980128198677))
    async def stock(self, interaction: discord.Interaction, ticker: str):
        await interaction.response.defer(thinking=True)
        response = parseStockData(ticker)
        await interaction.followup.send(response)

async def setup(bot):
    await bot.add_cog(Stocks(bot))