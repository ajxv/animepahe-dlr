import requests
from bs4 import BeautifulSoup
import os
from clint.textui import progress
from custom_modules.initiate_driver import driver, WebDriverWait, EC, By

def downloader(download_link, location):
    driver.get(download_link)
    #time.sleep(5)
    #wait for elements to load
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//form[@method = 'POST']/button[contains(@class, 'button')]")))


    download_page_source = driver.page_source
    download_page_soup = BeautifulSoup(download_page_source, 'html.parser')

    post_link = download_page_soup.find('form')['action']
    token = download_page_soup.find('input', {'name': '_token'})['value']

    filename = driver.title.replace(" :: Kwik",'')
    file = location + os.path.sep + filename #complete path to file
    
    cookie = str(driver.get_cookie('kwik_session')['value'])

    current_url = driver.current_url #for referer in request header

    header = {
        'Host': 'kwik.cx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
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

    choice = "0"
    if os.path.exists(file):
        print("[#] " + filename)
        while choice.lower() not in ["y", "n"]:
            choice = input("File already exists. Re-download ? (y/n): ")
            if choice.lower() not in ["y", "n"]:
                print("Invalid Choice !")
    
    if choice.lower() == "y" or choice.lower() == "0":

        response = requests.post(post_link, headers=header, data = {'_token': token}, stream=True)

        with open(file, 'wb') as local_file:
            total_length = int(response.headers.get('content-length'))
            for chunk in progress.bar(response.iter_content(chunk_size=1024),label = "[#] " + filename + " ", expected_size=(total_length/1024) + 1):
                if chunk:
                    local_file.write(chunk)
                    local_file.flush()
    else:
        print("Skipping file..")



def download(download_link, location):
    error_counter = 0
    try:
        if error_counter > 6:
            print("Couldn't resolve the issue! Skipping file..")
            return
        downloader(download_link, location)
    except TypeError:
        error_counter += 1
        print("Failed to start download! Retrying..")
        download(download_link, location)
    except Exception as e:
        error_counter += 1
        print(str(e.__class__) + " occured! Retrying..")
        download(download_link, location)