import yt_dlp
import traceback
import json
import sys

def download(data, path, retry=0):

    if retry == 5:
        sys.exit()

    url = data['url']
    title = data['title']

    print('TITLE')
    print(title)

    ydl_opt = {
        'outtmpl': f'{path}/{title}.%(ext)s',
        'format': 'best',
        'progress_hooks': [lambda d: progress(d, title)],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opt) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        print('Download error occurred')
        traceback.print_exc()
        print(f'Retrying: {retry}')
        retry += 1
        download(data, path, retry)
    except Exception as e:
        print('An unexpected error occurred')
        traceback.print_exc()
        sys.exit()

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

