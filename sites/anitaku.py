import requests
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from bs4 import BeautifulSoup as soup
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import getpass

#globe driver
driver = None
root = 'https://anitaku.pe'

#set Driver
def setDriver():
    global driver
    print('Setting driver...')
    opt = FirefoxOptions()
    opt.add_argument('--headless')
    driver = webdriver.Firefox(options=opt)
    print('Done')

#get url from user
def getUrl():
    print('Enter Url')
    url = input(':')

#get Video links
def getLinks(url):
    print('Getting video links...')
    driver.get(url)

    try:
        # Wait until the container is present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "load_ep"))
        )

        # Now extract the page source
        page_source = driver.page_source
        container = soup(page_source, 'html.parser').find('div', id="load_ep")

        # Find all <a> tags and extract their href attributes, stripping spaces
        links = container.find_all('a')

        for link in links:
            if 'href' in link.attrs:
                href = root + link['href'].strip()  # Concatenate root and href
                print(href)

        hrefs = [root + link['href'].strip() for link in links if 'href' in link.attrs]

        return hrefs

    except Exception as e:
        print(f"An error occurred: {e}")

#get download links
def getDownLinks(urls):#the url should be a list
    links = None
    if urls is not None:
        for url in urls:
            driver.get(url)

            source = driver.page_source

            page = soup(source,'html.parser').find('li',class_='downloads')

            link = page.find('a')['href']
            print(link)
            
#let user choose video quality
#def getQuality():

def login():
    print('Anitaku requires you to logjn first before you can download')

    try:
        user = input('Enter username:')
        password = getpass.getpass('Enter password:')

        print('Logging in...')

        session = requests.Session()

        response = session.get(root + '/login.html')

        src = soup(response.text,'html.parser')

        csrf = src.find('input',{'name':'_csrf'})['value']

        payload = {
                'email':user,
                'password':password,
                '_csrf':csrf
                }

        response = session.post(root + '/login.html',data=payload)

        if response.url != root + '/login.html':
            print('Login successful')
        else:
            print('Login failed:')

    except Exception as e:
        print(f'an error occured: {e}')

# Example usage
setDriver()

login()

links = getLinks('https://anitaku.pe/category/my-home-hero')

print(links)

getDownLinks(links)

driver.quit()
