from discord.ext import commands
import logging
import json
import math
import inspect
import pandas as pd

from tabulate import tabulate
from utils.authHandler import AuthHandler
from utils.fileHandler import FileHandler


class Points(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot: commands.bot = bot
        self._FileHandler = FileHandler.instance()
        self._channels = {}
        self._fields = ["Metall", "Kristall", "Deuterium", "Punkte"]
        self._object: dict = {}
        self._setup()

    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<gebäude/forschung>,<level>",
                      brief="Zeigt die Punkte an, die ein erforschen/bauen dieses Levels eines Gebäude/ einer Forschung bringt",
                      help="Zeigt die Punkte an, die ein erforschen/bauen dieses Levels eines Gebäude/ einer Forschung bringt, für eine Liste der Forschungen Gebäude !abkürzungen eingeben")
    async def points(self, ctx: commands.context, *, argumente):
        argumente = argumente.lower()
        if "," in argumente:
            key = argumente.strip().split(',')[0]
            level = argumente.strip().split(',')[1]
            with open(self._FileHandler.getPointsFile(), "r") as read_json:
                object = json.load(read_json)
                met = object[key]["met"]
                kris = object[key]["kris"]
                deut = object[key]["deut"]
                met = met.replace("X", level)
                kris = kris.replace("X", level)
                deut = deut.replace("X", level)
                resultMet = float(eval(met))
                resultKris = float(eval(kris))
                resultDeut = float(eval(deut))
                punkte = resultMet / 1000 + resultKris / 1000 + resultDeut / 1000
                #await ctx.send("Das Gebäude kosts " + str(float(resultMet)) + " Metall, " + str(float(resultKris)) + " Kristall und " + str(float(resultDeut)) + " Deuterium und gibt " + str(float(punkte)) + " Punkte!")
                #await ctx.send(result)
                noDecimalResultMet = '{:.0f}'.format(float(resultMet))
                noDecimalResultKris = '{:.0f}'.format(float(resultKris))
                noDecimalResultDeut = '{:.0f}'.format(float(resultDeut))
                noDecimalResultPunkte = '{:.0f}'.format(float(punkte))
                formatResultMet = '{:,}'.format(float(noDecimalResultMet)).replace(',', '.')
                formatResultKris = '{:,}'.format(float(noDecimalResultKris)).replace(',', '.')
                formatResultDeut = '{:,}'.format(float(noDecimalResultDeut)).replace(',', '.')
                formatResultPunkte = '{:,}'.format(float(noDecimalResultPunkte)).replace(',', '.')
                returnMsg = "```"
                results = [[str(formatResultMet), str(formatResultKris[:-2]), str(formatResultDeut[:-2]), str(formatResultPunkte[:-2])]]
                col_names = ["Metall", "Kristall", "Deuterium", "Punkte"]
                returnMsg += tabulate(results, headers=col_names, tablefmt="plain")
                returnMsg += "```"
                await ctx.send(returnMsg)


        else:
            raise commands.MissingRequiredArgument(param=inspect.Parameter("username",inspect._ParameterKind.VAR_POSITIONAL))

    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<abkuerzungen>",
                      brief="Zeigt die Abkürzungen für den Befehl !points an",
                      help="Zeigt die Abkürzungen für den Befehl !points an")
    async def abkuerzungen(self, ctx: commands.context):
        with open(self._FileHandler.getPointsFile(), "r") as read_json:
            object = json.load(read_json)
            vollKeys = []
            vollNames = []
            col_names = ["Befehl", "Voller Name"]
            for key, val in object.items():
                if isinstance(val, dict):
                    vollNames += [val.get('voll')]

            for key in object.keys():
                vollKeys += [key]
            returnMsg = "```"
            combined = zip(vollKeys, vollNames)
            returnMsg += tabulate(combined, headers=col_names)
        returnMsg += "```"
        await ctx.send(returnMsg)


    @points.error
    async def history_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Fehelende Argumente! z.B !points met,12')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')

    def _setup(self):
        self._channels = self._FileHandler.getUpdateChannels().data


def setup(bot: commands.Bot):
    bot.add_cog(Points(bot))
