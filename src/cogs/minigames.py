import discord
from discord import app_commands
from discord.ext import commands
import random
from typing import Literal

class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="guess", description="Guess the number between 1 and 100 inclusive")
    @app_commands.rename(guess="number")
    async def guess(self, interaction: discord.Interaction, guess: int):
        await interaction.response.send_message(f"Guess a number between 1 and 100 inclusive.\n{interaction.user.mention}'s guess: {guess}")
        number = random.randint(1, 100)
        if guess < 1 or guess > 100:
            await interaction.followup.send("Number must be between 1 and 100.")
        elif number == guess:
            cursor = await self.bot.db.cursor()
            await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (interaction.user.id,))
            res = await cursor.fetchone()
            if res is not None:
                await cursor.execute("UPDATE users SET rice = rice + 10000 WHERE user_id = ?", (interaction.user.id,))
                await self.bot.db.commit()
                await cursor.close()
            await interaction.followup.send(f"Correct! The number was {number}.")
        else:
            await interaction.followup.send(f"you suck. it was {number}. gamble again")

    @app_commands.command(name="rps", description="Play rock paper scissors")
    @app_commands.describe(choice="Your choice: rock, paper, or scissors")
    async def rps(self, interaction: discord.Interaction, choice: Literal["rock", "paper", "scissors"]):
        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)

        if choice == bot_choice:
            await interaction.response.send_message(f"tie <:stare:1343032007277412424>\nboth chose {choice}.")
        elif (choice == "rock" and bot_choice == "scissors") or (choice == "paper" and bot_choice == "rock") or (choice == "scissors" and bot_choice == "paper"):
            await interaction.response.send_message(f"cheater <:tweaking:1386075748741157055>\nYou chose {choice}, I chose {bot_choice}.\n(+500 rice)")
            cursor = await self.bot.db.cursor()
            await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (interaction.user.id,))
            res = await cursor.fetchone()
            if res is not None:
                await cursor.execute("UPDATE users SET rice = rice + 500 WHERE user_id = ?", (interaction.user.id,))
                await self.bot.db.commit()
            await cursor.close()
        else:
            await interaction.response.send_message(f"skill issue <:lol:1371285955406991511>\nYou chose {choice}, I chose {bot_choice}.")

async def setup(bot):
    await bot.add_cog(Minigames(bot))