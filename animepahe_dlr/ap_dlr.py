import requests
from bs4 import BeautifulSoup
import time
import sys
import subprocess
import re
import os
import platform
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tqdm import tqdm

# check command line args
download_with_idm = False
if len(sys.argv) > 1 and "-idm" in sys.argv:
    download_with_idm = True
    
current_system_os = str(platform.system()) #get current os

#class to store all required details of selected anime
class anime:
    selected = None
    id = None
    episode_count = None
    episode_sessions = {}
    eps_to_dl = None
    download_location = None

class banners:
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
    def searching():
        print('''
        ----------------------------------------
                Searching for anime..
        ----------------------------------------
        ''')
    def getting_eps():
        print('''
        ----------------------------------------
                Getting episode links...
        ----------------------------------------
        ''')
    def start_dl():
        print('''
        ----------------------------------------
                Starting Downloads..
        ----------------------------------------
        ''')
    def downloading():
        print('''
        ----------------------------------------
                    Downloading..
        ----------------------------------------
        ''')

def initiate_driver(): 
    global driver, currentFFIDs

    this_dir = os.path.dirname(os.path.abspath(__file__)) #path where this script is stored

    #add geckodriver path to PATH
    geckodriver_path = os.path.join(this_dir, "geckodriver")

    if not os.path.exists(geckodriver_path): #check if geckodriver path already exists
        gecko_installer.install(this_dir) #installs and adds geckodriver to PATH

    # add geckodriver path to PATH (only for current terminal session)
    os.environ['PATH'] = os.environ['PATH'] + os.pathsep + geckodriver_path

    #firefox-webdriver options
    options = FirefoxOptions()
    options.add_argument("--headless")
    gecko_log_file = os.path.join(geckodriver_path, 'geckodriver.log')

    if current_system_os.lower() == "windows": # we need this only in windows
        # get list of currently running firefox processes (for in case -- keyboardInterrupt occurs)
        tasklist = subprocess.check_output(['tasklist', '/fi', 'imagename eq firefox.exe'], shell=True).decode()
        currentFFIDs = re.findall(r"firefox.exe\s+(\d+)", tasklist)

    try:
        #initiate driver
        driver = webdriver.Firefox(options=options, service_log_path=gecko_log_file)

    except WebDriverException as driverException:
        print(driverException)

    firefox_extensions_dir = this_dir + os.path.sep + "driver_extensions"
    #Load add-ons to webdriver
    driver.install_addon(firefox_extensions_dir + os.path.sep + "universal-bypass.xpi", temporary=True)
    #add-ons required only if download with idm is selected
    if download_with_idm:
        driver.install_addon(firefox_extensions_dir + os.path.sep + "uBlock0@raymondhill.net.xpi", temporary=True)
        driver.install_addon(firefox_extensions_dir + os.path.sep + "mozilla_cc3@internetdownloadmanager.com.xpi", temporary=True) # use idm if prefered


def search_anime_index(search_text, index_url = "https://animepahe.com/anime"):

    banners.searching()

    index_page = requests.get(index_url)
    index_page_soup = BeautifulSoup(index_page.content, 'html.parser')

    #find all anime entries listed in the index page
    anime_index_list = [tag_item for tag_item in index_page_soup.find_all('a') if "/anime/" in tag_item['href']]

    #search anime_index_list for matching anime titles
    matched_titles = [item for item in anime_index_list if search_text in item.text.lower()]

    #return if no anime found
    if not matched_titles:
        banners.banner()
        print("No matching anime found. Retry!")
        return

    print("Result:")
    for i, anime in enumerate(matched_titles):
        print(f"  [{i}] {anime['title']}")
    print("") #blank-line

    choice = -1
    while(choice not in range(len(matched_titles))):
        try:
            choice = int(input("Select[#] : "))
        except ValueError:
            choice = -1

    return matched_titles[choice]

def get_episode_sessions(anime_link, anime_title):
    banners.getting_eps()
    anime_link = "https://animepahe.com" + anime_link

    anime_page = requests.get(anime_link)
    anime_page_soup = BeautifulSoup(anime_page.content, 'html.parser')

    #get anime id
    anime.id = int(anime_page_soup.find('a', text=anime_title)['href'].split("/")[-1])

    anime_meta = requests.get(f"https://animepahe.com/api?m=release&id={anime.id}").json()

    #get anime metadata
    anime.episode_count, page_count = anime_meta['total'], anime_meta['last_page']

    for page_no in range(1, page_count + 1):
        anime_json = requests.get(f"https://animepahe.com/api?m=release&id={anime.id}&sort=episode_asc&page={page_no}").json()
        ep_in_page = anime_json['to'] - anime_json['from'] + 1 #no.of eps in page

        for ep in range(ep_in_page):
            anime.episode_sessions[anime_json['data'][ep]['episode']] = anime_json['data'][ep]['session']

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
            return chosen
        if "-" in choice[i]:
            r = choice[i].split('-')
            for j in range(int(r[0]), int(r[1]) + 1):
                chosen.append(j)
            continue
        chosen.append(int(choice[i]))

    return chosen

def external_download(download_link):
    # getting dynamic-page source using selenium-firefox-driver
    driver.get(download_link)

    #wait for elements to load
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//form[@method = 'POST']/button[contains(@class, 'button')]")))

    print("[#] Download Captured : " + driver.title.replace(" :: Kwik",''))
    driver.find_element_by_xpath("//form[@method = 'POST']/button[contains(@class, 'button')]").click()

    time.sleep(3) # wait for download to start

def close_progress_bar():
    if "progress_bar" in globals():
        progress_bar.close()

def downloader(download_link, location):
    driver.get(download_link)
    #wait for elements to load
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//form[@method = 'POST']/button[contains(@class, 'button')]")))

    download_page_source = driver.page_source
    download_page_soup = BeautifulSoup(download_page_source, 'html.parser')

    post_link = download_page_soup.find('form')['action']
    token = download_page_soup.find('input', {'name': '_token'})['value']

    filename = driver.title.replace(" :: Kwik",'')
    file = location + os.path.sep + filename #complete path to file
    
    cookie = str(driver.get_cookie('kwik_session')['value'])

    current_url = driver.current_url #for 'referer' in request header

    header = {
        'Host': 'kwik.cx',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '47',
        'Origin': 'https://kwik.cx',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': current_url,
        'Cookie': "cf_clearance=5bccdfce967dac708ad88a921f2fa4c611dab4a1-1621779043-0-250; __cfduid=dea2a5db62313b8e6304deccf7ae9da841619857420; SERVERID=lux; kwik_session=" + cookie,
        'Upgrade-Insecure-Requests': '1'
    }

    #check if file alreay exists. If it does resume download if its incomplete.
    if os.path.exists(file):
        print("File already exists! Resuming download..")
        current_size = os.stat(file).st_size
        size_in_mb = current_size/(1024*1024)
        header.update( {'Range':'bytes=%d-' %current_size} )

    response = requests.post(post_link, headers=header, data = {'_token': token}, stream=True)
    try:
        total_length = int(response.headers.get('content-length'))
    except TypeError:
        if current_size > 190:
            print(f"[#] {filename}: ??% - {size_in_mb:.1f}M/??M (Unexpected error: Skipping file)")
            time.sleep(5)
            return

    if str(total_length) == "190":
        print(f"[#] {filename}: 100% - {size_in_mb:.1f}M/{size_in_mb:.1f}M")
        time.sleep(5)
        return

    global progress_bar
    progress_bar = tqdm(unit="B", unit_scale=True, total=total_length, desc=f"[#] {filename}", dynamic_ncols=True)
    with open(file, 'ab') as local_file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                # update the progress bar manually
                progress_bar.update(len(chunk))
                # write file
                local_file.write(chunk)
                local_file.flush()

    progress_bar.close() # close progress bar

def inbuilt_dlr(download_link, location):
    try:
        downloader(download_link, location)
    except Exception as e:
        #exit progressbar if initiated
        close_progress_bar()

        print(f"{str(e.__class__)} occured! Retrying..")
        time.sleep(5)
        inbuilt_dlr(download_link, location)

def start_downloads(episode_sessions, quality=['720', '1080', '576', '480', '360']):
    if download_with_idm:
        banners.start_dl()
    else:
        banners.downloading()

    for ep in anime.eps_to_dl:
        if ep not in episode_sessions: 
            continue

        episode_json = requests.get(f"https://animepahe.com/api?m=links&id={anime.id}&session={episode_sessions[ep]}").json()
        for res in quality:
            flag = False
            for i in range(len(episode_json['data'])):
                if res not in episode_json["data"][i]:
                    continue
                if download_with_idm:
                    external_download(episode_json['data'][i][res]['kwik_adfly']) #link to dl-page
                inbuilt_dlr(episode_json['data'][i][res]['kwik_adfly'], anime.download_location)
                flag = True
                break
            if flag == True:
                break
        
            
    graceful_exit("All downloads Completed !!")

def tab_handler():
    #clear all tab except main tab
    driver.switch_to.window(driver.window_handles[1]) #switch-to add-on confirmation tab
    driver.close() #close active tab
    time.sleep(3)

    driver.switch_to.window(driver.window_handles[0]) #switch back to main tab

def create_folder(folder_name, folder_location = os.path.expanduser("~") + os.path.sep + "Videos" + os.path.sep, current_os = str(platform.system())):
    if current_os.lower() == "windows":
        foldername = re.sub('[/\:*?<>|]', ' ', folder_name)
    elif current_os.lower() == "linux":
        foldername = re.sub('[/]', ' ', folder_name)

    #make a new folder to download to (if one doesn't already exist)
    new_folder = os.path.join(folder_location, foldername)
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
        
    return new_folder

def graceful_exit(msg):
    #exit progress bar if initiated
    close_progress_bar()
    driver.quit()
    sys.exit(msg)

def winKeyInterruptHandler():
    #exit progress bar if initiated
    close_progress_bar()
        
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
        banners.banner() #displays banner
        initiate_driver() #initiate webdriver
        tab_handler() #handles open tabs in webdriver

        while(not anime.selected):
            anime_search_text = input("Search [q: quit]: ")
            if anime_search_text == 'q':
                graceful_exit("Exiting..")
            #search for anime in anime-index-page
            anime.selected = search_anime_index(anime_search_text)
        
        print(f"\nSelected: {anime.selected.text}")

        #get episode-sessions from api json response
        get_episode_sessions(anime.selected['href'], anime.selected.text)

        if not anime.episode_sessions:
            graceful_exit("Couldln't find any episode links")
        
        anime.eps_to_dl = choose_eps_to_dl(anime.episode_count)
        
        if not download_with_idm:
            anime.download_location = create_folder(anime.selected.text)
        
        #start all downloads
        start_downloads(anime.episode_sessions)

    except KeyboardInterrupt:
        if current_system_os.lower() == "windows": #needed only if in windows
            winKeyInterruptHandler()
        else:
            graceful_exit("\nKeyboardInterrupt : Exiting Gracefully..") #exit gracefully
    except Exception as e:
        graceful_exit(f"Oops! {str(e.__class__)} occured.")


if __name__ == "__main__":
    import gecko_installer #custom module
    main()
else:
    from animepahe_dlr import gecko_installer #custom module

    