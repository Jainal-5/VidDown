import yt_dlp
import traceback
import os
import json
import sys

def download(data,path,retry=0):

    if retry == 5:
        sys.exit()

    url = data['url']
    title = data['title']

    print('TITLE')
    print(title)

    ydl_opt = {
            'outtmpl':f'{path}/{title}.%(ext)s',
            'format':'best',
            }

    try:
        with yt_dlp.YoutubeDL(ydl_opt) as ydl:
            ydl.download([url])
    except Exception as e:
        print('An error occurred')
        traceback.print_exc()
        print(f'Retrying: {retry}')
        retry += 1
        download(data,path,retry)

def saveState(urls,path):
    with open(path,'w') as f:
        json.dump(urls,f)

def loadState(path):
    with open(path,'r') as f:
        link = json.load(f)
    return link
