import time, re                             # time.sleep, re.split
import sys                                  # some prints
import os, platform                         # for running  os, platform specific function calls
from selenium import webdriver              # for running the driver on websites
from datetime import datetime               # for tagging log with datetime
from random import choice

from selenium.webdriver.common.proxy import *       # for proxy settings

class BrowserUnit:

    def __init__(self, browser, log_file, unit_id, treatment_id, headless=False, proxy=None):
        self.headless = headless
        if(headless):
            from xvfbwrapper import Xvfb
            self.vdisplay = Xvfb(width=1280, height=720)
            self.vdisplay.start()
        if(proxy != None):
            sproxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': proxy,
                'ftpProxy': proxy,
                'sslProxy': proxy,
                'noProxy': '' # set this value as desired
                })
        else:
            sproxy = Proxy({
                'proxyType': ProxyType.MANUAL
                })

        if(browser=='firefox'):
            if (platform.system()=='Darwin'):
                self.driver = webdriver.Firefox(proxy=sproxy)
            elif (platform.system()=='Linux'):
                self.driver = webdriver.Firefox(proxy=sproxy)
            else:
                print("Unidentified Platform")
                sys.exit(0)
        elif(browser=='chrome'):
            print("Expecting chromedriver at path specified in core/web/browser_unit")
            if (platform.system()=='Darwin'):
                chromedriver = "../core/web/chromedriver/chromedriver_mac"
            elif (platform.system() == 'Linux'):
                chromedriver = "../core/web/chromedriver/chromedriver_linux"
            else:
                print("Unidentified Platform")
                sys.exit(0)

            # set environment and add options to driver
            os.environ["webdriver.chrome.driver"] = chromedriver
            chrome_option = webdriver.ChromeOptions()
            chrome_option.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_option.add_experimental_option('useAutomationExtension', False)
            chrome_option.add_argument('--disable-blink-features=AutomationControlled')

            if(proxy != None):
                chrome_option.add_argument("--proxy-server="+proxy)

            # initialize driver
            self.driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chrome_option, port = 8080)
        else:
            print("Unsupported Browser")
            sys.exit(0)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.driver.set_page_load_timeout(40)
        self.accept_next_alert = True
        self.log_file = log_file
        self.unit_id = unit_id
        self.treatment_id = treatment_id

    def quit(self):
        if(self.headless):
            self.vdisplay.stop()
        self.driver.quit()

    def wait(self, seconds):
        time.sleep(seconds)

    def log(self, linetype, linename, msg):     # linetype = ['treatment', 'measurement', 'event', 'error', 'meta']
        """Maintains a log of visitations"""
        fo = open(self.log_file, "a")
        fo.write(str(datetime.now())+"||"+linetype+"||"+linename+"||"+str(msg)+"||"+str(self.unit_id)+"||"+str(self.treatment_id) + '\n')
        fo.close()

    def interpret_log_line(self, line):
        """Interprets a line of the log, and returns six components
            For lines containing meta-data, the unit_id and treatment_id is -1
        """
        chunks = re.split("\|\|", line)
        tim = chunks[0]
        linetype = chunks[1]
        linename = chunks[2]
        value = chunks[3].strip()
        if(len(chunks)>5):
            unit_id = chunks[4]
            treatment_id = chunks[5].strip()
        else:
            unit_id = -1
            treatment_id = -1
        return tim, linetype, linename, value, unit_id, treatment_id

    def wait_for_others(self):
        """Makes instance with SELF.UNIT_ID wait while others train"""
        fo = open(self.log_file, "r")
        line = fo.readline()
        tim, linetype, linename, value, unit_id, treatment_id = self.interpret_log_line(line)
        instances = int(value)
        fo.close()

        fo = open(self.log_file, "r")
        for line in fo:
            tim, linetype, linename, value, unit_id, treatment_id = self.interpret_log_line(line)
            if(linename == 'block_id start'):
                round = int(value)
#       print "round, instances: ", round, instances
        fo.close()
        clear = False
        count = 0
        while(not clear):
            time.sleep(5)
            count += 1
            if(count > 500):
                self.log('event', 'wait_for_others timeout', 'breaking out')
                break
            c = [0]*instances
            curr_round = 0
            fo = open(self.log_file, "r")
            for line in fo:
                tim, linetype, linename, value, unit_id, treatment_id = self.interpret_log_line(line)
                if(linename == 'block_id start'):
                    curr_round = int(value)
                if(round == curr_round):
                    if(value=='training-start'):
                        c[int(unit_id)-1] += 1
                    if(value=='training-end'):
                        c[int(unit_id)-1] -= 1
            fo.close()
            clear = True
#           print c
            for i in range(0, instances):
                if(c[i] == 0):
                    clear = clear and True
                else:
                    clear = False


    def scroll_n_log(self, out_path, site):
            # log html source
            html = self.driver.page_source
            f = open(out_path + '/' + site.replace('/', '_') + '.html', 'w')
            f.write(html)
            f.close()

            # scroll through page, screenshot
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            itr = 0
            for y in range(0, page_height, page_height // 4):
                self.driver.execute_script("window.scrollTo(0," + str(y) + ")")
                filename =  site + str(itr) +'.png'
                success = self.driver.save_screenshot(out_path + '/' + filename)
                if success:
                    print("SAVED SCREENSHOT>>>" + filename)

                itr += 1


            # save footer of page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.driver.save_screenshot(out_path + '/' + site + str(itr) + '.png')



    def visit_sites(self, site_file, out_path,treatment='control', delay=5):
        """Visits all pages in site_file"""
        fo = open(site_file, "r")
        print('\n')
        print('@' * 60)
        print("Grab a coffee, Mr.Roboto🤖 will visit sites for you :)")
        print('@' * 60, '\n' * 2)

        # maximize window
        self.driver.maximize_window()


        # log email of account
        self.driver.get('https://mail.google.com/mail/u/0/#inbox')
        email_elem = self.driver.find_element_by_xpath('/html/body/div[7]/div[3]/div/div[1]/div[3]/header/div[2]/div[3]/div[1]/div[2]/div/a/img')
        email_elem.click()
        self.driver.save_screenshot(out_path + '/EMAIL_INFO.png')
        print('LOGGGED EMAIL>>>>>>>>>>')

        for line in fo:
            chunks = re.split("\|\|", line)
            site = "http://"+chunks[0].strip()
            try:
                self.driver.set_page_load_timeout(40)
                self.driver.get(site)
                time.sleep(delay)
                self.log(treatment, 'visit website', site)
                            # pref = get_ad_pref(self.driver)
                            # self.log("pref"+"||"+str(treatment_id)+"||"+"@".join(pref), self.unit_id)
            except:
                self.log('error', 'website timeout', site)

            # save screenshot of visited site
            time.sleep(1)
            # this is really ugly
            site = site[:-4]
            site = site[7:]
            # scroll and extract screenshots
            self.scroll_n_log(out_path, site)

            # simulate browsing activity
            # self.simulate_browse(treatment, out_path)

        # visit last sites with a lot of ads

        # rpgbot
        for i in range(3):
            time.sleep(25)
            self.driver.get('https://rpgbot.net/')
            self.driver.save_screenshot(out_path + '/' + 'rpgads' + str(i) + '.png')
            html = self.driver.page_source
            f = open(out_path + '/' + 'rpgads' + str(i) + '.html', 'w')
            f.write(html)
            f.close()



        # healthline
        self.driver.get('https://www.healthline.com/nutrition/stress-relieving-foods')
        self.driver.save_screenshot(out_path + '/' + 'healthline.png')
        html = self.driver.page_source
        f = open(out_path + '/' + 'healthline' + '.html', 'w')
        f.write(html)
        f.close()



    def simulate_browse(self, treatment, out_path):
        # scroll page, find link and click to simulate real activity
        self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        hrefs = self.driver.find_elements_by_xpath("//a[@href]")
        follow_link = choice(hrefs)
        self.driver.execute_script('arguments[0].scrollIntoView();', follow_link)
        follow_link.click()
        time.sleep(0.5)
        site = self.driver.current_url
        self.log(treatment, 'visit website', site)
        site = site[:-4]
        site = site[7:]
        site.replace('.', '_')
        filename = site + '.png'

        self.driver.save_screenshot(out_path + '/' + filename)

    def collect_sites_from_alexa(self, alexa_link, output_file="sites.txt", num_sites=5):
        """Collects sites from Alexa and stores them in file_name"""
        fo = open(output_file, "w")
        fo.close()
        self.driver.get(alexa_link)
        count = 0
        while(count < num_sites):
            els = self.driver.find_elements_by_css_selector("li.site-listing div.desc-container p.desc-paragraph a")
            for el in els:
                if(count < num_sites):
                    t = el.get_attribute('innerHTML').lower()
                    fo = open(output_file, "a")
                    fo.write(t + '\n')
                    fo.close()
                    count += 1
            self.driver.find_element_by_css_selector("a.next").click()
