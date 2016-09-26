## Python Wizzair scraper

Get prices for certain flights (semi)automaticly.

## Usage

For now it does 3 things from which one should stay in final version..
+takes a screenshot of the website and stores it in images/
+takes an 'html snapshot' and stores it in htmls/
+parses the html and saves the prices of certain flights in a csv file in results/

This is done twice a day at pseudo random times. The randomness is introduced in delayedActivation.sh

crontab content is shown in crontab.txt

Python version that I am testing with: Python 3.4.2

## Work in progress

A settings file will be created to address all the hardcoded variables such as, flight info.

## Crontab

Cron is used to issue repeated activation of tasks. In our case the .sh file will be executed twice a day at 10:00 and 22:00.

Basically, the last two lines from crontab.txt need to be added using command: crontab -e
