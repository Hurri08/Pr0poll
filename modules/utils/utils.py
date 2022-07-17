from discord.ext import commands
import re
import os
import logging
from dotenv import load_dotenv

from utils.fileHandler import FileHandler
from utils.authHandler import AuthHandler

class Utils(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.FileHandler = FileHandler.instance()
        self.lastUpdate = "N/A"
    
    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<g>:<s>",
                      brief="Erzeugt ein Link auf die Position",
                      help="Erzeugt ein Link der die Position <g>:<s> in der Galaxyansicht führt")
    async def link(self, ctx: commands.context, position: str):
        position = position.lower()
        try:
            result = re.search("^(\d):(\d{1,3})$",position)
            galaxy = result.group(1)
            system = result.group(2)
        except:
            await ctx.send('Position konnte nicht geparst werden\nz.B.: !link 1:1')
            return
        
        await ctx.send(f'https://pr0game.com/game.php?page=galaxy&galaxy={galaxy}&system={system}')

    @commands.check(AuthHandler.instance().check)
    @commands.command(brief="Zeigt eine NICHT geordnete liste der geplanten updates",
                      help="Zeigt eine NICHT geordnete liste der geplanten updates.")
    async def features(self, ctx: commands.context):
        featureList: list = [
            "```"
            "Monde:",
            "   - Speichern von sensor Phalanx lvl",
            "       - Überprüfen ob man in Reichweite ist",
            "Wachstum:",
            "   - prozentualer wachstum wie unnamed statisik anzeigen",
            "     als Listenform und auf einzelne Spieler",
            "Differenz:",
            "   - Spieler miteinander vergleichen",
            "     als Chart und gegenüberstellung wie !stats",
            "   - Vll auch rel. Startpunkt einstellbar. Aka",
            "     Start ist bei beiden Spieler bei 5k",
            "Points:",
            "   - Reimplementieren",
            "Usernamen:",
            "   - Usernamen mit Hauptlaneten speichern, sodass",
            "     bei namensänderungen weiterhin der gleiche Spieler",
            "     getrackt wird",
            "```"
        ]
        await ctx.send("\n".join(featureList))
   
    @link.error
    async def link_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Fehlendes Argument!\nBsp.: !link 1:1')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')
    
    @features.error
    async def features_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Keine rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')

    
    @commands.Cog.listener(name='on_command')
    async def log(self, ctx):
        if ctx.guild:
            server = str(ctx.guild.name)
        else:
            server = "private"
        user = str(ctx.author)
        command = str(ctx.command)
        args = " ".join(str(x) for x in ctx.kwargs.values())

        logChannel = self.bot.get_channel(int(os.getenv("LOGCHANNEL")))
        
        returnStr = "```{},{},{},{}```".format(server,user,command,args)
        await logChannel.send(returnStr)

def setup(bot: commands.Bot):
    bot.add_cog(Utils(bot))
