import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import time
from clint.textui import progress

dl_link = "https://fumacrom.com/UYfV"
script_dir = "D:\\WorkSpace\\animepahe-dlr"


#add geckodriver path to PATH
geckodriver_path = os.path.join(script_dir, "geckodriver")
if os.path.exists(os.path.join(geckodriver_path, r"geckodriver.exe")):
    os.environ['PATH'] = os.environ['PATH'] + os.pathsep + geckodriver_path



driver = webdriver.Firefox()
driver.install_addon(script_dir + os.path.sep + "extensions" + os.path.sep + "universal-bypass.xpi", temporary=True)
driver.install_addon(script_dir + os.path.sep + "extensions" + os.path.sep + "uBlock0@raymondhill.net.xpi", temporary=True)

driver.get(dl_link)
time.sleep(3)
driver.switch_to.window(driver.window_handles[1]) #switch-to add-on confirmation tab
driver.close() #close active tab
time.sleep(1)
driver.switch_to.window(driver.window_handles[0])
dl_page = driver.page_source

filename = script_dir + os.path.sep + driver.title.replace(" :: Kwik",'')

cookie = "cf_clearance=5bccdfce967dac708ad88a921f2fa4c611dab4a1-1621779043-0-250; __cfduid=dea2a5db62313b8e6304deccf7ae9da841619857420; SERVERID=lux; kwik_session=" + str(driver.get_cookie('kwik_session')['value'])

current_url = driver.current_url
print("-----------------------------------------------------------------------------------------------------")
print(cookie)
print("-----------------------------------------------------------------------------------------------------")


dl_page_soup = BeautifulSoup(dl_page, 'html.parser')
post_link = dl_page_soup.find('form')['action']

print(post_link)
print(dl_page_soup.find('input', {'name': '_token'}))

token = dl_page_soup.find('input', {'name': '_token'})['value']

print("-----------------------------------------------------------------------------------------------------")
print(token)
print("-----------------------------------------------------------------------------------------------------")


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
    'Cookie': cookie,
    'Upgrade-Insecure-Requests': '1'
}

resp = requests.post(post_link, headers=header, data = {'_token': token}, stream=True)
""" #dl-fn-1
with open(filename, 'wb') as target:
    resp.raw.decode_content = True
    shutil.copyfileobj(resp.raw, target)
"""

with open(filename, 'wb') as local_file:
    total_length = int(resp.headers.get('content-length'))
    for chunk in progress.bar(resp.iter_content(chunk_size=2048), expected_size=(total_length/1024) + 1):
        if chunk:
            local_file.write(chunk)
            local_file.flush()

print("-----------------------------------------------------------------------------------------------------")
print("status: " + str(resp.status_code))
print("-----------------------------------------------------------------------------------------------------")
print(resp.headers)
