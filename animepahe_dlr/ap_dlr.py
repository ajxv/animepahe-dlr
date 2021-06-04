import requests
from bs4 import BeautifulSoup
import time
import sys
import subprocess
import re
import os
import platform
from ap_dlr_modules import inbuilt_dlr
from ap_dlr_modules.initiate_driver import driver, WebDriverWait, EC, By
if os.name == 'nt':
    from ap_dlr_modules.initiate_driver import currentFFIDs
    
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


request_header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'}
base_url = "https://animepahe.com"

index_url = "https://animepahe.com/anime"
index_page = requests.get(index_url, headers=request_header)
index_soup = BeautifulSoup(index_page.content, 'html.parser')

def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('''
                 _                            _                   _ _      
      __ _ _ __ (_)_ __ ___   ___ _ __   __ _| |__   ___       __| | |_ __ 
     / _` | '_ \| | '_ ` _ \ / _ \ '_ \ / _` | '_ \ / _ \____ / _` | | '__|
    | (_| | | | | | | | | | |  __/ |_) | (_| | | | |  __/____| (_| | | |   
     \__,_|_| |_|_|_| |_| |_|\___| .__/ \__,_|_| |_|\___|     \__,_|_|_|   
                                 |_|                                        
    ''')

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
    for i, title in enumerate(matching_titles):
        print(f"[{i}] {title}")

    # get selection from user
    select = int(input("select[#] : "))
    print(f"selected : {str(matching_titles[select])}")

    return str(matching_titles[select])

def get_episode_links(anime_link):
    print('''
    ----------------------------------------
            Getting episode links...
    ----------------------------------------
    ''')

    # getting dynamic-page source using selenium-firefox-driver
    driver.get(anime_link)
    links = []
    while 1:
        time.sleep(3)
        anime_page = driver.page_source
        anime_page_soup = BeautifulSoup(anime_page, 'html.parser')
        
        links += [base_url + a['href'] for a in anime_page_soup.find_all('a', {"class" : "play"})]

        try:
            driver.find_element_by_xpath("//li[@class = 'page-item']/a[contains(@class, 'next-page')]").click()
        except: 
            break
    return links

def choose_eps_to_dl(total_episodes):
    print(f"No. of episodes : {total_episodes}\n")
    print("Options: [0 : all | x : episode x | x-y : episodes x to y]\n")
    chosen = []
    
    choice = input("Episodes to download : ").replace(' ', '').split(',')
    if choice == "":
        chosen.append(0)
        return chosen

    for i in range(len(choice)):
        if choice[i] == '0':
            chosen.clear
            for j in range(1, total_episodes + 1):
                chosen.append(j)
            break
        if "-" in choice[i]:
            r = choice[i].split('-')
            for j in range(int(r[0]), int(r[1]) + 1):
                chosen.append(j)
            continue
        chosen.append(int(choice[i]))

    return chosen

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
    #time.sleep(4) 
    #wait for elements to load
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//form[@method = 'POST']/button[contains(@class, 'button')]")))

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
    if current_os.lower() == "windows":
        foldername = re.sub('[/\:*?<>|]', ' ', title)
    elif current_os.lower() == "linux":
        foldername = re.sub('[/]', ' ', title)

    #make a new folder to download to (if one doesn't already exist)
    new_folder = os.path.join(in_location, foldername)
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
        
    return new_folder

def graceful_exit(msg):
    driver.quit()
    sys.exit(msg)

def winKeyInterruptHandler():
    #find new firefox processes
        tasklist = subprocess.check_output(['tasklist', '/fi', 'imagename eq firefox.exe'], shell=True).decode()
        newFFIDs = set(re.findall(r"firefox.exe\s+(\d+)", tasklist)).difference(currentFFIDs)

        #kills spawned firefox drivers -- (may also crash some tabs in other firefox sessions)
        taskkill = 'taskkill /f '+''.join(["/pid "+f+" " for f in newFFIDs]).strip()
        subprocess.check_output(taskkill.split(), shell=True)

        print("\nKeyboardInterrupt : Exiting with dirty hands..")
        print("You may experience a tab-crash in your open firefox sessions")

def main():
    try:
        banner() #displays banner
        tab_handler() #handles open tabs in webdriver

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
        
        episode_choice = choose_eps_to_dl(len(episode_links))
        
        if download_with_idm:
            print('''
        ----------------------------------------
                Starting Downloads..
        ----------------------------------------
        ''')
            for ep in episode_choice:
                download_link = get_download_link(episode_links[ep - 1], qualtiy)
                external_download(download_link)
                
            graceful_exit("\nAll Downloads Started !!") #exit gracefully
        else:
            print('''
        ----------------------------------------
                    Downloading..
        ----------------------------------------
        ''')
            anime_folder = create_folder(downloads_folder, anime_title, current_system_os)
            for ep in episode_choice:
                download_link = get_download_link(episode_links[ep - 1], qualtiy)
                inbuilt_dlr.download(download_link, anime_folder)

            graceful_exit("\nAll Downloads Completed !!") #exit gracefully

    except KeyboardInterrupt:
        if current_system_os.lower() == "windows": #needed only if in windows
            winKeyInterruptHandler()
        else:
            graceful_exit("\nKeyboardInterrupt : Exiting Gracefully..") #exit gracefully
    except Exception as e:
        graceful_exit(f"Oops! {str(e.__class__)} occured.")


if __name__ == "__main__":
    main()

    