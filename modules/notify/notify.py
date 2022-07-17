from discord.ext import commands
import logging

from utils.authHandler import AuthHandler
from utils.fileHandler import FileHandler
from utils.playerData import PlayerData

class Notify(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot: commands.bot = bot
        self._PlayerData = PlayerData.instance()
        self._PlayerData.setUpdateCallback(self.sendUpdates)
        self._FileHandler = FileHandler.instance()
        self._channels = {}

        self._setup()
    
    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<channelId>",
                      brief="Fügt channel zu Updatenachrichten hinzu",
                      help="Fügt channel mit der id <channelId> zu Updatenachrichten hinzu")
    async def addUpdate(self, ctx: commands.context, channelID: int):
        if channelID in self._channels["data"]:
            await ctx.send(returnMsg)
            return

        self._channels["data"].append(channelID)
        if self._FileHandler.setUpdateChannels(self._channels):
            returnMsg = "Channel hinzugefügt"
        else:
            returnMsg = "Fehler beim Channel hinzufügen"
        

        await ctx.send(returnMsg)
    
    @addUpdate.error
    async def addUpdate_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Fehlende Argumente!\nBsp.: !addUpdate 123456789')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')
    
    async def sendUpdates(self, msg):
        if self._channels:
            for channelId in self._channels["data"]:
                try:
                    channel = self.bot.get_channel(channelId)
                    await channel.send(msg)
                except:
                    logging.error("Notify: Failed to send Update Channel")

    def _setup(self):
        self._channels = self._FileHandler.getUpdateChannels().data



def setup(bot: commands.Bot):
    bot.add_cog(Notify(bot))
