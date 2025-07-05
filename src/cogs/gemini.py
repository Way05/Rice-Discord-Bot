import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
token = os.getenv("GEMINI_TOKEN")

client = genai.Client(api_key=token)
def getResponse(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    
    return response.text

class Gemini(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ask", description="ask gemini anything")
    async def ask(self, interaction: discord.Interaction, *, message: str):
        await interaction.response.defer(thinking=True)
        req = getResponse(message + " (please limit response to 150 words max)")
        await interaction.followup.send(f"**Original question: {message}**")
        await interaction.followup.send(req)

async def setup(bot):
    await bot.add_cog(Gemini(bot))