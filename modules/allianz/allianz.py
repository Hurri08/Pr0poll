import logging
import inspect
from discord.ext import commands

from utils.playerData import PlayerData
from utils.authHandler import AuthHandler

class Allianz(commands.Cog):
    def __init__(self, bot: commands.bot):
        self._bot: commands.bot = bot
        self._PlayerData: PlayerData = PlayerData.instance()
        self._allianzData: dict = {}
        self._topAllianzData: dict = {}

        self.setup()
    
    @commands.check(AuthHandler.instance().check)
    @commands.command()
    async def allianz(self, ctx: commands.context, *,allianzName):
        """Zeigt die Top 15 Spieler der Allianz <allianzname> an"""
        allianzName = allianzName.lower()

        if not allianzName in self._allianzData:
            await ctx.send('Allianzname nicht gefunden')
            return

        await ctx.send(self._getAllianzString(allianzName))

    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<allianzname>,<galaxy>",
                      brief="Zeigt alle Planeten der Allianz in einer Galaxy an",
                      help="Zeigt alle Planeten der Allianz <allianzname> in einer Galaxy <galaxy> an.")
    async def allianzPosition(self, ctx: commands.context, *,argumente):
        argumente = argumente.lower()
        if "," in argumente:
            allianzName = argumente.split(',')[0]
            galaxy = argumente.split(',')[1]
        else:
            raise commands.MissingRequiredArgument(param=inspect.Parameter("galaxy",inspect._ParameterKind.VAR_POSITIONAL))
        
        if not allianzName in self._allianzData:
            await ctx.send('Allianzname nicht gefunden')
            return
        

        await ctx.send(self._getAllianzPosString(allianzName, galaxy))

    @allianz.error
    async def allianz_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Allianzname fehlt!\nBsp.: !allianz Allianz mit Poll')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')
    
    @allianzPosition.error
    async def allianzPosition_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Fehlende Argumente!\nBsp.: !allianzPosition Allianz mit Poll,3')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')

    def setup(self):
        logging.info("Allianz: Get Data references")
        self._allianzData = self._PlayerData.getAllianzDataReference(self.updateCallback)
        self._topAllianzData = self._getAllTopAllianzMembers(self._allianzData)

    def updateCallback(self):
        logging.info("Allianz: Updated Data references")
        self._allianzData = self._PlayerData.getAllianzDataReference()
        self._topAllianzData = self._getAllTopAllianzMembers(self._allianzData)

    def _getAllTopAllianzMembers(self, fullAllianzData: dict):
        topAllianzUsers = {}
        for allianzName in fullAllianzData:
            allianzUsers: list = fullAllianzData[allianzName]
            
            #sort users by rank and keep only top 10
            topAllianzUsers[allianzName] = sorted(allianzUsers,key=lambda d: int(d['platz']))[:15]
        
        return topAllianzUsers

    def _getAllianzPosString(self, allianzName, galaxy):
        allianzPlanetsinGalaxy = self._getAllAllianzPlanetsInGalaxy(allianzName, galaxy)
        sortedPlanets = self._getSortedPlanets(allianzPlanetsinGalaxy)
        return self._getStringFromPlanets(sortedPlanets, galaxy)
    
    def _getStringFromPlanets(self, planets: list, gal: str):
        if len(planets) == 0:
            return f"``` Keine bekannte Planeten in galaxy {gal} ```"
        
        returnStr = "```"
        for idx,pos in enumerate(planets):
            if (idx%5==0):
                returnStr += "\n"
            returnStr += "{:10}".format(gal + ":" + str(pos[0]) + ":" + str(pos[1]))

        return returnStr + "```"

    def _getSortedPlanets(self, planets):
        sortedPlanets = []
        for planet in planets:
            splitted = planet.split(':')
            system = int(splitted[1])
            pos =int(splitted[2])
            sortedPlanets.append((system,pos))
        #sort by system then pos
        sortedPlanets.sort(key=lambda element: (element[0],element[1]))
        return sortedPlanets

    def _getAllAllianzPlanetsInGalaxy(self, allianzName, galaxy):
        result = []
        for user in self._allianzData[allianzName]:
            if "planets" in user:
                for planet in user["planets"]:
                    if planet.split(":")[0] == galaxy:
                        result.append(planet)
            else:
                pass
        return result

    def _getAllianzString(self, allianzName):
        returnMsg = f"```Top 15 von Allianz {allianzName}\n"
        returnMsg +="{:1} {:4} {:20} {:<10} {:10} \n\n".format("","Platz","Name", "Punkte", "Flotte")

        for userData in self._topAllianzData[allianzName]:           
            arrow = "-" #equal
            try:
                diff = int(userData["diff_platz"])
            except:
                arrow = "" # no history data
            
            if diff > 0:
                arrow = "\u2193" #down
            elif diff < 0:
                arrow = "\u2191" #up
            
            returnMsg +="{:1} {:4} {:20} {:<10} {:10}\n".format(arrow,
                                                                userData["platz"],
                                                                userData["username"],
                                                                userData["gesamt"],
                                                                userData["flotte"])
        return returnMsg + "```"

def setup(bot: commands.Bot):
    bot.add_cog(Allianz(bot))
