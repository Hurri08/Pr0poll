import discord
from discord.ext import commands
import json
import csv

from utils.authHandler import AuthHandler
from utils.fileHandler import FileHandler
from utils.playerData import PlayerData


class Download(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot: commands.bot = bot
        self._FileHandler = FileHandler.instance()
        self._channels = {}

        self._setup()

    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<download,planetdata>",
                      brief="Lädt die aktuelle planetData Datei auf Discord hoch",
                      help="Lädt die aktuelle planetData Datei auf Discord hoch")
    async def Download(self, ctx: commands.context, *, fileName):
        fileName.lower()
        if fileName == "planetdata":
            file = self._FileHandler.getPlanetFile()
            with open(file) as json_file:
                jsondata = json.load(json_file)

            data_file = open(self._FileHandler.getPlanetDataCsv(), 'w', newline='')
            csv_writer = csv.writer(data_file)

            count = 0
            for data in jsondata:
                if count == 0:
                    header = data.keys()
                    csv_writer.writerow(header)
                    count += 1
                csv_writer.writerow(data.values())

            data_file.close()
            await ctx.send(file=discord.File(str(self._FileHandler.getPlanetDataCsv())))
#        elif fileName == "stats":
#            file = self._FileHandler.getStatsFile(fileName)
#            await ctx.send(file=discord.File(str(file)))
        else:
            await ctx.send("Dies ist kein gültiges Argument.")

    def _setup(self):
        self._channels = self._FileHandler.getUpdateChannels().data


def setup(bot: commands.Bot):
    bot.add_cog(Download(bot))