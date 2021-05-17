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


def get_anime_list():
    # get list of anime titles in webpage
    anime_list = []
    for tag in index_soup.find_all('a'):
        anime_list.append(tag.text)
    return anime_list

def search_anime_title(anime_search_text):
    # search for anime title
    anime_list = get_anime_list()
    
    match = [s for s in anime_list if anime_search_text.lower() in s.lower()]
    for title in match:
        print("[" + str(match.index(title)) + "] " + str(title))

    select = int(input("select[#] : "))
    print("selected : " + str(match[select]))

    return str(match[select])

def get_episode_links(anime_link):
    # initiating webdriver
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(anime_link)

    time.sleep(1)

    anime_page = driver.page_source
    #anime_page = requests.get(anime_link, headers=request_header)
    anime_page_soup = BeautifulSoup(anime_page, 'html.parser')

    driver.close() #close all tabs
    driver.quit() #closes firefox-headless after usage

    return [base_url + a['href'] for a in anime_page_soup.find_all('a', {"class" : "play"})]


def main():
    # anime_search_text = input("Search : ")
    anime_title = "Joshiraku" #search_anime_title(anime_search_text)

    # get link tail 
    for atag in index_soup.find_all('a', title = anime_title):
        tail = atag['href']

    anime_link = base_url + tail
    #print(anime_link)

    episode_links = get_episode_links(anime_link) 
    print(episode_links[0])



#print(index_soup.text)
#print(index_soup.find_all('a', title = "Zombie-Loan Specials"))


if __name__ == "__main__":
    main()