# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from bs4 import BeautifulSoup
import unittest, time, re, datetime, os

class PomPurchaseTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path='./chromedriver')
        #self.driver = webdriver.PhantomJS()
        self.driver.implicitly_wait(30)
        self.start_url = 'http://www.jalan.net/activity/theme/photocontest/201609/'
        self.verificationErrors = []
        self.accept_next_alert = True
        self.pic_dir = 'dump'
    
    def test_pom_purchase(self):
        try:
            sttime = datetime.datetime.now()
            print "[START] time of {0}".format(sttime.strftime("%Y-%m-%d %H:%M:%S"))
            driver = self.driver
            driver.get(self.start_url)
            print "スタートページ:{0}".format(driver.title.encode('utf-8'))
            print "<<Instagramデータ抽出>>"
            time.sleep(2)
            last_len = 0
            miss_cnt = 0
            for i in range(1000):
                try:
                    driver.find_element_by_xpath(".//a[contains(text(), 'more')]").click()
                except Exception as e:
                    print e
                    time.sleep(0.5)
                    miss_cnt += 1
                    if miss_cnt <= 100: 
                        continue
                    else:
                        break
                time.sleep(0.5)
                data = driver.page_source
                html = BeautifulSoup(data)
                contents = html.find_all('li',attrs= {'class':'cardSocialinGadget1'})
                print "画像数:{0}".format(len(contents))
                entime = datetime.datetime.now()
                print "[CONFIG] time of {0}".format(entime.strftime("%Y-%m-%d %H:%M:%S"))
                
            print "<<html抽出>>"
            instagram_data = []
            for ci in contents:
                instagram_record = {}
                if ci.find('span',attrs= {'class':'userNameSocialinGadget1'}):
                    instagram_record["userName"] = ci.find('span',attrs= {'class':'userNameSocialinGadget1'}).text
                else:
                    instagram_record["userName"] = ""
                if ci.find('span',attrs= {'class':'textSocialinGadget1'}):
                    instagram_record["comment"] = ci.find('span',attrs= {'class':'textSocialinGadget1'}).text
                else:
                    instagram_record["comment"] = ""
                instagram_record["pictureUrl"] = ci.find('a',attrs= {'class':'contentsSocialinGadget1'}).get("href")
                if ci.find('span',attrs= {'class':'dateSocialinGadget1'}).a:
                    instagram_record["date"] = ci.find('span',attrs= {'class':'dateSocialinGadget1'}).a.text
                else:
                    instagram_record["date"] = ""
                instagram_data.append(instagram_record)
            entime = datetime.datetime.now()
            print "[CONFIG] time of {0}".format(entime.strftime("%Y-%m-%d %H:%M:%S"))
            import pandas as pd
            df = pd.DataFrame.from_dict(instagram_data)
            df.to_pickle('dump/asobi_instagram.pickle')
        finally:
            time.sleep(1)
            entime = datetime.datetime.now()
            print "[END] time of {0}".format(entime.strftime("%Y-%m-%d %H:%M:%S"))
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
