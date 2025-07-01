import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite

class DB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="register", description="Register your user in the database.")
    async def register(self, interaction: discord.Interaction):
        cursor = await self.bot.db.cursor()

        await cursor.execute("SELECT user_id from USERS WHERE user_id = ?", (interaction.user.id,))
        res = await cursor.fetchone()
        if res is not None:
            await interaction.response.send_message(f"{interaction.user.mention} is already registered in the database.")

        await cursor.execute("INSERT INTO users(user_id) VALUES(?)", (interaction.user.id,))
        await self.bot.db.commit()
        await interaction.response.send_message(f"{interaction.user.mention} has been registered in the database.")

    @app_commands.command(name="rice", description="Check your rice balance")
    async def rice(self, interaction: discord.Interaction):
        cursor = await self.bot.db.cursor()
        await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (interaction.user.id,))
        res = await cursor.fetchone()
        if res is None:
            await interaction.response.send_message("Please register your user using ```/register``` before checking your rice balance.")
        else:
            rice_amount = res[0]
            await interaction.response.send_message(f"{interaction.user.mention}, you have {rice_amount} rice.")

    @app_commands.command(name="leaderboard", description="Check the rice leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        cursor = await self.bot.db.cursor()
        await cursor.execute("SELECT user_id, rice FROM users ORDER BY rice DESC LIMIT 5")
        res = await cursor.fetchall()
        if res is None:
            await interaction.response.send_message("No users found in the database.")

        await cursor.close()
        formatStr = "".join([f"{self.bot.get_user(data[0]).display_name}: {data[1]} rice\n" for data in res])
        await interaction.followup.send(f"**Rice Leaderboard:**\n{formatStr}")

async def setup(bot):
    await bot.add_cog(DB(bot))

    print("Loading database...")
    bot.db = await aiosqlite.connect("main.db")
    cursor = await bot.db.cursor()
    await cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER, rice INTEGER DEFAULT 5000)")
    await bot.db.commit()
    await cursor.close()
    print("Database loaded.")