from json import load
from typing import ByteString
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time

request_header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'}
base_url = "https://animepahe.com"

index_url = "https://animepahe.com/anime"
index_page = requests.get(index_url, headers=request_header)
index_soup = BeautifulSoup(index_page.content, 'html.parser')

#firefox-webdriver-options
options = FirefoxOptions()
options.add_argument("--headless")

def get_anime_list():
    # get list of anime titles in webpage
    print("getting anime list ..") ######### delete after debug
    anime_list = []
    for tag in index_soup.find_all('a'):
        anime_list.append(tag.text)
    return anime_list

def search_anime_title(anime_search_text):
    # search for anime title
    print("getting anime title ...") ######### delete after debug
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
    # initiating webdriver
    print("getting episode link ....") ######### delete after debug

    driver = webdriver.Firefox(options=options)
    driver.get(anime_link)

    time.sleep(1)

    anime_page = driver.page_source
    anime_page_soup = BeautifulSoup(anime_page, 'html.parser')

    driver.close() #close all tabs
    driver.quit() #closes firefox-headless after usage

    return [base_url + a['href'] for a in anime_page_soup.find_all('a', {"class" : "play"})]

def get_download_link(episode_link, quality):

    print("getting download link .....") ######### delete after debug

    # initiating webdriver
    driver = webdriver.Firefox(options=options)
    driver.get(episode_link)

    time.sleep(2)

    episode_page = driver.page_source
    episode_page_soup = BeautifulSoup(episode_page, 'html.parser')

    driver.close() #close all tabs
    driver.quit() #closes firefox-headless after usage

    links = [a for a in episode_page_soup.find_all('a', {'class': 'dropdown-item', 'target':'_blank'})]
    for a in links:
        if a.text.find(quality) != -1:
            download_link = a['href']
    
    return download_link

def download(download_link):

    print("downloading.....")

    #configuring profile
    fxprofile = webdriver.FirefoxProfile()
    fxprofile.set_preference('browser.download.folderList', 2) # custom location
    fxprofile.set_preference("browser.download.manager.showWhenStarting", False)
    fxprofile.set_preference("browser.download.dir",'D:\\WorkSpace\\animepahe-dlr\\Downloads\\')
    fxprofile.set_preference("browser.helperApps.neverAsk.saveToDisk", "video/mp4")

    #initiate driver
    driver = webdriver.Firefox(firefox_profile=fxprofile, options=options)
    driver.install_addon('D:\\WorkSpace\\animepahe-dlr\\extension\\universal-bypass.xpi', temporary=True)
    driver.install_addon('D:\\WorkSpace\\animepahe-dlr\\extension\\uBlock0@raymondhill.net.xpi', temporary=True)
    driver.install_addon('D:\\WorkSpace\\animepahe-dlr\\extension\\mozilla_cc3@internetdownloadmanager.com.xpi', temporary=True) # use idm if available

    time.sleep(2)
    driver.get(download_link)
    time.sleep(3)
    driver.switch_to_window(driver.window_handles[0])
    time.sleep(2)
    driver.find_element_by_class_name('button').click()

    time.sleep(3)

    driver.close() #close all tabs
    driver.quit() #closes firefox-headless after usage

def main():
    # anime_search_text = input("Search : ")
    anime_title = "Joshiraku" #search_anime_title(anime_search_text)

    qualtiy = "720p"

    # get link tail 
    for atag in index_soup.find_all('a', title = anime_title):
        tail = atag['href']

    anime_link = base_url + tail
    #print(anime_link)

    episode_links = get_episode_links(anime_link) 
    print(episode_links[0])

    for ep_link in episode_links:
        download_link = get_download_link(ep_link, qualtiy)
        download(download_link)

    print("all dl staretd /////")
    



#print(index_soup.text)
#print(index_soup.find_all('a', title = "Zombie-Loan Specials"))


if __name__ == "__main__":
    main()