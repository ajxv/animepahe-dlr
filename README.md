# animepahe-dlr
A python script to automate downloads from animepahe.

## Requirements
- Python3
- FireFox Web browser
- IDM (Internet Download Manager)

## Script dependencies
- Selenium
- BeautifulSoup4

## Setting up the Script
1. Download the [source zip file](https://github.com/ed-archer/animepahe-dlr/archive/refs/heads/main.zip) and extract it.
2. Open cmd and navigate inside the extracted folder.
3. Execute `pip install -r requirements.txt` to install the dependencies.
4. Use `python ap-dlr.py` to execute the script.

## Features
- Search for an anime.
- Select the anime from search results to download all the episodes available under the selected anime.
- Downloads are automatically captured by IDM.

## Notes
- This script is made for Wndows os, if you want to use this in any other os's you may need to edit a few lines of codes.
- Make sure you have python, Firefox and IDM installed before downloading the script.
- This script is a work under progress and therefore may lack some features, please bear with it, and consider contributing to the code if you have any fixes or improvements :relaxed:. 
- The webdriver if found to misbehave if the script is forced to exit using `ctrl^C`. A good solution to this couldn't be found and a temporary fix have been implemented. And as such, please be noted that if you use ctrl^C to exit, your active firefox sessions or tabs have a good chance of crashing. 
- If you encounter `'geckodriver' executable needs to be in PATH.` error; download latest geckodriver from Mozilla's geckodriver [releases](https://github.com/mozilla/geckodriver/releases/), extract the zip file and add the path to the folder containing 'geckodriver.exe' file to windows PATH environment variable. Refer [this](https://docs.microsoft.com/en-us/previous-versions/office/developer/sharepoint-2010/ee537574(v=office.14)) if you are having difficulties adding to PATH variable.
