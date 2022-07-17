import logging
from discord.ext import commands
from quickchart import QuickChart
import math

from utils.playerData import PlayerData
from utils.authHandler import AuthHandler


class Stats(commands.Cog):
    def __init__(self, bot: commands.bot):
        self._bot: commands.bot = bot
        self._PlayerData: PlayerData = PlayerData.instance()
        self._fields = ["platz", "username", "allianz", "gesamt", "flotte", "defensive", "gebäude", "forschung"]
        self._userData: dict = {}
        self._historyData: dict = {}
        
        self.setup()

    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<username>",
                      brief="Zeigt die Werte des Spielers an",
                      help="Zeigt die Werte des Spielers <username> an")
    async def stats(self, ctx: commands.context, *, username):
        username = username.lower()
        await ctx.send(self._getStatsString(username))

    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<username>",
                      brief="Zeigt die History des Spielers an",
                      help="Zeigt die History der letzen 7 Tage des Spielers <username> an")
    async def history(self, ctx: commands.context, *,username):
        username = username.lower()
        await ctx.send(self._getHistoryString(username))

    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<username>,[size]",
                      brief="Zeigt ein Diagramm an",
                      help="Zeigt ein Diagramm für den User <username> an. Die Größe wird über den optionalen " +
                           "parameter [size] angepasst. Mögliche Größen sind: S, M, L, XL (default: M)")
    async def chart(self, ctx: commands.context, *,argumente):
        argumente = argumente.lower()
        if "," in argumente:
            username = argumente.split(',')[0]
            size = argumente.split(',')[1]
        else:
            username = argumente.split(',')[0]
            size = 'm'
        
        if not username in self._historyData:
            return "Nutzer nicht gefunden"

        chartData = self._setupChartData(self._historyData[username])
       
        await ctx.send(self._getChartURL(chartData, size))

    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<galaxy>",
                      brief="Zeigt potentiell inaktive Spieler an",
                      help="Zeigt alle Spieler in Galaxie <galaxy> an, die potentiell inaktiv "+
                           "sind. (min. 3 tage kein Punktewachstum). Spieler im Urlaubsmodus " +
                           "werden leider mit aufgelistet")
    async def inactive(self, ctx: commands.context, galaxy: int):
        if galaxy <1 or galaxy>9:
            return ctx.send("Galaxie muss zwischen 1 und 9 sein")

        inactivePlayers = self._getLoosingPointsPlayer(galaxy)
        sortedInactivePlayerPlanets = self._getFilteredAndSortedInactivePlayerPlanets(inactivePlayers, galaxy)
        resultStr = ""
        for user,systems in sortedInactivePlayerPlanets:
            resultStr += "{:<20}".format(user)
            for system in systems:
                resultStr += "{:<4}".format(system)
            resultStr += "\n"
        if len(resultStr) > 1994:
            n = 1994
            x = 0
            resultStr = [resultStr[i:i+n] for i in range(0, len(resultStr), n)]
            for lists in resultStr:
                await ctx.send("```" + lists + "```")
                x += 1
        else:
            await ctx.send("```" + resultStr + "```")

    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<galaxy>",
                      brief="Zeigt die Namen von potentiell inaktiven Spielern an",
                      help="Zeigt alle Spielernamen in Galaxie <galaxy> and, die potentiell Inaktiv "+
                           "sind. (min. 3 tage kein Punktewachstum). Spieler im Urlaubsmodus " +
                           "werden leider mit aufgelistet")
    async def iname(self, ctx: commands.context, galaxy: int):
        if galaxy <1 or galaxy>9:
            return ctx.send("Galaxie muss zwischen 1 und 9 sein")

        inactivePlayers = self._getLoosingPointsPlayer(galaxy)

        resultStr = "```"
        for user in inactivePlayers:
            resultStr += "{:<20}".format(user)
            resultStr += "\n"
        if len(resultStr) > 1997:
            n = 1997
            resultStr = [resultStr[i:i+n] for i in range(0, len(resultStr), n)]
            resultStr[0] += "```"
            resultStr[1] += "```"
            await ctx.send(resultStr[0])
            await ctx.send("```" + resultStr[1])
        else:
            await ctx.send(resultStr + "```")

    @stats.error
    async def stats_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Spielername fehlt!\nBsp.: !stats Sc0t')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine Rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')

    @iname.error
    async def stats_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Spielername fehlt!\nBsp.: !inactive 3')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine Rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')
    
    @history.error
    async def history_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Spielername fehlt!\nBsp.: !history Sc0t')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine Rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')
    
    @chart.error
    async def chart_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Spielername fehlt!\nBsp.: !chart Sc0t')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine Rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')

    @inactive.error
    async def inactive_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Galaxy fehlt!\nBsp.: !inactive 1')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine Rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')

    def setup(self):
        logging.info("Stats: Get Data references")
        self._userData = self._PlayerData.getUserDataReference(self.updateUserDataCallback)
        self._historyData = self._PlayerData.getHistoryDataReference(self.updateHistoryDataCallback)

    def updateUserDataCallback(self):
        logging.info("Stats: Update UserData references")
        self._userData = self._PlayerData.getUserDataReference()
    
    def updateHistoryDataCallback(self):
        logging.info("Stats: Update HistoryData references")
        self._historyData = self._PlayerData.getHistoryDataReference()

    def _getFilteredAndSortedInactivePlayerPlanets(self, inactivePlayers: dict, galaxy):
        filteredPlayerPlanets: dict = {}

        #filter inactive players
        for user in inactivePlayers:
            if "planets" in self._userData[user]:
                if(inactivePlayers[user] >=3) and "planets" in self._userData[user]: #3 = threshold for amount of datapoints of loosing points
                    filteredPlayerPlanets[user] = []
                    for planet in self._userData[user]["planets"]:
                        planetGalaxy = int(planet.split(":")[0])
                        planetSystem = int(planet.split(":")[1])
                        if(galaxy == planetGalaxy and not planetSystem in filteredPlayerPlanets[user]):
                            filteredPlayerPlanets[user].append(planetSystem)
            else:
                pass

        #sort
        sortedPlayerPlanets = []
        for user in filteredPlayerPlanets:
            sortedPlayerPlanets.append((user,filteredPlayerPlanets[user]))
        sortedPlayerPlanets.sort(key=lambda x: x[1][0])
        return sortedPlayerPlanets

    def _getLoosingPointsPlayer(self, galaxy: int):
        inactiveData: dict = {}
        for user in self._historyData:
            historyData = self._historyData[user]
            last = historyData[0]
            for current in historyData[1:]:
                lastPoints = int(last["gesamt"].replace(".",""))
                currentPoints = int(current["gesamt"].replace(".",""))
                cUsername = current["username"]
                if lastPoints >= currentPoints:
                    if cUsername in self._userData and "planets" in self._userData[cUsername]:
                        for planet in self._userData[cUsername]["planets"]:
                            if int(planet.split(":")[0]) == galaxy:
                                if cUsername in inactiveData:
                                    inactiveData[cUsername] += 1
                                    break
                                else:
                                    inactiveData[cUsername] = 1
                                    break
                else:
                    inactiveData.pop(user, None)
                last = current
        return inactiveData

    def _getChartURL(self, chartData: dict, size: str):
        qc = QuickChart()

        if size == 's':
                qc.width = 500
                qc.height = 300
        elif size == 'm':
                qc.width = 720
                qc.height = 480
        elif size == 'l':
                qc.width = 1280
                qc.height = 720
        elif size == 'xl':
                qc.width = 1980
                qc.height = 1080
        else: #m
                qc.width = 720
                qc.height = 480
           
        qc.device_pixel_ratio = 2.0
        qc.config = {
            "type": "line",
            "data": {
                "labels": chartData["labels"],
                "datasets": [{
                    "yAxisID": "rankAxis",
                    "label": "Platz",
                    "data": chartData["platz"],
                    "fill": False,
                },{
                    "yAxisID": "pointAxis",
                    "label": "Gesamtpunkte",
                    "data": chartData["gesamt"],
                    "fill": False,
                },{
                    "yAxisID": "pointAxis",
                    "label": "Gebäude",
                    "data": chartData["gebäude"],
                    "fill": False,
                },{
                    "yAxisID": "pointAxis",
                    "label": "Forschung",
                    "data": chartData["forschung"],
                    "fill": False,
                },{
                    "yAxisID": "pointAxis",
                    "label": "Flotte",
                    "data": chartData["flotte"],
                    "fill": False,
                },{
                    "yAxisID": "pointAxis",
                    "label": "Defensive",
                    "data": chartData["defensive"],
                    "fill": False,
                }]
            },
            "options": {
                "scales": {
                "xAxes": [{
                    "stacked": True
                }],
                "yAxes": [{
                    "id": "rankAxis",
                    "display": True,
                    "position": "left",
                    "stacked": True,
                    },{
                    "id": "pointAxis",
                    "display": True,
                    "position": "right",
                    "gridLines": {
                        "drawOnChartArea": False
                    },
                    "ticks": {
                        "beginAtZero": True}
                    }]
                }
            }
        }
        return qc.get_short_url()

    def _setupChartData(self, historyData: dict):
        chartData= {
            "labels": [],
            "gesamt": [],
            "platz": [],
            "flotte": [],
            "gebäude": [],
            "defensive": [],
            "forschung": []
        }

        for day in historyData:
            chartData["labels"].append(day["timestamp"].rsplit("_",1)[0].replace("_","."))
            chartData["gesamt"].append(day["gesamt"].replace(".",""))
            chartData["platz"].append(day["platz"])
            chartData["flotte"].append(day["flotte"].replace(".",""))
            chartData["gebäude"].append(day["gebäude"].replace(".",""))
            chartData["defensive"].append(day["defensive"].replace(".",""))
            chartData["forschung"].append(day["forschung"].replace(".",""))

        return chartData

    def _getHistoryString(self, username):
        if not username in self._historyData:
            return "Nutzer nicht gefunden"
        
        #only use last 7 entrys
        data = self._historyData[username][-7:]

        returnMsg = f"```Spieler {username}\n\n"
        returnMsg +="{0:7} {1:5} {2:10} {3:10} {4:10}\n".format("Datum", "P.", "Gesamt", "Flotte", "Gebäude")
        for entry in data:
            returnMsg += "{0:7} {1:5} {2:10} {3:10} {4:10}\n".format(entry["timestamp"].rsplit("_",1)[0].replace("_","."), str(entry["platz"]),
                                                                     entry["gesamt"] ,entry["flotte"], entry["gebäude"])
        returnMsg += "{0:7} {1:5} {2:10} {3:10} {4:10}\n".format("Diff.", 
                                                                 self._userData[username]["diff_platz"],
                                                                 self._userData[username]["diff_gesamt"],
                                                                 self._userData[username]["diff_flotte"],
                                                                 self._userData[username]["diff_gebäude"])
        return returnMsg + "```"

    def _getStatsString(self, username):
        if not username in self._userData:
            return "Nutzer nicht gefunden"
        userData = self._userData[username]

        returnMsg = "```"
        for field in self._fields:
            if f"diff_{field}" in userData:
                returnMsg += "{0:30}{1:10} ({2})\n".format(field.capitalize(),str(userData[field]), userData["diff_" +field])
            elif userData[field] == "sc0t":
                returnMsg += "{0:30}{1:10} {2}\n".format(field.capitalize(),userData[field], "<- Bot-Vater")
            elif userData[field] == "oconna":
                returnMsg += "{0:30}{1:10} {2}\n".format(field.capitalize(),userData[field], "<- Alli-Führer")
            elif userData[field] == "nuxc":
                returnMsg += "{0:30}{1:10} {2}\n".format(field.capitalize(),userData[field], "<- Wing-Führer")
            else:
                returnMsg += "{0:30}{1}\n".format(field.capitalize(),userData[field])
        
        #addPlanetData
        returnMsg += "\n{0:30}\n".format("Bekannte Planeten")
        returnMsg += "{0:7} Mond?".format("Pos.")
        returnMsg += "{0:1} Phalanx Level".format("")
        returnMsg += "{0:1} Phalanx Reichweite\n".format("")

        if "planets" in userData:
            for planetPos in sorted(userData["planets"]):
                if userData["planets"][planetPos]["moon"]:
                    returnMsg += "{:7}  \u2713".format(planetPos)
                    if userData["planets"][planetPos]["phalanx"] != "":
                        system = planetPos.split(":")
                        reach = math.pow(int(userData["planets"][planetPos]['phalanx']), 2) - 1
                        reachMin = int(system[1]) - int(reach)
                        reachMax = int(system[1]) + int(reach)
                        returnMsg += f"       {userData['planets'][planetPos]['phalanx'].format('')}" + \
                                     f"             {reachMin} - {reachMax}" + "\n"
                    else:
                        returnMsg += "\n"
                else:
                    returnMsg += "{:7}\n".format(planetPos)
        
            return returnMsg + "```"
        else:
            return returnMsg + "```"

def setup(bot: commands.Bot):
    bot.add_cog(Stats(bot))
