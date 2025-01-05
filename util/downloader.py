import yt_dlp
import traceback
import json
import sys
import time
import requests
import os
from platform import platform
from util.FileManager import FileManager
import dotenv
from pathlib import Path

def download(data,path, retry=0,ydl_opt=None):

    fm = FileManager()

    if retry == 6:
        os.system("termux-vibrate -d 2000")
        sys.exit()

    url = data['url']

    try:
        title = data['title']
        title = fm.cleanName(title)
    except KeyError as e:
        print("Title is missing, using title from url")
        title = getTitle(url)

    print('TITLE')
    print(str(os.path.join(path,title)))
    #check if file has been deleted
    #res = requests.get(url)

    #if "file was deleted".casefold() in res.text.casefold():
        #return "Fail"


    if ydl_opt == None:
        ydl_opt = {
            'outtmpl': os.path.join(path,title + '.%(ext)s'),
            'format': 'best',
            'progress_hooks': [lambda d: progress(d, title)],
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opt) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        print(str(e))
        traceback.print_exc()

        print(f'Retrying: {retry}')

        if "[SSL: CERTIFICATE_VERIFY_FAILED" in str(e):
            choice = input("Would you like to disable check certificate?: Y:")

            if choice.lower() == "y":
                ydl_opt["nocheckcertificate"] = True
            else:
                print("Quitting")
                time.sleep(1)
                sys.exit()

        if "Errno 1" in str(e):
            name = input("Name has Invalid character\nPlease choose another one: ")
            download({"url":url,"title":name},path,retry+1,ydl_opt)

        retry += 1

        time.sleep(2)
        download(data, path, retry,ydl_opt)
    except Exception as e:
        print('An unexpected error occurred')
        sys.exit()

def getTitle(url):
    with yt_dlp.YoutubeDL() as f:
        info = f.extract_info(url,download=False)

    return info["title"]

def progress(d, title):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        print(f'Downloading: {title} - {percent}', end='\r', flush=True)
    else:
        print('\nDownloaded')

def saveState(urls, path):
    with open(path, 'w') as f:
        json.dump(urls, f)

def loadState(path):
    with open(path, 'r') as f:
        link = json.load(f)
    return link

def getSite(site):
    if site == "gogo":
        print("Enter your gogoanime login info")
        return "GA-"

def setLoginCredentials(site):
    prefix = getSite(site)

    print("Please Enter your email")

    email = input(":")

    print("Please Enter your password")
    password = input(":")

    fm = FileManager()

    envPath = Path(os.path.join(fm.getParentDirectory(), ".env"))

    if not os.path.exists(envPath):
        envPath.touch(mode=0o600, exist_ok=False)

    dotenv.set_key(dotenv_path=envPath,
                   key_to_set=prefix + "EMAIL",
                   value_to_set=email)
    dotenv.set_key(dotenv_path=envPath,
                   key_to_set=prefix + "PASSWORD",
                   value_to_set=password)
