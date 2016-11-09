# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from bs4 import BeautifulSoup
import unittest, time, re, datetime, os, urllib2

class PomPurchaseTest(unittest.TestCase):
    def setUp(self):
        #self.driver = webdriver.Chrome(executable_path='./chromedriver')
        self.driver = webdriver.PhantomJS()
        self.driver.implicitly_wait(2)
        self.start_url = ''
        self.picture_dic = 'picture'
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
            df['picture_filename'] = ''
            cnt = 0
            for i, vi in df.iterrows():
                driver.get(vi["pictureUrl"])
                data = driver.page_source
                html = BeautifulSoup(data)
                like_num = 0
                picture_filename = ''
                # 動画対応 
                if html.find("div", attrs= {'class':'_iuf51 _3sst1'}):
                    # 動画から画像を抽出
                    picture_url = html.find('video').attrs['poster']
                    picture_filename = download_picture(picture_url, self.picture_dic)
                    # いいね取得のため遷移
                    print(">>動画用クリック")
                    driver.find_element_by_class_name("_9jphp").click()
                    data = driver.page_source
                    html = BeautifulSoup(data)
                    play_div = html.find("div", attrs= {'class':'_iuf51 _3sst1'})
                    like_span = play_div.find("div", attrs= {'class':'_mjnfc'})
                    if not like_span:
                        like_num = len(play_div.find_all("a"))
                # 画像対応
                elif html.find("div", attrs= {'class':'_iuf51 _oajsw'}):
                    # 画像URL抽出
                    picture_url = html.find_all('img')[1].attrs['src']
                    picture_filename = download_picture(picture_url, self.picture_dic)
                    # いいね取得
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
                df.ix[i, 'picture_filename'] = picture_filename
                cnt += 1
                if cnt % 10 == 0:
                    print("[INFO]取得数:{0}".format(cnt))
                time.sleep(0.5+(random.random()/2))
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

# url先の画像を保存する関数
def download_picture(url, picture_dir):
    img = urllib2.urlopen(url)
    filename = os.path.basename(url).split('?')[0]
    localfile = open(os.path.join(picture_dir, filename), 'wb')
    localfile.write(img.read())
    img.close()
    localfile.close()
    return filename
    

if __name__ == "__main__":
    unittest.main()
