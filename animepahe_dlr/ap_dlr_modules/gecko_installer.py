import requests
from bs4 import BeautifulSoup
import platform
import os
from zipfile import ZipFile
import shutil

current_os = str(platform.system())

def get_gecko_pkg_name():
    #navigate to latest geckodriver release page
    page = requests.get("https://github.com/mozilla/geckodriver/releases/latest")
    pagesoup = BeautifulSoup(page.content, 'html.parser')

    latest_version = "v" + pagesoup.find('h2').text.split()[0] #extract latest version

    current_sys_arch = platform.architecture()[0] 

    #determine the system arch of file to download
    if current_os.lower() == "windows":
        if current_sys_arch == "64bit":
            pkg_arch = "win64"
        elif current_sys_arch == "32bit":
            pkg_arch = "win32"
        
        extension = "zip"
    
    elif current_os.lower() == "linux":
        if current_sys_arch == "64bit":
            pkg_arch = "linux64"
        elif current_sys_arch == "32bit":
            pkg_arch = "linux32"
        
        extension = "tar.gz"

    gecko_pkg_name = f"geckodriver-{latest_version}-{pkg_arch}.{extension}"

    return gecko_pkg_name

def create_folder(to_location):
    #make a new folder to download to (if one doesn't already exist)
    new_folder = os.path.join(to_location, r'geckodriver')
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
    
    return new_folder #path to where the file will be downloaded

def download_package(download_path, gecko_dl_link, gecko_package_name):
    #download the package
    save_as = os.path.join(download_path, gecko_package_name) #save file as

    if not os.path.exists(save_as):
        r = requests.get(gecko_dl_link, stream=True)
        with open(save_as, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
    
    return save_as #path to downloaded zip


def extract_zip(gecko_zip, geckodriver_dir):
    #extract zip file
    gecko_file = os.path.join(geckodriver_dir, r"geckodriver.exe")

    if os.path.exists(gecko_file): #remove file if file already exists
        os.remove(gecko_file)
    
    with ZipFile(gecko_zip, 'r') as zip:
        zip.extractall(geckodriver_dir) #extract content to geckodriver_dir

    return gecko_file

def extract_tar_gz(gecko_tar_gz, geckodriver_dir):
    #extract *.tar.gz
    gecko_file = os.path.join(geckodriver_dir, r"geckodriver")

    if os.path.exists(gecko_file):
        os.remove(gecko_file)

    shutil.unpack_archive(gecko_tar_gz, geckodriver_dir) #extract *.tar.gz

    return gecko_file

def add_to_PATH(path_of_dir):
    if path_of_dir not in os.environ['PATH']: #add the dir containing geckodriver to PATH
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + path_of_dir

def install(to_location):
    package_name = get_gecko_pkg_name()
    gecko_dl_link = f"https://github.com/mozilla/geckodriver/releases/download/v0.29.1/{package_name}"

    geckodriver_dir = create_folder(to_location)

    gecko_pkg = download_package(geckodriver_dir, gecko_dl_link, package_name) #download zip file to download_path

    if current_os.lower() == "windows":
        gecko_file = extract_zip(gecko_pkg, geckodriver_dir) #extracts downloaded zip
    elif current_os.lower() == "linux":
        gecko_file = extract_tar_gz(gecko_pkg, geckodriver_dir) #extracts downloaded tar.gz file

    add_to_PATH(geckodriver_dir) #add geckodriver to path


install(os.path.dirname(os.path.abspath(__file__)))