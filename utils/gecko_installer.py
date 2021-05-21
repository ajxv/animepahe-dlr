import subprocess
import requests
from bs4 import BeautifulSoup
import platform
import os
from zipfile import ZipFile

def get_gecko_pkg_name():
    #navigate to latest geckodriver release page
    page = requests.get("https://github.com/mozilla/geckodriver/releases/latest")
    pagesoup = BeautifulSoup(page.content, 'html.parser')

    latest_version = "v" + pagesoup.find('h2').text.split()[0] #extract latest version

    current_sys_arch = platform.architecture()[0] 

    #determine the system arch of file to download
    if current_sys_arch == "64bit":
        pkg_arch = "win64"
    elif current_sys_arch == "32bit":
        pkg_arch = "win32"

    gecko_pkg_name = "geckodriver-" + latest_version + "-" + pkg_arch + ".zip"

    return gecko_pkg_name

def create_folder():
    #make a new folder to download to (if one doesn't already exist)
    current_dir = os.path.dirname(__file__)
    new_folder = os.path.join(current_dir, r'geckodriver')
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
    
    return new_folder #path to where the file will be downloaded

def download_zip(download_path, gecko_dl_link, gecko_package_name):
    #download the zip file
    save_as = os.path.join(download_path, gecko_package_name) #save file as

    if not os.path.exists(save_as):
        r = requests.get(gecko_dl_link, stream=True)
        with open(save_as, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
    
    return save_as #path to downloaded zip


def extract_zip(gecko_zip, download_dir):
    #extract zip file
    gecko_exe = os.path.join(download_dir, r"geckodriver.exe")

    if os.path.exists(gecko_exe): #remove file if file already exists
        os.remove(gecko_exe)
    
    with ZipFile(gecko_zip, 'r') as zip:
        zip.extractall(download_dir) #extract content to download_dir

    return gecko_exe

def add_to_PATH(path_of_dir):
    if path_of_dir not in os.environ['PATH']:
        #print("Adding " + path_of_dir + " to $PATH")
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + path_of_dir

def install():
    package_name = get_gecko_pkg_name()
    gecko_dl_link = "https://github.com/mozilla/geckodriver/releases/download/v0.29.1/" + package_name

    download_dir = create_folder()
    
    gecko_zip = download_zip(download_dir, gecko_dl_link, package_name) #download zip file to download_path
    gecko_exe = extract_zip(gecko_zip, download_dir) #extracts downloaded zip

    add_to_PATH(download_dir) #add geckodriver to path