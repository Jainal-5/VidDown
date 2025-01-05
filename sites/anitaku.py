import time
import os
from util import downloader
import requests
from bs4 import BeautifulSoup as soup
import traceback
from util.FileManager import FileManager
import dotenv
from util import session
from sites import base_site

class GogoAnime(base_site.BaseSite):
    def __init__(self):
        super().__init__()
        self.root = 'https://gogoanime3.cc/'
        self.fm = FileManager()
        self.downPath = self.fm.getDownloadPath()
        self.statePath = os.path.join(self.fm.getStateDirectory(), "state.json")
        self.sessions = session.Sessions(self.statePath)


    def setDownPath(self, page_source, _session):
        dirName = soup(page_source,'html.parser').find_all('title')[0].text

        cDirName = self.fm.cleanName(dirName)

        index = self.sessions.searchSessions(cDirName)

        if index:
            print(f"{cDirName} is found in session at index {index}")

            print("Would you like to download this?")

            if self.yesNo():
                self.download(index - 1)
            else:
                self.download(index=0)

        self.downPath = os.path.join(self.downPath,cDirName)
        _session.downloadPath = self.downPath
        _session.title = cDirName

        self.fm.makeDirectory(self.downPath)

    def parseUrl(self, url):
        titleUrl = self.root + "/category/" + url.replace(self.root,"").split("-episode-")[0]
        print(f"Title Url >>>>>>> {titleUrl}")
        return titleUrl

    def getLinks(self,url=None):
        _session = session.SessionInfo()

        if url is None:
            print('Enter Url')
            url = input(':')

        print('Getting video links...')

        if "category" in url:
            url = self.root + url.split("category/")[1]

        try:
            res = requests.get(self.parseUrl(url),timeout=10)
            self.setDownPath(res.text,_session)

            links = {}
            episode = 0;

            while(True):

                if episode == 0:
                    clink = url.split("-episode-")[0]
                else:
                    clink = url.split("-episode-")[0] + "-episode-" + str(episode)
                print(f"Current link => {clink}")

                time.sleep(2.5)

                res = requests.get(clink,timeout=10)

                if "Not Found" not in res.text or res.status_code == 200:

                    links[f"Episode {episode}"] = clink

                    print(f"Found Episode {episode}")

                    episode += 1
                else:

                    print(f"Episode {episode} not found.")

                    if episode == 0: 
                        episode += 1
                    else: break

            print(f"Links >>>>>>>>>> {links}")

            _session.url = links
            _session.quality = self.getQuality()
            self.sessions.add(_session)
            self.sessions.saveSessions()

            return links

        except requests.ConnectionError as e:
            print("Connection Error, please check you internet connection")

            if yesNoError():
                self.getLinks(url)
            else:
                self.main()

    def yesNoError(self):
        os.system("termux-vibrate -d 2000")

        return self.yesNo()
    
    def getQuality(self):
        validC = [0,1,2,3]

        while(True):
            print("Enter desired quality")
            print("\t0 - 360")
            print("\t1 - 480")
            print("\t2 - 720")
            print("\t3 - 1080")

            choice = int(input(":"))

            if choice in validC:
                return choice
            else:
                print("Choice out of bounds Try again")
                time.sleep(2)

    def isQualityAvailable(self,quality,index):
        if(index == 0):
            if len(quality) == 1:
                return quality[index]["href"]
            else:
                return None

        if len(quality) - 1 >= index:
            return quality[index]["href"]
        else:
            print(f"{index} is not available")
            print(f"Trying {index - 1}")
            return isQualityAvailable(quality,index - 1)

    def getDownLinks(self, url,session,quality, try_=0):

        if try_ > 5:
            print("Failed to get download link")
            os.system("termux-api -d 2000")
            exit(0)

        if url is not None:
            print('Current url: '+url)

            try:
                source = session.get(url, timeout=10)
            except requests.exceptions.ConnectionError as e:
                print(e)
                print("Error getting Download links")
                print(f"retrying ({try_+1}/5)")
                time.sleep(2.5)
                return getDownLinks(url,session,quality,try_+1)

            if not source.status_code == 200:
                print("Unable to get download lini")
                return None

            #container = soup(source.text, 'html.parser').find('li', class_="vidcdn")
            #source = requests.get(container.find("a")["data-video"])

            container = soup(source.text,"html.parser").find("div",class_="cf-download")

            links = container.find_all("a")

            link = self.isQualityAvailable(links,quality)

            return link

    def login(self):

        dotenv.load_dotenv()
        s = requests.Session()

        try:
            result = s.get(self.root + "/login.html",timeout=10)
        except requests.ConnectionError as e:
            print("Connection Error occured.")
            print("Please check your internet connection.")
            input("Press any key to continue:")
            return self.login()

    #    tree = html.fromstring(result.text)
    #    # extract hidden token
    #    token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
    #

        src = soup(result.text,"html.parser")

        form = src.find_all("form")[1]

        token = form.find("input")["value"]

        try:
            payload = {
                'email': os.getenv("GA-EMAIL"),
                'password': os.getenv("GA-PASSWORD"),
                '_csrf': token
            }
        except KeyError as e:
            print("Credential doesnt exists")
            downloader.setLoginCredentials("gogo")
            return login()

        p = s.post(self.root + "/login.html", data=payload)

        return s

    def islogin(self,session):
        res = session.get(self.root)

        if "account" in res.text:
            return True

        return False

    def download(self, index=0):
        login_session = self.login()

        if not self.islogin(login_session):
            print("You are not logged in")
            print("You might want to change your settings")
            downloader.setLoginCredentials("gogo")
        
        while len(self.sessions.sessions) > 0:
            currentSession = self.sessions.sessions[index]
            for title, link in currentSession.url.copy().items():
                download_link = self.getDownLinks( link, login_session, currentSession.quality)

                data = {
                        "title":title,
                        "url":download_link
                        }

                downloader.download(data, currentSession.downloadPath)

                currentSession.url.pop(title)
                self.sessions.saveSessions()

            if index != 0:
                index = 0

            self.sessions.session.remove(currentSession)
            self.sessions.saveSessions()
