from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import WebDriverException
import os
from custom_modules import gecko_installer
import platform
import subprocess
import re

this_dir = os.path.dirname(os.path.abspath(__file__)) #path where this script is stored
parent_dir = os.path.dirname(this_dir) #path to parent of current dir
current_system_os = platform.system() #get current os

options = FirefoxOptions()
options.add_argument("--headless")

#firefox-webdriver options
options = FirefoxOptions()
options.add_argument("--headless")

if current_system_os == "Windows": # we need this only in windows
    # get list of currently running firefox processes (for in case -- keyboardInterrupt occurs)
    tasklist = subprocess.check_output(['tasklist', '/fi', 'imagename eq firefox.exe'], shell=True).decode()
    currentFFIDs = re.findall(r"firefox.exe\s+(\d+)", tasklist)

try:
    #initiate driver
    driver = webdriver.Firefox(options=options)

except WebDriverException as driverException:
    if "Message: 'geckodriver' executable needs to be in PATH." in str(driverException) :
        gecko_installer.install(parent_dir) #installs and adds geckodriver to PATH
        driver = webdriver.Firefox(options=options)
    else:
        print(driverException)

#Load add-ons to webdriver
driver.install_addon(parent_dir + os.path.sep + "extensions" + os.path.sep + "universal-bypass.xpi", temporary=True)
driver.install_addon(parent_dir + os.path.sep + "extensions" + os.path.sep + "uBlock0@raymondhill.net.xpi", temporary=True)
