from discord.ext import commands
from dotenv import load_dotenv
import os
import logging

from modules import *
from utils.authHandler import AuthHandler
from utils.playerData import PlayerData


def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    logging.info("Programm started")

    client = commands.Bot(command_prefix="+", case_insensitive=True)

    # Initialize Singeltons
    playerData = PlayerData.instance()
    autHandler = AuthHandler.instance()
    autHandler.addBot(client)

    for name in os.listdir(os.path.join(os.path.abspath(os.getcwd()), "modules")):
        if os.path.exists(os.path.join("modules", name)):
            client.load_extension(f"modules.{name}.{name}")
            logging.info(f"Bot: Module {name} loaded")

    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    main()