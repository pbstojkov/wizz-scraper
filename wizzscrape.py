from datetime import datetime
import dryscrape
import time
import os
from bs4 import BeautifulSoup
import argparse
import ntpath
from pushetta import Pushetta
from matplotlib.dates import DateFormatter
from matplotlib import pyplot as plt


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


def process(in_file_path, save_images, save_html):
    t = datetime.now()

    input_file_name = ntpath.basename(in_file_path)

    print("activated " + input_file_name + " at " + t.strftime("%Y-%m-%d %H:%M") + '\n')

    dates_to_check = list();
    working_dir = os.path.dirname(os.path.abspath(in_file_path))[:-(len("/SettingFiles"))]

    page_path = ""
    with open(in_file_path, "r") as myfile:
        raw_input = myfile.read().split('\n')
        if raw_input[0] == "Wizz discount club":
            wizz_discount = True
            page_path = raw_input[1]
            offset = 2
        else:
            wizz_discount = False
            page_path = raw_input[0]
            offset = 1
        cut_index = page_path.find(".com") + len(".com") + 1
        page_path = page_path[cut_index:]

        for date_param in raw_input[offset:]:
            if len(date_param) > 0:
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

    # set up a web scraping session
    sess = dryscrape.Session(base_url = 'https://wizzair.com/')

    # no cookies pls
    sess.clear_cookies()

    # we don't need images
    sess.set_attribute('auto_load_images', False)

    # visit specified page
    sess.visit(page_path)
    # todo: does this do anything interesting if the page is wrong?

    time.sleep(30)  # making sure that everything is loaded properly. 30sec should be enough.

    if wizz_discount:  # if we want to follow the discounted prices
        print("Yay discounts!")
        discount_button = sess.at_xpath('//*[@class="button button--outlined button--medium button--block"]')
        discount_button.click() 
        time.sleep(2)

    # save a screenshot of the web page
    if save_images == 1:
        f_name = working_dir + "/images/" + input_file_name + t.strftime("_%d_%H") + ".png"
        sess.render(f_name)  # taking the screenshot.

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
        csv_to_graph(f_name)
    except Exception as e: 
        print("ERROR :", str(e))
        print("You can ignore that or change the hardcoded path in csv_to_graph() to a more apropriate place to store graphs.")

    try:
        notification_msg = generate_notif_msg(f_name)
    except Exception as e: 
        print("ERROR :", str(e))
        print("generating notif msg failed somehow.. Is the proper csv file provided?")
        print("csv file :", f_name)
        notification_msg = "You might want to look at the log."

    if save_html == 1:
        f_name = working_dir + "/htmls/" + input_file_name + t.strftime("_%d_%H") + ".html"
        with open(f_name, "w") as myfile:
            myfile.write(hideously_big_str)

    send_notification(working_dir, notification_msg)


def generate_notif_msg(f_name):  # gets the csv file with the results
    msg = ""
    with open(f_name, "r") as myfile:
        raw_input = myfile.read().split('\n')[:-1]  # -1 to ignore the last blank element
        if len(raw_input) < 3:
            return ""  # this is the first run of the script .. there are no previous prices

        raw_dates = raw_input[0].split(',')[1:-1]  # to ignore the first text and the blank element at the end

        current_prices = raw_input[-1].split(',')[1:-1]
        previous_prices = raw_input[-2].split(',')[1:-1]

    if len(current_prices) != len(previous_prices) or len(current_prices) != len(raw_dates):
        raise Exception('Check the input file.. sizes dont match')

    for i in range(0, len(current_prices)):
        if current_prices[i] != previous_prices[i]:
            msg += raw_dates[i] + " changed from " + previous_prices[i] + " to " + current_prices[i] + "\n"

    return msg


def send_notification(working_dir, msg):
    if len(msg) == 0:
        return

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


def csv_to_graph(f_name):
    with open(f_name, "r") as myfile:
        raw_input = myfile.read().split('\n')
        raw_dates = raw_input[0].split(',')[1:-1]  # to ignore the first text and the blank element at the end

        pricesBySample = list()
        samples = list()
        for ri in raw_input[1:-1]:
            pricesBySample.append(ri.split(',')[1:-1])
            samples.append(ri.split(',')[0])

    x = list()
    for sample in samples:
        date_obj = datetime.strptime(sample, '%Y-%m-%d %H:%M')
        x.append(date_obj)

    # style
    plt.style.use('ggplot')

    input_file_name = ntpath.basename(f_name)[:-4]
    # for price in pricesBySample:
    for i in range(0, len(raw_dates)):
        img_name = "/var/www/html/images/" + input_file_name + "_" + raw_dates[i].replace(' ', '_') + ".png"

        y = list()
        for price in pricesBySample:
            y.append(float(price[i]))

        fig, ax = plt.subplots()
        ax.plot_date(x, y, '--o')
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        plt.savefig(img_name, bbox_inches='tight')


def test(in_file_path, bs, bss):
    print("lol.. test function forgotten again huh?")
    # sess = dryscrape.Session(base_url = 'https://wizzair.com/')
    # sess.clear_cookies()

    # dryscrape.start_xvfb()

    # input_file_name = ntpath.basename(in_file_path)
    # working_dir = os.path.dirname(os.path.abspath(in_file_path))[:-(len("/SettingFiles"))]
    # f_name = working_dir + "/results/" + input_file_name[:-3] + ".csv"
    # csv_to_graph(f_name)

    # input_file_name = ntpath.basename(in_file_path)
    # working_dir = os.path.dirname(os.path.abspath(in_file_path))[:-(len("/SettingFiles"))]
    # f_name = working_dir + "/results/" + input_file_name[:-3] + ".csv"
    # try:
    #     notification_msg = generate_notif_msg(f_name)
    # except:
    #     print("generating notif msg failed somehow.. Is the proper csv file provided?")
    #     print("csv file :", f_name)

    # send_notification(working_dir, notification_msg)


def main():
    parser = argparse.ArgumentParser(
        description="This script is intended to be called with three arguments: path to the input .in file, save images? (0/1) and save html? (0/1)")
    parser.add_argument('in_file_path')
    parser.add_argument('save_images')
    parser.add_argument('save_html')
    args = parser.parse_args()

    process(args.in_file_path, args.save_images, args.save_html)
    # test(args.in_file_path, args.save_images, args.save_html)


if __name__ == "__main__":
    main()