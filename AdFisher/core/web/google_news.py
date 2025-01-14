import time, re                                                     # time.sleep, re.split
import sys                                                          # some prints
from selenium import webdriver                                      # for running the driver on websites
from datetime import datetime                                       # for tagging log with datetime
from selenium.webdriver.common.keys import Keys                     # to press keys on a webpage
# import browser_unit
from . import google_ads                                                   # interacting with Google ads and Ad Settings
from . import google_search                                                # interacting with Google Search

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

class GoogleNewsUnit(google_ads.GoogleAdsUnit):

    def __init__(self, browser, log_file, unit_id, treatment_id, headless=False, proxy=None):
#         google_search.GoogleSearchUnit.__init__(self, browser, log_file, unit_id, treatment_id, headless, proxy=proxy)
        google_ads.GoogleAdsUnit.__init__(self, browser, log_file, unit_id, treatment_id, headless, proxy=proxy)
#       browser_unit.BrowserUnit.__init__(self, browser, log_file, unit_id, treatment_id, headless, proxy=proxy)
    
    def get_topstories(self):
        """Get top news articles from Google News"""
        self.driver.set_page_load_timeout(60)
        self.driver.get("http://news.google.com")
        tim = str(datetime.now())
#        print "Fetching top news stories"
        topdivs =\
            self.driver.find_elements_by_xpath("""//*[@id="yDmH0d"]/c-wiz/c-wiz/main/div[1]/div[1]/c-wiz/div/c-wiz""")
        print("\n# articles in Top News: ", len(topdivs))
        sys.stdout.write(".")
        sys.stdout.flush()
        for (i, div) in enumerate(topdivs):
            #           print "div", i, "out of", len(topdivs)
            this_topdiv =\
                div.find_element_by_xpath("./c-wiz/div/div[2]/c-wiz[1]")
            title = this_topdiv.find_element_by_xpath("./a").get_attribute('innerHTML')
            ago = this_topdiv.find_element_by_xpath("./div/span[2]/span").get_attribute("innerHTML")
            agency = this_topdiv.find_element_by_xpath("./div/span[1]").get_attribute("innerHTML")
            heading = "Top News"
            #print "Title:", title, ", ago:", ago, ", agency:", agency
            news = strip_tags(tim+"@|"+heading+"@|"+title+"@|"+agency+"@|"+ago).encode("utf8")
            self.log('measurement', 'news', news)
        #print "Done getting top stories"

    def get_allbutsuggested(self):  # Slow execution
        """Get all news articles (except suggested stories) from Google News"""
        self.driver.set_page_load_timeout(60)
        self.driver.get("http://news.google.com")
        tim = str(datetime.now())
        divs = self.driver.find_elements_by_xpath(".//td[@class='lt-col']/div/div/div")
        topdivs = divs[1].find_elements_by_css_selector("div.section-list-content div div.blended-wrapper.blended-wrapper-first.esc-wrapper")
        tds = self.driver.find_elements_by_xpath(".//td[@class='esc-layout-article-cell']")
        print("\n# articles: ", len(tds))
        sys.stdout.write(".")
        sys.stdout.flush()
        for td in tds:
            title = td.find_element_by_xpath(".//div[@class='esc-lead-article-title-wrapper']/h2/a/span").get_attribute('innerHTML')
            tds1 = td.find_elements_by_xpath(".//div[@class='esc-lead-article-source-wrapper']/table/tbody/tr/td")
            agency = tds1[0].find_element_by_xpath(".//span").get_attribute("innerHTML")
            ago = tds1[1].find_element_by_xpath(".//span[@class='al-attribution-timestamp']").get_attribute("innerHTML")
    #       print agency, ago
            body = td.find_element_by_xpath(".//div[@class='esc-lead-snippet-wrapper']").get_attribute('innerHTML')
            heading = "Top News"
            try:
                heading = td.find_element_by_xpath("../../../../../../../../../div[@class='section-header']/div/div/h2/a/span").get_attribute('innerHTML')
            except:
                pass
            if ("Suggested" in heading):
                print("Skipping Suggested news")
                continue
#           print "entering"
            news = strip_tags(tim+"@|"+heading+"@|"+title+"@|"+agency+"@|"+ago+"@|"+body).encode("utf8")
            self.log('measurement', 'news', news)
    
    def get_news(self,type, reloads, delay):
        """Get news articles from Google"""
        rel = 0
        while (rel < reloads):  # number of reloads on sites to capture all ads
            time.sleep(delay)
            try:
                s = datetime.now()
                if(type == 'top'):
                    self.get_topstories()
                elif(type == 'all'):
                    self.get_allbutsuggested()
                else:
                    input("No such news category found: %s!" % site)
                e = datetime.now()
                self.log('measurement', 'loadtime', str(e-s))
            except:
                self.log('error', 'collecting', 'news')
                pass
            rel = rel + 1
    
    def read_articles(self, count=5, agency=None, keyword=None, category=None, time_on_site=20):
        """Click on articles from an agency, or having a certain keyword, or under a category"""
        self.driver.set_page_load_timeout(60)
        self.driver.get("http://news.google.com")
        tim = str(datetime.now())
        i = 0
        for i in range(0, count):
            links = []
            if(agency != None):
                links.extend(self.driver.find_elements_by_xpath(".//div[@class='esc-lead-article-source-wrapper'][contains(.,'"+agency+"')]/.."))
            if(keyword != None):
                links.extend(self.driver.find_elements_by_xpath(".//td[@class='esc-layout-article-cell'][contains(.,'"+keyword+"')]"))
            if(category != None):
                header = self.driver.find_element_by_xpath(".//div[@class='section-header'][contains(.,'"+category+"')]")
                links.extend(header.find_elements_by_xpath("../div/div/div/div/div/table/tbody/tr/td[@class='esc-layout-article-cell']"))
            if(i==0):
                print("# links found:", len(links))
            if(i>=len(links)):
                break
            links[i].find_element_by_xpath("div[@class='esc-lead-article-title-wrapper']/h2/a/span").click()
            sys.stdout.write(".")
            sys.stdout.flush()
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle);
                if not(self.driver.title.strip() == "Google News"):
                    time.sleep(time_on_site)
                    site = self.driver.current_url
                    self.log('treatment', 'read news', site)
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
