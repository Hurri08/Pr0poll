from discord.ext import commands
import logging
import csv
import json
import pandas as pd
from datetime import date
import requests

from utils.authHandler import AuthHandler
from utils.fileHandler import FileHandler
from utils.playerData import PlayerData


class Update(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot: commands.bot = bot
        self._PlayerData = PlayerData.instance()
        self._FileHandler = FileHandler.instance()
        self._channels = {}

        self._setup()

    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<update>",
                      brief="Lädt die stats.json vom pr0game herunter",
                      help="Lädt die stats.json vom pr0game herunter und verarbeitet diese entsprechend")
    async def update(self, ctx: commands.context):
        logging.info("FileHandler: Start Updating from stats-page ...")

        logging.info("Updating vom pr0game")
        await ctx.send("Start updating from pr0game.com/stats.json")
        json_url = requests.get("https://pr0game.com/stats.json")
        self._FileHandler.setLastUpdate()
        df = pd.read_json(json_url.text)
        df.to_csv(self._FileHandler.getStatsCsv(), index=None)

        myData = {}

        try:
            with open(self._FileHandler.getStatsCsv(), newline='', encoding='utf-8') as inFile, open(self._FileHandler.getCurrentFileNameCsv(), 'w', newline='', encoding='utf-8') as outFile:
                r = csv.reader(inFile)
                w = csv.writer(outFile)

                next(r, None)
                w.writerow(['playerId', 'username', 'playerGalaxy', 'allianceId', 'allianz', 'platz', 'gesamt', 'researchRank', 'forschung', 'buildingRank', 'gebäude', 'defensiveRank', 'defensive', 'fleetRank', 'flotte', 'battlesWon', 'battlesLost', 'battlesDraw', 'debris Metal', 'debrisCrystal', 'untisDestroyed', 'unitsLost'])
                for row in r:
                    w.writerow(row)

            with open(self._FileHandler.getCurrentFileNameCsv(), encoding='utf-8') as csvf:
                csvReader = csv.DictReader(csvf)

                for rows in csvReader:
                    key = rows['username']
                    myData[key] = rows

            with open(self._FileHandler.getCurrentFileName(), 'w', encoding='utf-8') as jsonf:
                def recursion_lower(x):
                    if type(x) is str:
                        return x.lower()
                    elif type(x) is list:
                        return [recursion_lower(i) for i in x]
                    elif type(x) is dict:
                        return {recursion_lower(k): recursion_lower(v) for k, v in x.items()}
                    else:
                        return x

                new_data = recursion_lower(myData)
                jsonf.write(json.dumps(new_data, indent=4))

            #self._FileHandler.writeFile(self._FileHandler.getCurrentFileName(), myData.data)
            self._PlayerData.updateData()
            self._FileHandler.getHistoryData()
            await ctx.send("Finished updating data")

        except:
            logging.error("FileHandler: Something went wrong with the stats")


    def _setup(self):
        self._channels = self._FileHandler.getUpdateChannels().data


def setup(bot: commands.Bot):
    bot.add_cog(Update(bot))
