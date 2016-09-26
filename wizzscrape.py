from datetime import datetime
import dryscrape
import sys
import time
import os
from bs4 import BeautifulSoup

def find_price_in_html(search_date, hideously_big_str):
    '''
    search_date - string that describes the date that is checked. example : "23 December 2016"
    hideously_big_str - the html in string.
    '''
    magic_string = '\\xe2\\x80\\x8e\\xe2\\x82\\xac'
    start_index = hideously_big_str.find(search_date) + len(search_date)
    start_index = hideously_big_str.find(magic_string, start_index) + len(magic_string)
    stop_index = hideously_big_str.find('\\n', start_index)
    price = hideously_big_str[start_index:stop_index]
    return price

def main():
    t = datetime.now()

    input_file = "Christmas1.in"  # todo: a directory with .in files should be checked and the files inside should be used for input_file's
    dates_to_check = ("22 December 2016",
                      "23 December 2016",
                      "24 December 2016",
                      "5 January 2017",
                      "6 January 2017",
                      "7 January 2017",)  # todo: This should be filled in with data from a .in file later on

    working_dir = os.getcwd()

    if not os.path.exists(working_dir + "/results/"):
        os.makedirs(working_dir + "/results/")
    if not os.path.exists(working_dir + "/htmls/"):
        os.makedirs(working_dir + "/htmls/")
    if not os.path.exists(working_dir + "/images/"):
        os.makedirs(working_dir + "/images/")

    f_name = working_dir + "/activations.txt"
    with open(f_name, "a") as myfile:
        myfile.write("activated at " + t.strftime("%Y-%m-%d %H:%M") + '\n')

    if 'linux' in sys.platform:
        # start xvfb in case no X is running. Make sure xvfb 
        # is installed, otherwise this won't work!
        dryscrape.start_xvfb()

    # set up a web scraping session
    sess = dryscrape.Session(base_url = 'https://wizzair.com/')

    # we don't need images
    sess.set_attribute('auto_load_images', False)

    # visit homepage and search for a term
    sess.visit('#/booking/select-flight/EIN/SOF/2016-12-23/2017-01-06/1/0/0')

    # save a screenshot of the web page
    time.sleep(30)

    response = sess.body()
    soup = BeautifulSoup(response)

    hideously_big_str = str(soup.prettify().encode('utf-8'))

    f_name = working_dir + "/results/" + input_file[:-3] + ".csv"
    if not os.path.isfile(f_name):  # if this is the first entry, fill in the top line 
        with open(f_name, "a") as myfile:
            myfile.write("Date,")
            for date_str in dates_to_check:
                myfile.write(date_str + ",")
            myfile.write("\n")

    with open(f_name, "a") as myfile: # fill in prices for every date in a csv file
        myfile.write(t.strftime("%Y-%m-%d %H:%M") + ",")
        for date_str in dates_to_check:
            price = find_price_in_html(date_str, hideously_big_str)
            myfile.write(price + ",")
        myfile.write("\n")

    f_name = working_dir + "/htmls/SS_" + t.strftime("%d_%H") + ".html"
    with open(f_name, "a") as myfile:
        myfile.write(hideously_big_str)

    f_name = working_dir + "/images/SS_" + t.strftime("%d_%H") + ".png"
    sess.render(f_name)
    print(f_name)


if __name__ == "__main__":
    main()