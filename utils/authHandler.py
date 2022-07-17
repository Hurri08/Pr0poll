from discord.ext import commands
import logging

from utils.singleton import Singleton
from utils.fileHandler import FileHandler
from utils.myData import MyData

@ Singleton


class AuthHandler:
    def __init__(self):
        self._fileHandler: FileHandler = FileHandler.instance()
        self._authData: dict = {}
        self._bot: commands.bot = None
        self._groups: list = []

        self._setup()

    def addBot(self, bot: commands.bot):
        self._bot = bot

    def check(self, ctx):
        author = str(ctx.author).lower()
        # author = "n0sleep#9106"
        command = str(ctx.command).lower()

        # check for groups
        for group in self._authData["group"]:
            groupData = self._authData["group"][group]
            if author in groupData["user"]:
                if command in groupData["commands"] or '*' in groupData["commands"]:
                    return True

        # check for single User auth
        if author in self._authData["user"]:
            if command in self._authData["user"][author]["commands"]:
                return True

        return False

    def add(self, user: str, field: str):
        commandNames = [c.name.lower() for c in self._bot.commands]

        if field in self._groups:
            self._authData["group"][field]["user"].append(user)
        elif field in commandNames:
            if user in self._authData["user"]:
                if not field in self._authData["user"][user]["commands"]:
                    self._authData["user"][user]["commands"].append(field)
            else:
                self._authData["user"][user] = {"commands": [field]}
        else:
            return False

        return self._fileHandler.setAuthData(self._authData)

    def remove(self, user: str, field: str):
        commandNames = [c.name.lower() for c in self._bot.commands]

        if field in self._groups:
            if user in self._authData["group"][field]["user"]:
                self._authData["group"][field]["user"].remove(user)
        elif field in commandNames:
            if user in self._authData["user"]:
                if field in self._authData["user"][user]["commands"]:
                    self._authData["user"][user]["commands"].remove(field)
                else:
                    # field not in commands
                    return False
            else:
                # no user field
                return False
        else:
            # command not in command List
            return False

        return self._fileHandler.setAuthData(self._authData)

    def _setup(self):
        myData: MyData = self._fileHandler.getAuthData()
        if (myData.valid):
            self._authData = myData.data
            self._groups = list(self._authData["group"].keys())
        else:
            logging.warning("Auth: Invalid authData to update")

