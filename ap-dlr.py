import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
import sys
import subprocess
import re

request_header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'}
base_url = "https://animepahe.com"

index_url = "https://animepahe.com/anime"
index_page = requests.get(index_url, headers=request_header)
index_soup = BeautifulSoup(index_page.content, 'html.parser')

# get list of currently running firefox processes (for in case -- keyboardInterrupt occurs)
tasklist = subprocess.check_output(['tasklist', '/fi', 'imagename eq firefox.exe'], shell=True).decode()
currentFFIDs = re.findall(r"firefox.exe\s+(\d+)", tasklist)

#firefox-webdriver options
options = FirefoxOptions()
options.add_argument("--headless")

#initiate driver
driver = webdriver.Firefox(options=options)
driver.install_addon('D:\\WorkSpace\\animepahe-dlr\\extensions\\universal-bypass.xpi', temporary=True)
driver.install_addon('D:\\WorkSpace\\animepahe-dlr\\extensions\\uBlock0@raymondhill.net.xpi', temporary=True)
driver.install_addon('D:\\WorkSpace\\animepahe-dlr\\extensions\\mozilla_cc3@internetdownloadmanager.com.xpi', temporary=True) # use idm if available


def get_anime_list():
    # get list of anime titles in webpage
    anime_list = []
    for tag in index_soup.find_all('a'):
        anime_list.append(tag.text)
    return anime_list

def search_anime_title(anime_search_text):
    # search for anime title
    print("###--(Searching for anime..)--###") ######### delete after debug
    anime_list = get_anime_list()

    # store a list of matching titles
    matching_titles = [s for s in anime_list if anime_search_text.lower() in s.lower()]
    for title in matching_titles:
        print("[" + str(matching_titles.index(title)) + "] " + str(title))

    # get selection from user
    select = int(input("select[#] : "))
    print("selected : " + str(matching_titles[select]))

    return str(matching_titles[select])

def get_episode_links(anime_link):
    print("###--(getting episode links...)--###") ######### delete after debug

    # getting dynamic-page source using selenium-firefox-driver
    driver.get(anime_link)

    #clear all tab except main tab
    driver.switch_to.window(driver.window_handles[1]) #switch-to add-on confirmation tab
    driver.close() #close active tab
    driver.switch_to.window(driver.window_handles[0]) #switch back to main tab

    time.sleep(1)

    anime_page = driver.page_source
    anime_page_soup = BeautifulSoup(anime_page, 'html.parser')

    return [base_url + a['href'] for a in anime_page_soup.find_all('a', {"class" : "play"})]

def get_download_link(episode_link, quality):

    # getting dynamic-page source using selenium-firefox-driver
    driver.get(episode_link)

    time.sleep(2)

    episode_page = driver.page_source
    episode_page_soup = BeautifulSoup(episode_page, 'html.parser')

    links = [a for a in episode_page_soup.find_all('a', {'class': 'dropdown-item', 'target':'_blank'})]
    for a in links:
        for q in quality:
            if a.text.find(q) != -1:
                download_link = a['href']
                break
    
    if "download_link" in locals():
        return download_link
    else:
        gracious_exit("Error while getting download_link :(") #exits graciously

def download(download_link):

    # getting dynamic-page source using selenium-firefox-driver
    driver.get(download_link)
    time.sleep(4) #wait for elements to load
    print("- DOWNLOADING : " + driver.title.replace(" :: Kwik",''))
    driver.find_element_by_class_name('button').click()

    time.sleep(3) # wait for download to start

def gracious_exit(msg):
    driver.quit()
    sys.exit(msg)


def main():
    anime_search_text = input("Search : ")
    anime_title = search_anime_title(anime_search_text)

    qualtiy = ["720p", "576p", "480p"]

    # get link tail for selected anime
    for atag in index_soup.find_all('a', title = anime_title):
        tail = atag['href']

    anime_link = base_url + tail #link of anime-page

    episode_links = get_episode_links(anime_link)

    if not episode_links:
        gracious_exit("Couldln't finding any episodes")
        
    for ep_link in episode_links:
        download_link = get_download_link(ep_link, qualtiy)
        download(download_link)


    gracious_exit("All downloads Started !!") #exits graciously
    


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:

        #find new firefox processes
        tasklist = subprocess.check_output(['tasklist', '/fi', 'imagename eq firefox.exe'], shell=True).decode()
        newFFIDs = set(re.findall(r"firefox.exe\s+(\d+)", tasklist)).difference(currentFFIDs)

        #kills spawned firefox drivers -- (may also crash some tabs in other firefox sessions)
        taskkill = 'taskkill /f '+''.join(["/pid "+f+" " for f in newFFIDs]).strip()
        subprocess.check_output(taskkill.split(), shell=True)

        print("KeyboardInterrupt : Exiting with dirty hands..")
        print("You may experience tab-crash in your firefox sessions")
    except:
        gracious_exit("Caught an Unexpected Error : Exiting Graciously..")