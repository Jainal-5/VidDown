from pathlib import Path
import os
from platform import platform

class FileManager():
    def getParentDirectory(self):
        currentDir = os.path.dirname(__file__)

        return os.path.split(currentDir)[0]

    def getDownloadPath(self):
        if "android" in platform():
            downloadPath = "/storage/emulated/0/Download/Anime/"
            if os.path.exists(downloadPath):
                return downloadPath
            else:
                print(f"Path {downloadPath} does'nt exists.")
                print(f"Creating Path.")

                self.makeDirectory(downloadPath)

                return self.getDownloadPath()
                
        else:
            return Path.home() / "Download"

    def getStateDirectory(self):
        stateDir = os.path.join(self.getParentDirectory(),"state")

        if os.path.exists(stateDir):
            return stateDir
        else:
            print(f"{stateDir} doesn't exists.")
            print(f"Creating {stateDir} .")
            self.makeDirectory(stateDir)

            return self.getStateDirectory()

    def makeDirectory(self, downloadPath):
        if not os.path.exists(downloadPath):
            os.makedirs(downloadPath, exist_ok=True)

    def cleanName(self, name):
        validC = "abcdefghijklmnopqrstuvwxyz1234567890"

        for c in name:
            if c.casefold() in validC.casefold():
                continue
            else:
                name = name.replace(c,"_")

        return name
