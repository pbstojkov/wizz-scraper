## Python Wizzair scraper

Get prices for certain flights (semi)automaticly.

## Overview

+takes a screenshot of the website and stores it in images/  
+takes an 'html snapshot' and stores it in htmls/  
+parses the html and saves the prices of certain flights in a csv file in results/  
+gets input from .in files in SettingFiles/

This is done twice a day at pseudo random times. The randomness is introduced in delayedActivation.sh

crontab content is shown in crontab.txt

Python version that I am testing with: Python 3.4.2

The screenshot and html snapshot will be removed after a week or so. They are only there for debugging.

## Input files
For every X.in file in SettingFiles/ a separate X.csv file will be created and filled in every time the python script is executed. First line should be the link to the wizzair page you want to check. The next lines should be the dates that you want to record, in the same format that you see them on the website.  
Examples can be found in Examples folder.


## Crontab

Cron is used to issue repeated activation of tasks. In our case the .sh file will be executed twice a day at 10:00 and 22:00.

Basically, the last two lines from crontab.txt need to be added using command: crontab -e
