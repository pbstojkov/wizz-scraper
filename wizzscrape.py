from datetime import datetime
import dryscrape
import sys
import time
from bs4 import BeautifulSoup


def main():
    t = datetime.now()
    with open("/home/osmc/code/wizzscrape/activations.txt", "a") as myfile:
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
    # q = sess.at_xpath('//*[@name="q"]')
    # q.set(search_term)
    # q.form().submit()

    # extract all links
    # for link in sess.xpath('//a[@href]'):
    #   print(link['href'])

    # save a screenshot of the web page
    time.sleep(30)

    response = sess.body()
    soup = BeautifulSoup(response)
    f_name = "/home/osmc/code/wizzscrape/htmls/SS_" + t.strftime("%d_%H") + ".html"
    with open(f_name, "a") as myfile:
        myfile.write(str(soup.prettify().encode('utf-8')))

    f_name = "/home/osmc/code/wizzscrape/images/SS_" + t.strftime("%d_%H") + ".png"
    sess.render(f_name)
    print(f_name)


if __name__ == "__main__":
    main()