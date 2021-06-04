from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import WebDriverException
import os
from ap_dlr_modules import gecko_installer
import platform
import subprocess
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

this_dir = os.path.dirname(os.path.abspath(__file__)) #path where this script is stored
parent_dir = os.path.dirname(this_dir) #path to parent of current dir
current_system_os = str(platform.system()) #get current os

#add geckodriver path to PATH
geckodriver_path = os.path.join(this_dir, "geckodriver")
if current_system_os.lower() == "windows":
    if os.path.exists(os.path.join(geckodriver_path, r"geckodriver.exe")):
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + geckodriver_path
if current_system_os.lower() == "linux":
    if os.path.exists(os.path.join(geckodriver_path, r"geckodriver")):
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + geckodriver_path

log_file = os.path.join(geckodriver_path, 'geckodriver.log')
#firefox-webdriver options
options = FirefoxOptions()
options.add_argument("--headless")

if current_system_os.lower() == "windows": # we need this only in windows
    # get list of currently running firefox processes (for in case -- keyboardInterrupt occurs)
    tasklist = subprocess.check_output(['tasklist', '/fi', 'imagename eq firefox.exe'], shell=True).decode()
    currentFFIDs = re.findall(r"firefox.exe\s+(\d+)", tasklist)

try:
    #initiate driver
    driver = webdriver.Firefox(options=options, service_log_path=log_file)

except WebDriverException as driverException:
    if "Message: 'geckodriver' executable needs to be in PATH." in str(driverException) :
        gecko_installer.install(this_dir) #installs and adds geckodriver to PATH
        driver = webdriver.Firefox(options=options, service_log_path=geckodriver_path)
    else:
        print(driverException)

#Load add-ons to webdriver
driver.install_addon(parent_dir + os.path.sep + "driver_extensions" + os.path.sep + "universal-bypass.xpi", temporary=True)
driver.install_addon(parent_dir + os.path.sep + "driver_extensions" + os.path.sep + "uBlock0@raymondhill.net.xpi", temporary=True)
