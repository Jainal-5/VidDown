from lxml import html
import time
import sys
import os
import downloader
import requests
from bs4 import BeautifulSoup as soup
import traceback
from decouple import config

root = 'https://gogoanime3.cc'
downPath = '/data/data/com.termux/files/home/storage/shared/Download/'
state = {}

def cleanName(name):
    validC = "abcdefghijklmnopqrstuvwxyz1234567890"

    for c in name:
        if c.casefold() in validC.casefold():
            continue
        else:
            name = name.replace(c,"_")

    return name

def setDownPath(page_source,isLong = 0):
    dirName = soup(page_source,'html.parser').find_all('title')[0].text

    global downPath

    if len(downPath + dirName) >= 255:
        print(f"File name is too long with {len(dirName)} characters.")
        print("Please Enter shorter title")
        dirName = input(":")

    cDirName = cleanName(dirName)
    downPath = downPath + cDirName

    global state
    state['path'] = downPath

    os.makedirs(downPath,exist_ok=True)

def parseUrl(url):
    titleUrl = root + "/category/" + url.replace(root,"").split("-episode-")[0]
    print(f"Title Url >>>>>>> {titleUrl}")
    return titleUrl

#get Video links
def getLinks(url=None):

    if url is None:
        print('Enter Url')
        url = input(':')

    print('Getting video links...')

    try:
        res = requests.get(parseUrl(url))
        setDownPath(res.text)

        source = requests.get(url.strip())

        links = {}
        episode = 1;

        while(True):
            clink = url[:-9] + "episode-" + str(episode)
            print(f"Current link => {clink}")

            time.sleep(2.5)

            res = requests.get(clink)

            if "Not Found" not in res.text or res.status_code == 200:
                links[f"Episode {episode}"] = clink 
                episode += 1
            else:
                break

        print(f"Links >>>>>>>>>> {links}")

        state["url"] = links
        downloader.saveState(state,"state.json")

        return links

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        
        print("Try again? Y/n")
        choice = input(":")

        if choice.lower() == "y":
            getLinks(url)
        else:
            print("Quiting")

def getQuality():
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

def isQualityAvailable(quality,index):
    if(index == 0):
        return 0

    if len(quality) >= index:
        return quality[index]["href"]
    else:
        print(f"{index} is not available")
        print(f"Trying {index - 1}")
        return isQualityAvailable(quality,index - 1)

#get download links
def getDownLinks(url,session,quality):
    if url is not None:
        print('Current url: '+url)

        source = session.get(url)

        if not source.status_code == 200:
            print("Unable to get download lini")
            return None

        #container = soup(source.text, 'html.parser').find('li', class_="vidcdn")
        #source = requests.get(container.find("a")["data-video"])

        container = soup(source.text,"html.parser").find("div",class_="cf-download")

        links = container.find_all("a")

        link = isQualityAvailable(links,quality)

        return link

def checkRecentUrl():
    global downPath
    global state
    ep_links = None

    url = None
    try:
        url = state["url"]
    except KeyError as e:
        print(str(e))

    if url:
        print('An unfinished download is detected would you like to resume??')
        choice = input('Y/n:')
        while True:
            if choice.lower() == 'y':
                ep_links = state['url']
                downPath = state['path']
                break
            elif choice.lower() == 'n':
                ep_links = getLinks()
                state["quality"] = getQuality()
                break
            else:
                print('Invalid input:')
    else:
        ep_links = getLinks()
        state["quality"] = getQuality()

    return ep_links

def loadState():
    global state
    try:
        state = downloader.loadState("state.json")
    except Exception as e:
        print(str(e))

def printFail(fail):
    print("Failed to download the following: ")
    for title in fail:
        print ("\t" + title)
        print("File has been deleted.")

def login():
    s = requests.Session()
    result = s.get(root + "/login.html")

    tree = html.fromstring(result.text)
    # extract hidden token
    token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]

    payload = {
        'email': config("EMAIL"),
        'password': config("PASSWORD"),
        '_csrf': token
    }
    p = s.post(root + "/login.html", data=payload)

    return s

def islogin(session):
    res = session.get(root)

    if "account" in res.text:
        return True

    return False

def main():
    session = login()

    if not islogin(session):
        print("You are not logged in")
        print("You might want to change your settings")
        return 0

    loadState()

    global state 
    global downPath
    fail = []

    ep_links = checkRecentUrl()

    state['url'] = ep_links
    downloader.saveState(state,"state.json")

    for title,link in ep_links.copy().items():
        down_link = getDownLinks(link,session,state["quality"])

        print(f'Final Link: {down_link}')

        data = {"url":down_link,"title":title}
        time.sleep(2.5)
        downloader.download(data,downPath)

        ep_links.pop(title)
        state['url'] = ep_links
        downloader.saveState(state,"state.json")

    print('Download Completed')

    if fail:
        printFail(fail)

    print('Quiting...')

    session.close()
