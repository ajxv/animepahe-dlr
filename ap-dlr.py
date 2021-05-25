import requests
from bs4 import BeautifulSoup
import time
import sys
import subprocess
import re
import os
import platform
from custom_modules import inbuilt_dlr
from custom_modules.initiate_driver import driver, currentFFIDs

if len(sys.argv) > 1 and "-idm" in sys.argv:
    download_with_idm = True
else:
    download_with_idm = False

this_dir = os.path.dirname(os.path.abspath(__file__)) #path where this script is stored
downloads_folder = os.path.expanduser("~") + os.path.sep + "Videos" + os.path.sep
current_system_os = str(platform.system()) #get current os

#enable this to download with idm if download with idm is selected
if download_with_idm:
    driver.install_addon(this_dir + os.path.sep + "driver_extensions" + os.path.sep + "mozilla_cc3@internetdownloadmanager.com.xpi", temporary=True) # use idm if prefered


#add geckodriver path to PATH
geckodriver_path = os.path.join(os.path.expanduser("~"), "geckodriver")
if os.path.exists(os.path.join(geckodriver_path, r"geckodriver.exe")) or os.path.exists(os.path.join(geckodriver_path, r"geckodriver")):
    os.environ['PATH'] = os.environ['PATH'] + os.pathsep + geckodriver_path

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
    print('''
    ----------------------------------------
            Searching for anime..
    ----------------------------------------
    ''')
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
    print('''
    ----------------------------------------
            Getting episode links...
    ----------------------------------------
    ''')

    # getting dynamic-page source using selenium-firefox-driver
    driver.get(anime_link)

    time.sleep(2)

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
        graceful_exit("Error while getting download_link :(") #exit gracefully

def external_download(download_link):

    # getting dynamic-page source using selenium-firefox-driver
    driver.get(download_link)
    time.sleep(4) #wait for elements to load
    print("[#] Download Captured : " + driver.title.replace(" :: Kwik",''))
    driver.find_element_by_xpath("//form[@method = 'POST']/button[contains(@class, 'button')]").click()

    time.sleep(3) # wait for download to start

def tab_handler():
    #clear all tab except main tab
    driver.switch_to.window(driver.window_handles[1]) #switch-to add-on confirmation tab
    driver.close() #close active tab
    time.sleep(3)

    driver.switch_to.window(driver.window_handles[0]) #switch back to main tab

def create_folder(in_location, title, current_os):
    if str(current_os).lower() == "windows":
        foldername = re.sub('[/\:*?<>|]', ' ', title)
    elif str(current_os).lower() == "linux":
        foldername = re.sub('[/]', ' ', title)

    #make a new folder to download to (if one doesn't already exist)
    new_folder = os.path.join(in_location, foldername)
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
        
    return new_folder

def graceful_exit(msg):
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
        graceful_exit("Couldln't find any episode links")

    if download_with_idm:
        for ep_link in episode_links:
            download_link = get_download_link(ep_link, qualtiy)
            external_download(download_link)
            
        graceful_exit("\nAll Downloads Started !!") #exit gracefully
    else:
        anime_folder = create_folder(downloads_folder, anime_title, current_system_os)
        for ep_link in episode_links:
            download_link = get_download_link(ep_link, qualtiy)
            inbuilt_dlr.download(download_link, anime_folder)

        graceful_exit("\nAll Downloads Completed !!") #exit gracefully

if __name__ == "__main__":

    tab_handler() #handles open tabs in webdriver

    try:
        main()
    except KeyboardInterrupt:

        if current_system_os == "Windows": #needed only if in windows
            #find new firefox processes
            tasklist = subprocess.check_output(['tasklist', '/fi', 'imagename eq firefox.exe'], shell=True).decode()
            newFFIDs = set(re.findall(r"firefox.exe\s+(\d+)", tasklist)).difference(currentFFIDs)

            #kills spawned firefox drivers -- (may also crash some tabs in other firefox sessions)
            taskkill = 'taskkill /f '+''.join(["/pid "+f+" " for f in newFFIDs]).strip()
            subprocess.check_output(taskkill.split(), shell=True)

            print("\nKeyboardInterrupt : Exiting with dirty hands..")
            print("You may experience a tab-crash in your open firefox sessions")

        else:
            graceful_exit("\nKeyboardInterrupt : Exiting Gracefully..") #exit gracefully
    
    except Exception as e:
        graceful_exit("Oops! " + str(e.__class__) + " occured.")
    