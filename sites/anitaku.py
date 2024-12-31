from lxml import html
import time
import sys
import os
from util import downloader
import requests
from bs4 import BeautifulSoup as soup
import traceback
from decouple import config
from pathlib import Path

root = 'https://gogoanime3.cc'
downPath = downloader.downloadPath
state = {}

current_Path = os.path.dirname(__file__)

parentDir = os.path.split(current_Path)[0]

statePath = os.path.join(parentDir,
                         "state",
                         "state.json")

def setDownPath(page_source,isLong = 0):
    dirName = soup(page_source,'html.parser').find_all('title')[0].text

    global downPath

    if len(downPath + dirName) >= 255:
        print(f"File name is too long with {len(dirName)} characters.")
        print("Please Enter shorter title")
        dirName = input(":")

    cDirName = downloader.cleanName(dirName)
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

    if "category" in url:
        url = root + url.split("category/")[1]

    try:
        res = requests.get(parseUrl(url))
        setDownPath(res.text)

        links = {}
        episode = 0;

        while(True):

            if episode == 0:
                clink = url.split("-episode-")[0]
            else:
                clink = url.split("-episode-")[0] + "-episode-" + str(episode)
            print(f"Current link => {clink}")

            time.sleep(2.5)

            res = requests.get(clink)

            if "Not Found" not in res.text or res.status_code == 200:

                links[f"Episode {episode}"] = clink

                print(f"Found Episode{episode}")

                episode += 1
            else:

                print(f"Episode{episode} not found.")

                if episode == 0: 
                    episode += 1
                else: break

        print(f"Links >>>>>>>>>> {links}")

        state["url"] = links
        downloader.saveState(state, statePath)

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

#get download links
def getDownLinks(url,session,quality, try_=0):

    if try_ > 5:
        print("Failed to get download link")
        os.system("termux-api -d 2000")
        exit(0)

    if url is not None:
        print('Current url: '+url)

        try:
            source = session.get(url)
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
        state = downloader.loadState(statePath)
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
    downloader.saveState(state,statePath)

    for title,link in ep_links.copy().items():
        
        try:
            down_link = getDownLinks(link,session,state["quality"])
        except ConnectionError as e:
            print(f"Error occured {e}")
            os.system("termux-vibrate -d 2000")
        if down_link == None:
            continue

        print(f'Final Link: {down_link}')

        data = {"url":down_link,"title":title}
        time.sleep(2.5)
        downloader.download(data,downPath)

        ep_links.pop(title)
        state['url'] = ep_links
        downloader.saveState(state,statePath)

    print('Download Completed')

    if fail:
        printFail(fail)

    print('Quiting...')

    session.close()
    os.system("termux-vibrate -d 2000")
