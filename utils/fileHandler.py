import os
import json
import logging
import pandas as pd
from datetime import *
#from bs4 import BeautifulSoup
from dotenv import load_dotenv

from utils.singleton import Singleton
from utils.myData import MyData

@Singleton
class FileHandler:
    def __init__(self):
        load_dotenv()
        logging.info("FileHandler created")
        self._path = "files/"
        self._fileEnding = ".json"
        self._csvEnding = ".csv"
        self._currentData = MyData({})
        self._historyData = MyData({})
        self._planetData = MyData()
        self._authData = MyData()
        self._channelData = MyData()
        self._playerIdFile = self._path + "playerId" + self._fileEnding
        self._lastUpdate = "N/A"
        self._historyFileNames = self._path + "historyFileNames" + self._fileEnding
        self._planetDataFile = self._path + "planetData" + self._fileEnding
        self._authFile = self._path + "auth" + self._fileEnding
        self._channelFile = self._path + "channelIds" + self._fileEnding
        self._pointsFile = self._path + "points" + self._fileEnding
        self.currentDataFileCsv = self._path + date.today().strftime("%d_%m_%Y") + self._csvEnding
        self._statsFile = self._path + "stats" + self._csvEnding

    def getCurrentData(self):
        currentFileName = self.getCurrentFileName()

        if os.path.exists(currentFileName):
            self._currentData: MyData = self._readFile(currentFileName)
        else:
            pass
        return self._currentData

    def setLastUpdate(self):
        now = datetime.now()
        self._lastUpdate = now.strftime("%d/%m/%Y um %H:%M")

    def getHistoryData(self):
        historyFileNames: MyData = self._readFile(self._historyFileNames)

        try:
            if historyFileNames.valid:
                if not date.today().strftime("%d_%m_%Y") in historyFileNames.data["filenames"]:
                    historyFileNames.data["filenames"].append(date.today().strftime("%d_%m_%Y"))
                    self.writeFile(self._historyFileNames, historyFileNames.data)

                self._historyData.data = {}
                for file in historyFileNames.data["filenames"]:
                    day = self._readFile(self._path + file + self._fileEnding)
                    if day.valid:
                        for userName in day.data:
                            day.data[userName]["timestamp"] = file
                            if userName in self._historyData.data:
                                self._historyData.data[userName].append(day.data[userName])
                            else:
                                self._historyData.data[userName] = [day.data[userName]]
            self._historyData.valid = True
        except:
            self._historyData.valid = False
            logging.error("FileHandler: Failed to read/parse History Files")
       
        return self._historyData

    def getLastUpdate(self):
        return self._lastUpdate

    def getPointsFile(self):
        return self._pointsFile

    def getPlanetData(self):
        planetData: MyData = self._readFile(self._planetDataFile)

        if planetData.valid:
            self._planetData = planetData
        
        return self._planetData

    def setPlanetData(self, data: dict):
        self._planetData = data
        return self.writeFile(self._planetDataFile, data)

    def getAuthData(self):
        authData: MyData = self._readFile(self._authFile)

        if authData.valid:
            self._authData = authData
        
        return self._authData

    def setAuthData(self, data):
        self._authData = data
        return self.writeFile(self._authFile, data)

    def getUpdateChannels(self):
        channelData: MyData = self._readFile(self._channelFile)

        if channelData.valid:
            self._channelData = channelData
        
        return self._channelData

    def setUpdateChannels(self, data):
        self._channelData = data
        return self.writeFile(self._channelFile, data)

    def getCurrentFileName(self):
        today = date.today()
        return self._path + today.strftime("%d_%m_%Y") + self._fileEnding

    def getCurrentFileNameCsv(self):
        today = date.today()
        return self._path + today.strftime("%d_%m_%Y") + self._csvEnding

    def getStatsCsv(self):
        return self._statsFile

    def _readFile(self, filePath):
        myData = MyData()

        try:
            with open(filePath, encoding='utf-8' ) as file:
                myData.data = json.load(file)
                myData.valid = True
        except:
            myData.valid = False
            logging.error(f"FileHandler: Failed to open file {filePath}")
        
        return myData

    def writeFile(self, filePath: str, data: dict):
        logging.info(f"FileHandler: Saving data to file {filePath}")
        try:
            with open(filePath, 'w') as file:
                file.write(json.dumps(data, indent=2))
        except:
            logging.error(f"FileHandler: Failed to save data to file: {filePath}")
            return False
        return True

    #def parsePlayerCards(self, session, playerPosAndId):
    #    data = {}
    #    idx = 0
    #    for pos,id in playerPosAndId:
    #        if int(idx)%100 == 0:
    #             logging.info(f"FileHandler: Parsing Playercard {idx+1} of {100* self._sitesToParse}")
    #        idx += 1

    #        url = 'https://pr0game.com/game.php?page=playerCard&id=1000]https://pr0game.com/game.php?page=playerCard&id={}'.format(str(id))
    #        r = session.get(url)
    #        soup = BeautifulSoup(r.text, "html.parser")

    #        table = soup.find('table')
    #        name = str(table.findChildren("tr" , recursive=False)[1].findChildren("td" , recursive=False)[1]).split(">")[1].split("<")[0].strip().lower()
    #        data[name] = { "platz": pos}
    #        data[name]["planets"] = []
            
    #        for tr in table.findChildren("tr" , recursive=False)[1:10]:
    #            try:
    #                tds = tr.findChildren("td" , recursive=False)
    #                keyName = str(tds[0]).split(">")[1].split("<")[0].strip().lower()
    #                value = str(tds[1]).split(">")[1].split("<")[0].strip().lower()

    #                if(keyName == "heimatplanet"):
    #                    value = str(tds[1]).split(">")[2].split("<")[0]

    #                if(keyName == "allianz"):
    #                    value = str(tds[1]).split(">")[2].split("<")[0]

    #                if(keyName):
    #                    data[name][keyName] = value
    #            except:
    #                pass
    #    return data

    #def parseStatisticSite(self, session):
    #    playerPosAndId = []
    #    playerPos = 1

    #    for site in range(0, self._sitesToParse):
    #        logging.info(f"FileHandler: Site {site+1} of {self._sitesToParse} ...")
    #        payload = {
    #            "who": 1,
    #            "type" : "1",
    #            "range": "{}01".format(site)
    #        }
    #        r = session.post("https://pr0game.com/game.php?page=statistics", data=payload)
    #        soup = BeautifulSoup(r.text, "html.parser")

    #        table = soup.find_all("table",{"class":"table519"})[1]
    #        for tr in table.findChildren("tr" , recursive=False)[1:]:
    #            td = tr.findChildren("td" , recursive=False)[1]
    #            id = str(td).split('(')[1].split(',')[0]
    #            playerPosAndId.append((playerPos,id))
    #            playerPos+=1
            
    #    return playerPosAndId

    #def login(self,session):
    #    logging.info("FileHandler: Logging in ...")
    #
    #    payload = {
    #        "uni": 1,
    #        "username" : os.getenv("PLAYERNAME"),
    #        "password": os.getenv("PASSWORD")
    #    }
    #    session.post('https://pr0game.com/index.php?page=login', data=payload)
