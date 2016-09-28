from datetime import datetime
import dryscrape
import sys
import time
import os
from bs4 import BeautifulSoup
import argparse
import ntpath
from pushetta import Pushetta


def find_price_in_html(search_date, hideously_big_str):
    '''
    search_date - string that describes the date that is checked. example : "23 December 2016" - "DD Month YYYY"
    hideously_big_str - the html in string.
    '''
    magic_string = '\\xe2\\x80\\x8e\\xe2\\x82\\xac'
    start_index = hideously_big_str.find(search_date) + len(search_date)
    start_index = hideously_big_str.find(magic_string, start_index) + len(magic_string)
    stop_index = hideously_big_str.find('\\n', start_index)
    price = hideously_big_str[start_index:stop_index]
    if len(price) > 7:  # the price is prooobably not more than 9999.99
        print("Price was bigger than 7 symbols.. assuming there was a bug. ERROR !!! (" + price[:7] + ").")
        return price[:7]
    return price


def process(in_file_path):
    t = datetime.now()

    input_file_name = ntpath.basename(in_file_path)
    dates_to_check = list();
    working_dir = os.path.dirname(os.path.abspath(in_file_path))[:-(len("/SettingFiles"))]

    page_path = ""
    with open(in_file_path, "r") as myfile:
        raw_input = myfile.read().split('\n')
        page_path = raw_input[0]
        cut_index = page_path.find(".com") + len(".com") + 1
        page_path = page_path[cut_index:]

        for date_param in raw_input[1:]:
            dates_to_check.append(date_param)

    if len(page_path) < 1:
        print("Something is wrong with page_path -", page_path)
        exit();

    if not os.path.exists(working_dir + "/results/"):
        os.makedirs(working_dir + "/results/")
    if not os.path.exists(working_dir + "/htmls/"):
        os.makedirs(working_dir + "/htmls/")
    if not os.path.exists(working_dir + "/images/"):
        os.makedirs(working_dir + "/images/")

    f_name = working_dir + "/activations.txt"
    with open(f_name, "a") as myfile:
        myfile.write("activated " + input_file_name + " at " + t.strftime("%Y-%m-%d %H:%M") + '\n')

    if 'linux' in sys.platform:
        # start xvfb in case no X is running. Make sure xvfb 
        # is installed, otherwise this won't work!
        dryscrape.start_xvfb()

    # set up a web scraping session
    sess = dryscrape.Session(base_url = 'https://wizzair.com/')

    # we don't need images
    sess.set_attribute('auto_load_images', False)

    # visit specified page
    sess.visit(page_path)
    # todo: does this do anything interesting if the page is wrong?
    # sess.visit('#/booking/select-flight/EIN/SOF/2016-12-23/2017-01-06/1/0/0')

    time.sleep(30)  # making sure that everything is loaded properly. 30sec should be enough.

    # save a screenshot of the web page
    f_name = working_dir + "/images/SS_" + t.strftime("%d_%H") + ".png"
    sess.render(f_name)  # taking the screenshot.
    print(f_name)

    soup = BeautifulSoup(sess.body())  # there probably is a better way. 
    # bs4 was supposed to be used way smarter than this .. but oh well, whatever works.
    hideously_big_str = str(soup.prettify().encode('utf-8'))

    f_name = working_dir + "/results/" + input_file_name[:-3] + ".csv"
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

    try:
        notification_msg = generate_notif_msg(f_name)
    except:
        print("generating notif msg failed somehow.. Is the proper csv file provided?")
        print("csv file :", f_name)

    f_name = working_dir + "/htmls/SS_" + t.strftime("%d_%H") + ".html"
    with open(f_name, "w") as myfile:
        myfile.write(hideously_big_str)

    send_notification(working_dir, notification_msg)


def generate_notif_msg(f_name):  # gets the csv file with the results
    msg = ""
    with open(f_name, "r") as myfile:
        raw_input = myfile.read().split('\n')
        raw_dates = raw_input[0].split(',')[1:-1]  # to ignore the first text and the blank element at the end

        current_prices = raw_input[-2].split(',')[1:-1]
        previous_prices = raw_input[-3].split(',')[1:-1]

    if len(current_prices) != len(previous_prices) or len(current_prices) != len(raw_dates):
        raise Exception('Check the input file.. sizes dont match')

    for i in range(0, len(current_prices)):
        if current_prices[i] != previous_prices[i]:
            msg += raw_dates[i] + " changed from " + previous_prices[i] + " to " + current_prices[i] + "\n"
    return msg


def send_notification(working_dir, msg):
    f_name = working_dir + "/SettingFiles/pushetta"
    if not os.path.isfile(f_name):  # if such a file doesnt exist
        print("Are you sure you dont want to use pushetta? It is pretty neat.")
        return

    with open(f_name, "r") as myfile:
        raw_input = myfile.read().split('\n')
        API_KEY= raw_input[0]
        CHANNEL_NAME= raw_input[1]

    p=Pushetta(API_KEY)
    p.pushMessage(CHANNEL_NAME, msg)


# def test(in_file_path):
#     input_file_name = ntpath.basename(in_file_path)
#     working_dir = os.path.dirname(os.path.abspath(in_file_path))[:-(len("/SettingFiles"))]
#     f_name = working_dir + "/results/" + input_file_name[:-3] + ".csv"
#     try:
#         notification_msg = generate_notif_msg(f_name)
#     except:
#         print("generating notif msg failed somehow.. Is the proper csv file provided?")
#         print("csv file :", f_name)

#     send_notification(working_dir, notification_msg)


def main():
    parser = argparse.ArgumentParser(
        description="This script is intended to be called with one argument: path to the input .in file.")
    parser.add_argument('in_file_path')
    args = parser.parse_args()

    process(args.in_file_path)
    # test(args.in_file_path)


if __name__ == "__main__":
    main()