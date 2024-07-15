
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'downloader')))


import downloader
import requests
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from bs4 import BeautifulSoup as soup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import getpass
import traceback

#globe driver
driver = None
root = 'https://anitaku.pe'
downPath = '/data/data/com.termux/files/home/storage/shared/Download/'
state = {}

#set Driver
def setDriver():
    global driver
    print('Setting driver...')
    opt = FirefoxOptions()
    opt.add_argument('--headless')
    driver = webdriver.Firefox(options=opt)
    print('Done')

#get Video links
def getLinks(url=None):

    if url is None:
        print('Enter Url(Please note that the only supported link are the links from that has category in it. A link to an episode is not yet supported)')
        url = input(':')

    print('Getting video links...')

    try:
        driver.get(url)

        # Now extract the page source
        page_source = driver.page_source

        container = soup(page_source, 'html.parser').find('div', id="load_ep")

        # Find all <a> tags and extract their href attributes, stripping spaces
        links = container.find_all('a')
        dirName = soup(page_source,'html.parser').find('title').text

        global downPath
        downPath = downPath + dirName

        global state
        state['path'] = downPath

        state['path'] = downPath

        os.makedirs(downPath,exist_ok=True)

        for link in links:
            if 'href' in link.attrs:
                href = root + link['href'].strip()  # Concatenate root and href
                print(href)

        hrefs = [root + link['href'].strip() for link in links if 'href' in link.attrs]

        if len(hrefs) > 0:
            print('Episode Links Retrieved')
            return hrefs
        else:
            print('Unable to get links')
            print('LINKS:')
            print(hrefs)
            getLinks(url)

    except Exception as e:
        print(f"An error occurred: {e}")
        getLinks(url)

#get download links
def getDownLinks(url):
    if url is not None:
        print('Current url: '+url)
        driver.get(url)

        source = driver.page_source

        page = soup(source,'html.parser').find('li',class_='dowloads')

        link = page.find('a')['href']
        print('Links: ' +  link)
        return link

#getQuality

def getQuality():
    print('Please Enter desired quality')

    print('Available Qualities:')

    print('\t0 - 360')
    print('\t1 - 480')
    print('\t2 - 720')
    print('\t3 - 1080')

    validC = ['0','1','2','3']

    while(True):
        choice = input(':')

        if choice in validC:
            return choice
        else:
            print('Pleas enter a valid input')
            
#let user choose video quality
def setQuality(url,choice):
    index = int(choice)

    try:
        driver.get(url)

        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'mirror_link')))

        src = driver.page_source
        title = soup(src,'html.parser').find('title').text
        container = soup(src,'html.parser').find('div',class_='mirror_link')

        qlist = container.find_all('div',class_='dowload')

        #selectedQ = qlist[index].find('a')['href']
        selectedQ = None

        for item in qlist:
            text = item.find('a').text

            #current url
            curl = item.find('a')['href']
            print(f'Current text: {text}')
            if index == 0 and '360' in text:
                selectedQ = curl
            elif index == 1 and '480' in text:
                selectedQ = curl
            elif index == 2 and '720' in text:
                selectedQ = curl
            elif index == 3 and '1080' in text:
                selectedQ = curl

        link = {'url':selectedQ,'title':title}
        print(f'Links:\n {link}')
        return link
    except Exception as e:
        print('An error occured:')
            
        traceback.print_exc()

def main():
    setDriver()
    global state
    global downPath

    ep_links = None

    stateDir = os.path.join('/data/data/com.termux/files/home/projects/python/vidDown/states','state.json')

    if os.path.exists(stateDir):
        state = downloader.loadState(stateDir)

        if state['url']:
            print('An unfinished download is detected would you like to resume??')
            choice = input('Y/n:')
            if choice.lower() == 'y':
                ep_links = state['url']
                downPath = state['path']
        else:
            ep_links = getLinks()
    else:
        ep_links = getLinks()

    state['url'] = ep_links
    downloader.saveState(state,stateDir)

    quality_input = getQuality()

    for ep in ep_links[:]:
        down_link = getDownLinks(ep)

        final_link = setQuality(down_link,quality_input)

        print(f'Final Link: {final_link}')

        downloader.download(final_link,downPath)
        ep_links.remove(ep)
        state['url'] = ep_links
        downloader.saveState(state,stateDir)

    print('Download Completed')
    print('Quiting...')
    driver.quit()

main()
