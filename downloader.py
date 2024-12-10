import yt_dlp
import traceback
import json
import sys
import time
import requests

def download(data, path, retry=0,ydl_opt=None):

    if retry == 5:
        sys.exit()

    url = data['url']
    title = data['title']

    print('TITLE')
    print(title)

    #check if file has been deleted
    #res = requests.get(url)

    #if "file was deleted".casefold() in res.text.casefold():
        #return "Fail"


    if ydl_opt == None:
        ydl_opt = {
            'outtmpl': f'{path}/{title}.%(ext)s',
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

def progress(d, title):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        print(f'Downloading: {title} - {percent}', end='\r', flush=True)
    else:
        print('\nDownloaded')

def saveState(urls, path):
    with open("state.json", 'w') as f:
        json.dump(urls, f)

def loadState(path):
    with open(path, 'r') as f:
        link = json.load(f)
    return link

