# animepahe-dlr
A python script to automate downloads from animepahe.

## Requirements
- Python3
- FireFox Web browser
- IDM (Internet Download Manager)

## Script dependencies
- Selenium
- BeautifulSoup4
- requests

## Setting up the Script
1. Download the [source zip file] and extract it.
2. Open cmd and navigate inside the extracted folder.
3. Execute `pip install -r requirements.txt` to install the dependencies.
4. Use `python ap-dlr.py` to execute the script.

## Features
- Search for an anime.
- Select the anime from search results to download all the episodes available under the selected anime.
- Downloads are automatically captured by IDM.
- **Downloading and Quality :**
  - Downloads are set to be automatically captured by IDM. (so make sure IDM is installed)
  - Currently the download quality priority is as follows : [720p, 576p, 480p]
    - ie, downloader first checks for 720p video, if 720p is not available checks for 576p and so on.
    - If you want to download anime in 1080p, open up 'ap-dlr.py' in any editor and add 1080p to the begining of the list defined using 'quality' variable in the code. 

## Notes
- Make sure you have python, Firefox and IDM installed before downloading the script.
- This script is a work under progress and therefore may lack some features, please bear with it, and consider contributing to the code if you have any fixes or improvements :relaxed:. 
- **In Windows** the webdriver if found to misbehave if the script is forced to exit using `ctrl^c`. A good solution to this couldn't be found and a temporary fix have been implemented. And as such, please be noted that if you use ctrl^c to exit, your active firefox sessions or tabs have a good chance of crashing. (Note: ctrl^c doesn't have any issues in Linux)
