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
        self.driver.implicitly_wait(2)
        self.start_url = ''
        self.instagram_pickle = 'dump/asobi_instagram.pickle'
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_pom_purchase(self):
        try:
            sttime = datetime.datetime.now()
            print "[START] time of {0}".format(sttime.strftime("%Y-%m-%d %H:%M:%S"))
            driver = self.driver
            import pandas as pd
            import random
            df = pd.read_pickle(self.instagram_pickle)
            df['like'] = 0
            cnt = 0
            for i, vi in df.iterrows():
                driver.get(vi["pictureUrl"])
                data = driver.page_source
                html = BeautifulSoup(data)
                like_num = 0
                if html.find("div", attrs= {'class':'_iuf51 _3sst1'}):
                    print(">>動画用クリック")
                    driver.find_element_by_class_name("_9jphp").click()
                    data = driver.page_source
                    html = BeautifulSoup(data)
                    play_div = html.find("div", attrs= {'class':'_iuf51 _3sst1'})
                    like_span = play_div.find("div", attrs= {'class':'_mjnfc'})
                    if not like_span:
                        like_num = len(play_div.find_all("a"))
                elif html.find("div", attrs= {'class':'_iuf51 _oajsw'}):
                    like_div = html.find("div", attrs= {'class':'_iuf51 _oajsw'})
                    like_span = like_div.find("span", attrs= {'class':'_tf9x3'})
                    if not like_span:
                        like_num = len(like_div.find_all("a"))
                else:
                    like_span = None
                if like_num == 0:
                    try:
                        like_text = like_span.span.text.replace(',', '')
                        if like_text.find(u'\u5343') > -1:
                            like_num = int(like_text.replace(u'\u5343', '')) * 1000
                        elif like_text.find(u'\u767e\u4e07') > -1:
                            like_num = int(like_text.replace(u'\u767e\u4e07', '')) * 1000000
                        else:
                            like_num = int(like_text)
                    except Exception as e:
                        print("[ERROR]いいねが取得できませんでした:{0}".format(vi["pictureUrl"]))
                        print(e)
                        print(like_span)
                print("いいね数:{0}".format(like_num))
                df.ix[i, 'like'] = like_num           
                cnt += 1
                if cnt % 10 == 0:
                    print("[INFO]取得数:{0}".format(cnt))
                #time.sleep(0.5+(random.random()/2))
                time.sleep(1)
            entime = datetime.datetime.now()
            print "[CONFIG] time of {0}".format(entime.strftime("%Y-%m-%d %H:%M:%S"))
        finally:
            df.to_pickle('dump/asobi_instagram_like.pickle')
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
