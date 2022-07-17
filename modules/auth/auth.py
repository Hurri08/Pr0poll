import logging
import inspect
from discord.ext import commands

from utils.authHandler import AuthHandler

class Authentication(commands.Cog):
    def __init__(self, bot: commands.bot):
        self._bot: commands.bot = bot
        self._auth = AuthHandler.instance()
    
    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<username>,<feld/gruppe>",
                      brief="Authorisiert Nutzer auf Befehle",
                      help="Authorisiert Nutzer <username> auf eine Gruppe oder einzelnen Befehl <field/gruppe>")
    async def auth(self, ctx: commands.context, *,argumente):
        argumente = argumente.lower()
        if "," in argumente:
            username = argumente.split(',')[0]
            field = argumente.split(',')[1]
        else:
            raise commands.MissingRequiredArgument(param=inspect.Parameter("field",inspect._ParameterKind.VAR_POSITIONAL))
        
        if self._auth.add(username, field):
            returnMsg = "Erfolgreich Authorisiert"
        else:
            returnMsg = "Authorisiorung fehlgeschlagen"

        await ctx.send(returnMsg)

    @commands.check(AuthHandler.instance().check)
    @commands.command(usage="<username>,<feld/gruppe>",
                      brief="Deauthorisiert Nutzer auf Befehle",
                      help="Deauthorisiert Nutzer <username> auf eine Gruppe oder einzelnen Befehl <field/gruppe>")
    async def deauth(self, ctx: commands.context, *,argumente):
        argumente = argumente.lower()
        if "," in argumente:
            username = argumente.split(',')[0]
            field = argumente.split(',')[1]
        else:
            raise commands.MissingRequiredArgument(param=inspect.Parameter("field",inspect._ParameterKind.VAR_POSITIONAL))

        if self._auth.remove(username, field):
            returnMsg = "Erfolgreich Deauthorisiert"
        else:
            returnMsg = "Deauthorisiorung fehlgeschlagen"

        await ctx.send(returnMsg)

    @commands.check(AuthHandler.instance().check)
    @commands.command()
    async def ban(self, ctx: commands.context, *,username):
        """Deauthorisiert Nutzer auf den Bot"""
        username = username.lower()
       
        if self._auth.remove(username, "all"):
            returnMsg = "Bonk!"
        else:
            returnMsg = "Bonk hammer kaputt"

        await ctx.send(returnMsg)

    @auth.error
    async def auth_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Fehler in den Argumenten!\nBsp.: !auth Sc0t#123,boom')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')
    
    @deauth.error
    async def deauth_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Spielername fehlt!\nBsp.: !deauth Sc0t#123,boom')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')
    
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Spielername fehlt!\nBsp.: !ban Sc0t#123')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Keine rechte diesen Befehl zu nutzen')
        else:
            logging.error(error)
            await ctx.send('ZOMFG ¯\_(ツ)_/¯')

def setup(bot: commands.Bot):
    bot.add_cog(Authentication(bot))
