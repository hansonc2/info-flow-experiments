import time, re                                                     # time.sleep, re.split
import sys                                                          # some prints
from selenium import webdriver                                      # for running the driver on websites
from datetime import datetime                                       # for tagging log with datetime
from selenium.webdriver.common.keys import Keys                     # to press keys on a webpage
from selenium.webdriver.common.action_chains import ActionChains    # to move mouse over
# import browser_unit
from . import google_search                                         # interacting with Google Search
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request                  # Auth for Google login
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


    def login(self, googleID, pswd):
        try:
            driver = self.driver
            id = self.unit_id
            sys.stdout.write(".")
            sys.stdout.flush()
            driver.set_page_load_timeout(6000)

            # log into Google via StackOverflow
            driver.get("https://stackoverflow.com/users/login")
            google_sign_in_path = '//*[@id="openid-buttons"]/button[1]'
            google_button = driver.find_elements_by_xpath(google_sign_in_path)
            time.sleep(1.5)
            google_button[0].click()
            driver.implicitly_wait(200)
            time.sleep(2)

            # input username
            email_path = '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input'
            email_box = driver.find_element_by_xpath(email_path)
            email_box.click()
            time.sleep(1.5)
            email_box.send_keys(googleID)
            times.sleep(0.1)
            email_box.send_keys(Keys.ENTER)
            driver.implicitly_wait(200)
            time.sleep(1)

            # input password
            pass_path = '//*[@id="password"]/div[1]/div/div[1]/input'
            with open('google_login_page.html', 'w') as f:
                f.write(str(driver.page_source.encode("utf-8")))
            password_box = driver.find_element_by_xpath(pass_path)
            password_box.click()
            time.sleep(0.7)
            pass_path[0].send_keys(pswd)
            time.sleep(0.2)
            pass_path[0].send_keys(Keys.ENTER)

            #success
            print('Logged in as' + googleID)

        except Exception as e:
            print('$$$' + str(e) + '$$$')
            print('Login Failed')


    def sign_in(self, usr, pswd):
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)

        # Call the Gmail API
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                print(label['name'])



