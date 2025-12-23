import discord
from discord import app_commands
from discord.ext import commands
import random

class Rice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daily", description="Claim your daily rations")
    @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id, i.user.id))
    async def daily(self, interaction: discord.Interaction):
        cursor = await self.bot.db.cursor()
        await cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)", (interaction.user.id,))
        res = await cursor.fetchone()
        if res[0] == 0:
            await interaction.response.send_message("Please register your user using ```/register``` first.")
        else:
            await cursor.execute("UPDATE users SET rice = rice + 2500 WHERE user_id = ?", (interaction.user.id,))
            await self.bot.db.commit()
            await interaction.response.send_message(f"{interaction.user.mention} claimed their daily 2500 rice!")
        await cursor.close()

    @daily.error
    async def daily_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"You can only claim your daily rations once every 24 hours. Try again in {error.retry_after:.0f} seconds.", ephemeral=True)

    @app_commands.command(name="gamble", description="Gamble with your rice")
    async def gamble(self, interaction: discord.Interaction, amount: int):
        cursor = await self.bot.db.cursor()
        await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (interaction.user.id,))
        res = await cursor.fetchone()
        if res is None:
            await interaction.response.send_message("Please register your user using ```/register``` before gambling.")
        money = res[0]
        
        if amount > money:
            await interaction.response.send_message(f"You don't have enough rice to gamble {amount} rice.")
        elif amount <= 0:
            await interaction.response.send_message(f"You cannot gamble {amount} rice.")
        else:
            roll = random.randint(1, 10)
            money -= amount
            if roll == 1:
                win = round(amount * 5 * random.randint(1, 5))
                money += win
                await interaction.response.send_message(f"You gambled {amount} rice and won {win} rice! You now have {money} rice.")
            else:
                await interaction.response.send_message(f"You lost {amount} rice. You now have {money} rice left.")

            await cursor.execute("UPDATE users SET rice = ? WHERE user_id = ?", (money, interaction.user.id))
            await self.bot.db.commit()

        await cursor.close()

    @app_commands.command(name="donate", description="donate your rice")
    async def donate(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        cursor = await self.bot.db.cursor()
        await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (user.id,))
        res = await cursor.fetchone()
        if res is None:
            await interaction.response.send_message(f"{user.name} is not registered in the DB")
            return
        await cursor.execute("SELECT rice FROM users WHERE user_id = ?", (interaction.user.id,))
        res = await cursor.fetchone()
        if res is None:
            await interaction.response.send_message(f"{interaction.user.mention} is not registered in the DB")
            return
        if amount > res[0]:
            await interaction.response.send_message("you do not have enough rice to donate")
            return
        if amount <= 0:
            await interaction.response.send_message("you cannot donate 0 or negative rice")
            return

        await cursor.execute(f"UPDATE users SET rice = rice - {amount} WHERE user_id = ?", (interaction.user.id,))
        await cursor.execute(f"UPDATE users SET rice = rice + {amount} WHERE user_id = ?", (user.id,))
        await self.bot.db.commit()
        await cursor.close()
        await interaction.response.send_message(f"{interaction.user.mention} donated {amount} rice to {user.mention}")

async def setup(bot):
    await bot.add_cog(Rice(bot))