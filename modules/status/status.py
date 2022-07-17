import logging

from discord.ext import commands
from utils.fileHandler import FileHandler
from utils.authHandler import AuthHandler

class Status(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.FileHandler = FileHandler.instance()
        self.lastUpdate = "N/A"
    
    @commands.check(AuthHandler.instance().check)
    @commands.command()
    async def test(self, ctx: commands.context):
        """Antwortet mit \"Test Bestanden\" (Verbindungstest)"""
        await ctx.send('Test bestanden')

    @commands.check(AuthHandler.instance().check)
    @commands.command()
    async def status(self, ctx: commands.context):
        """Stand des Datensatzes"""
        await ctx.send(f"Letztes Update: {self.FileHandler.getLastUpdate()}")

    @test.error
    async def test_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Keine rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')
    
    @status.error
    async def status_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Keine rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')
    


def setup(bot: commands.Bot):
    bot.add_cog(Status(bot))
