import time, re                                                     # time.sleep, re.split
import sys                                                          # some prints
from selenium import webdriver                                      # for running the driver on websites
from datetime import datetime                                       # for tagging log with datetime
from selenium.webdriver.common.keys import Keys                     # to press keys on a webpage
from selenium.webdriver.common.action_chains import ActionChains    # to move mouse over
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# import browser_unit
from . import google_search                                                # interacting with Google Search

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request                  # Auth for Google login
import random
import os
import pickle
import webbrowser

from twilio.rest import Client
# strip html

from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class GoogleAdsUnit(google_search.GoogleSearchUnit):

    def __init__(self, browser, log_file, unit_id, treatment_id, headless=False, proxy=None):
        google_search.GoogleSearchUnit.__init__(self, browser, log_file, unit_id, treatment_id, headless, proxy=proxy)
#         browser_unit.BrowserUnit.__init__(self, browser, log_file, unit_id, treatment_id, headless, proxy=proxy)

    def collect_ads(self, reloads, delay, site, file_name=None):
        if file_name == None:
            file_name = self.log_file
        rel = 0
        while (rel < reloads):  # number of reloads on sites to capture all ads
            time.sleep(delay)
            try:
                s = datetime.now()
                if(site == 'toi'):
                    self.save_ads_toi(file_name)
                elif(site == 'bbc'):
                    self.save_ads_bbc(file_name)
                elif(site == 'monster'):
                    self.save_ads_monster(file_name)
                else:
                    input("No such site found: %s!" % site)
                e = datetime.now()
                self.log('measurement', 'loadtime', str(e-s))
            except:
                self.log('error', 'collecting ads', 'Error')
            rel = rel + 1

    def save_ads_toi(self, file):
        driver = self.driver
        id = self.unit_id
        sys.stdout.write(".")
        sys.stdout.flush()
        driver.set_page_load_timeout(60)
        driver.get("http://timesofindia.indiatimes.com/international-home")
        time.sleep(10)
        driver.execute_script('window.stop()')
        tim = str(datetime.now())
        frame = driver.find_element_by_xpath(".//iframe[@id='ad-left-timeswidget']")

        def scroll_element_into_view(driver, element):
            """Scroll element into view"""
            y = element.location['y']
            driver.execute_script('window.scrollTo(0, {0})'.format(y))

        scroll_element_into_view(driver, frame)
        driver.switch_to.frame(frame)
        ads = driver.find_elements_by_css_selector("html body table tbody tr td table")
        for ad in ads:
            aa = ad.find_elements_by_xpath(".//tbody/tr/td/a")
            bb = ad.find_elements_by_xpath(".//tbody/tr/td/span")
            t = aa[0].get_attribute('innerHTML')
            l = aa[1].get_attribute('innerHTML')
            b = bb[0].get_attribute('innerHTML')
            ad = strip_tags(tim+"@|"+t+"@|"+l+"@|"+b).encode("utf8")
            self.log('measurement', 'ad', ad)
        driver.switch_to.default_content()

    def save_ads_bbc(self, file):
        driver = self.driver
        id = self.unit_id
        sys.stdout.write(".")
        sys.stdout.flush()
        driver.set_page_load_timeout(60)
        driver.get("http://www.bbc.com/news/")
        tim = str(datetime.now())
        els = driver.find_elements_by_css_selector("div.bbccom_adsense_container ul li")
        for el in els:
            t = el.find_element_by_css_selector("h4 a").get_attribute('innerHTML')
            ps = el.find_elements_by_css_selector("p")
            b = ps[0].get_attribute('innerHTML')
            l = ps[1].find_element_by_css_selector("a").get_attribute('innerHTML')
            ad = strip_tags(tim+"@|"+t+"@|"+l+"@|"+b).encode("utf8")
            self.log('measurement', 'ad', ad)


    def save_ads_monster(self, file):
        driver = self.driver
        id = self.unit_id
        sys.stdout.write(".")
        sys.stdout.flush()
        driver.set_page_load_timeout(60)
        driver.get("http://jobsearch.monster.com/")
        tim = str(datetime.now())
        els = driver.find_elements_by_css_selector("div.ctlJobListEntry")
        for el in els:
            title = el.find_element_by_class_name('wdgJobTitle').get_attribute('innerHTML').strip()
            company = el.find_element_by_class_name('wdgJobCompany').get_attribute('innerHTML').strip()
            location = el.find_element_by_css_selector('div.jobPlace a').get_attribute('innerHTML').strip()
            ad = strip_tags(tim+"@|"+title+"@|"+company+"@|"+location).encode("utf8")
            self.log('measurement', 'ad', ad)


    def opt_in(self):
        driver = self.driver
        id = self.unit_id
        driver.set_page_load_timeout(60)
        driver.get()

    def create_account(self):
        driver = self.driver
        id = self.unit_id
        sys.stdout.write(".")
        sys.stdout.flush()
        driver.set_page_load_timeout(200)

        # log into Google via StackOverflow
        driver.get("https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp")

        print("$" * 50)
        print('PLEASE CREATE A GOOGLE ACCOUNT MANUALLY')
        print("$" * 50, '\n')
        while True:
            if driver.current_url.startswith('https://accounts.google.com/signup/v2/webgradsidvphone'):
                break
        print("Phone Verification Started!")
        print("Use your phone nubmer until you get banned...I dunno")

        # open ad preferences for account
        time.sleep(60)

        driver.get('https://accounts.google.com/signin/v2/identifier?passive=1209600&continue=https%3A%2F%2Fadssettings.google.com%2Fauthenticated%3Fhl%3Den&followup=https%3A%2F%2Fadssettings.google.com%2Fauthenticated%3Fhl%3Den&hl=en&flowName=GlifWebSignIn&flowEntry=ServiceLogin')

        print('<<<<<<<Select the ad settings relevant to the account you created>>>>>>>', '\n')



