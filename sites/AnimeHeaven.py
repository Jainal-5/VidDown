import requests
from bs4 import BeautifulSoup as soup
import os
from util import downloader
from pathlib import Path
from platform import platform
import json
import traceback
import time

root = "https://animeheaven.me/"

currentPath = os.path.dirname(__file__)
parentPath = os.path.split(currentPath)[0]
statePath = os.path.join(parentPath, 
                         "state", 
                         "AnimeHeaven.json")

downloadPath = downloader.downloadPath

state = {}

def parseUrl(url):
    url = url.split(root)
    if "anime" in url[1]:
        return "Anime"
    elif "episode" in url[1]:
        return "episode"
    else:
        os.system("termux-vibrate -d 2000")
        print("unspported url")
        exit(0)

def getLinks(url=None):
    global state
    global downloadPath

    if url == None:
        url = input("Enter url: ")

    parsedUrl = parseUrl(url)
    try:
        header = {"user-agent":"Mozilla"}
        req = requests.get(
                url,
                timeout=10,
                headers=header)
        src = soup(req.text, "html.parser")

        if parsedUrl == "Anime":
            divTag = src.find("div", class_="linetitle2")
            title = downloader.cleanName(src.find("title").text)

            state["path"] = os.path.join(downloadPath, title)

            aTag = divTag.find_all("a")

            links = []

            if len(aTag) >= 0:
                for link in aTag:
                    links.append(root+link["href"])

                links.reverse()
                state["url"] = links
                downloader.saveState(state, statePath)
                print(f"Found and saved {len(aTag)} episodes")

                return links
            else:
                print("Unable to get any links")
                os.system("termux-vibrate -d 2000")
                exit(0);
        elif parsedUrl == "episode":
            url = src.find("div", class_="linetitle3").find("a")["href"]
            return getLinks(root + url)
        else:
            print("Unsupported url")
            os.system("termux-vibrate -d 2000")
            exit(0)
    except Exception as e:
        traceback.print_exc();

def yesNo():
    while(True):
        choice = input("Y/n:")

        if choice.lower() == "y":
            return True
        elif choice.lower() == "n":
            return False
        else:
            print("Invalid Input")

def getDownloadLink(url):
    req = requests.get(
            url,
            timeout=10,
            headers={"user-agent":"Mozilla"}
                       )

    src = soup(req.text, "html.parser")

    return src.find_all("div", class_="linetitle2")[1].find("a")["href"]

def main():
    global state
    global downloadPath

    try:
        state = downloader.loadState(statePath)
    except json.decoder.JSONDecodeError as e:
        print("Decoding State error")
        state = {}

    if state and state["url"]:
        print("An unfinished download is detected, would you like to resume?")
        if yesNo():
            links = state["url"]
            downloadPath = state["path"]
        else:
            print("Downloading new anime")
            links = getLinks()
    else:
        links = getLinks()

    for link in links[:]:
        time.sleep(3)
        #downloadLink = getDownloadLink(link)
        #time.sleep(3)
        downloader.download({"url":link}, downloadPath)

        links.remove(link)
        state["url"] = links
        downloader.saveState(state, statePath)

    print("Download finish")
    os.system("termux-vibrate -d 5000")
        

