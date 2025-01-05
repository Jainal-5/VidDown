import requests
from bs4 import BeautifulSoup as soup
import os
import traceback
from util.FileManager import FileManager
from util import session
from sites import base_site
from util import downloader

class AnimeHeaven(base_site.BaseSite):
    def __init__(self):
        super().__init__()
        self.root = "https://animeheaven.me/"
        self.fm = FileManager()
        self.downloadPath = self.fm.getDownloadPath()
        self.statePath = os.path.join(self.fm.getStateDirectory(),"AnimeHeaven.json")
        self.sessions = session.Sessions(self.statePath)

    def parseUrl(self,url):
        if self.root not in url:
            print("Unsupported url")
            self.main()

        url = url.split(self.root)

        if len(url) < 2:
            print("Unsupported url")
            self.main()

        if "anime" in url[1]:
            return "Anime"
        elif "episode" in url[1]:
            return "episode"
        else:
            os.system("termux-vibrate -d 2000")
            print("unspported url")
            exit(0)

    def getLinks(self,url=None):
        _session = session.SessionInfo()

        if url == None:
            url = input("Enter url: ")

        parsedUrl = self.parseUrl(url)
        try:
            header = {"user-agent":"Mozilla"}
            req = requests.get(
                    url,
                    timeout=10,
                    headers=header)
            src = soup(req.text, "html.parser")

            if parsedUrl == "Anime":
                divTag = src.find("div", class_="linetitle2")
                title = self.fm.cleanName(src.find("title").text)

                _session.title = title

                index = self.sessions.searchSessions(title)

                if index:
                    print(f"{title} already exists in session with index {index - 1}")
                    print("Would you like to download this?")

                    if self.yesNo():
                        self.download(index - 1)
                    else:
                        self.main()

                downloadPath = os.path.join(self.downloadPath, title)

                self.fm.makeDirectory(downloadPath)

                _session.downloadPath = downloadPath

                aTag = divTag.find_all("a")

                links = []

                if len(aTag) >= 0:
                    for link in aTag:
                        links.append(self.root+link["href"])

                    links.reverse()
                    _session.url = links
                    self.sessions.add(_session)
                    self.sessions.saveSessions()
                    print(f"Found and saved {len(aTag)} episodes")

                    return links
                else:
                    print("Unable to get any links")
                    os.system("termux-vibrate -d 2000")
                    self.main()
            elif parsedUrl == "episode":
                url = src.find("div", class_="linetitle3").find("a")["href"]
                return getLinks(self.root + url)
            else:
                print("Unsupported url")
                os.system("termux-vibrate -d 2000")
                self.main()
        except Exception as e:
            traceback.print_exc();

    def getDownloadLink(self,url):
        req = requests.get(
                url,
                timeout=10,
                headers={"user-agent":"Mozilla"}
                           )

        src = soup(req.text, "html.parser")

        return src.find_all("div", class_="linetitle2")[1].find("a")["href"]

    def listDownload(self,index):
        currentSession = self.sessions.sessions[index]
        for link in currentSession.url[:]:
            download_link = self.getDownloadLink(link)

            downloader.download({"url":download_link}, currentSession.downloadPath)

            currentSession.url.remove(link)
            self.sessions.saveSessions()

        print("Download finish")
        os.system("termux-vibrate -d 5000")

        return currentSession

    def dictionaryDownload(self,index):
        currentSession = self.sessions.sessions[index]
        for title, link in currentSession.url.copy().items():
            download_link = self.getDownloadLink( link)

            data = {
                    "title":title,
                    "url":download_link
                    }

            downloader.download(data, currentSession.downloadPath)

            currentSession.url.pop(title)
            self.sessions.saveSessions()

        print("Download finish")
        os.system("termux-vibrate -d 5000")

        return currentSession
