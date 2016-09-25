## Python Wizzair scraper

Get prices for certain flights (semi)automaticly.

## Usage

For now it is just taking screenshots for a hardcoded flight twice a day at "random" times and stores them in .. a hardcoded path folder.
+ 'html snapshot' is saved in folder /htmls along with the screenshot. For further parsing.

The randomness is introduced in delayedActivation.sh

crontab content in crontab.txt

Python version used is Python 3.4.2

## Work in progress

A settings file will be created to address all the hardcoded variables such as, flight info and various paths
The prices will be kept in a cleaner, more readable way. Probably in a CSV file.

## Crontab

Cron is used to issue repeated activation of tasks. In our case the .sh file will be executed twice a day at 10:00 and 22:00.

Basically, the last two lines from crontab.txt need to be added using command: crontab -e
