# animepahe-dlr
A python script to automate downloads from animepahe.

## Requirements
- Python3
- FireFox Web browser
- IDM (Internet Download Manager) (Optional)

## Script dependencies
- Selenium
- BeautifulSoup4
- requests
- clint

## Setting up the Script
1. Download the [source zip file] and extract it.
2. Open cmd and navigate inside the extracted folder.
3. Execute `pip install -r requirements.txt` to install the dependencies.
4. Use `python3 ap-dlr.py` to execute the script.

## Usage
- To execute the script, use `pyhton3 ap-dlr.py`
- To use idm to capture downloads, execute script using '-idm' argument : `python3 ap-dlr.py -idm`

## Features
- Search for an anime.
- Select anime from search result.
- Select episodes to download.
- Downloads are made using inbuilt-dlr.
- **Downloading and Quality :**
  - Downloads are taken care of by the inbuilt downloader on default.
  - Currently the download quality priority is as follows : [720p, 576p, 480p]
    - ie, downloader first checks for 720p video, if 720p is not available checks for 576p and so on.
    - If you want to download anime in 1080p, open up 'ap-dlr.py' in any editor and add 1080p to the begining of the list defined using 'quality' variable in the code. 

## Notes
- Make sure you have python, Firefox (and IDM (optional), if you want idm to capture downlads) installed before downloading the script.
- This script is a work under progress and therefore may lack some features, please bear with it, and consider contributing to the code if you have any fixes or improvements :relaxed:. 
- **In Windows** the webdriver if found to misbehave if the script is forced to exit using `ctrl^c`. A good solution to this couldn't be found and a temporary fix have been implemented. And as such, please be noted that if you use ctrl^c to exit, your active firefox sessions or tabs have a good chance of crashing. (Note: ctrl^c doesn't have any issues in Linux)
