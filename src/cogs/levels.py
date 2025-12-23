import discord
from discord import app_commands
from discord.ext import commands, tasks

sessionLevelData = {}

async def loadLevelData(bot):
    cursor = await bot.db.cursor()
    await cursor.execute("SELECT user_id, level, xp FROM users")
    res = await cursor.fetchall()
    for data in res:
        sessionLevelData[data[0]] = {
            "level": data[1],
            "xp": data[2]
        }
    await cursor.close()

def getXPToNextLevel(level):
    return round(100 * level ** 1.5)

def addXP(userID, value):
    sessionLevelData[userID]["xp"] += value
    
async def checkIfLevelUp(message):
    currXP = sessionLevelData[message.author.id]["xp"]
    XPToNextLevel = getXPToNextLevel(sessionLevelData[message.author.id]["level"])
    if currXP >= XPToNextLevel:
        overflow = currXP - XPToNextLevel
        sessionLevelData[message.author.id]["xp"] = overflow
        sessionLevelData[message.author.id]["level"] += 1
        await message.channel.send(f"{message.author.mention} leveled up! [{sessionLevelData[message.author.id]["level"]}]")

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.saveLevels.start()

    @app_commands.command(name="level", description="Check your level")
    async def getLevel(self, interaction: discord.Interaction):
        userData = sessionLevelData[interaction.user.id]
        if userData is None:
            await interaction.response.send_message("Please register your user using ```/register``` before checking your level.")
        else:
            level = userData["level"]
            xp = userData["xp"]
            await interaction.response.send_message(f"{interaction.user.mention}, you are level {level} [{getXPToNextLevel(level) - xp} XP to next level]")

    @tasks.loop(minutes=5)
    async def saveLevels(self):
        cursor = await self.bot.db.cursor()
        for entry, value in sessionLevelData.items():
            await cursor.execute("SELECT level, xp FROM users WHERE user_id = ?", (entry,))
            res = await cursor.fetchone()
            if res is not None:
                await cursor.execute("UPDATE users SET level = ?, xp = ? WHERE user_id = ?", (value["level"], value["xp"], entry))
        await self.bot.db.commit()
        await cursor.close()

    @saveLevels.before_loop
    async def waitForBot(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        addXP(message.author.id, len(message.content))
        await checkIfLevelUp(message)

        ctx = await self.bot.get_context(message)
        if ctx.valid:
            addXP(message.author.id, 50)

    @commands.Cog.listener()
    async def on_disconnect(self):
        self.saveLevels().close()
        await self.saveLevels()
        
async def setup(bot):
    await bot.add_cog(Levels(bot))

    await loadLevelData(bot)