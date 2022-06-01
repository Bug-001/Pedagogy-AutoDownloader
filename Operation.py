import json
import logging
import os
import re
import time
import math
from contextlib import closing
from retrying import retry

import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class AutoGet():
    def __init__(self, cid):
        self.current_page = 1
        self.current_file = 1
        self.attachment_url = 'https://teaching.applysquare.com/S/Course/index/cid/' + str(cid) + '#S-Lesson-index'
        while driver.current_url != self.attachment_url:
            driver.get(self.attachment_url)
        pcs = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div[1]/div/div[1]/div[3]/div[2]/div/span'))
        ).text
        self.max_page = math.ceil(int(pcs) / 10)

    @retry
    def Update_page(self):
        while driver.current_url != self.attachment_url:
            driver.get(self.attachment_url)
        for i in range(self.current_page - 1):
            page_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,'/html/body/div[3]/div/div/div/div[2]/div[1]/div/div[1]/div[3]/div[2]/nav/ul/li[last()-1]/a'))
            )
            page_button.click()
            time.sleep(1)

    @retry
    def Choose_attachment(self):
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div[1]/div/div[1]/div[3]/div[1]/table/tbody/tr[{}]/td[7]/a'.format(
                self.current_file)))
        ).click()

    def Source_get(self):
        time.sleep(1)
        src_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
                By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div[1]/div/div[1]/div[2]/div[1]/div[1]/span[@title]")
        )).get_attribute('data-original-title')
        if src_name is not None and src_name.endswith('.mp4'):
            src_url = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
                    By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div[1]/div/div[1]/div[2]/div[3]/div/div/div[1]/video[@src]")
            )).get_attribute('src')
            print(src_name)
            print(src_url)
            return src_url, src_name
        else:
            return None, None


def start_driver():
    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'performance': 'ALL'}
    opt = webdriver.ChromeOptions()
    opt.add_experimental_option('w3c', False)
    opt.add_argument('log-level=3')
    if headless_mode:
        opt.add_argument("--headless")
    driver = webdriver.Chrome(options=opt, desired_capabilities=caps)
    # driver.implicitly_wait(10)
    return driver


def log_in():
    # Login to Pedagogy Square
    login_url = r"https://teaching.applysquare.com/Home/User/login"
    driver.get(login_url)
    time.sleep(1)

    driver.find_element_by_xpath(r"/html/body/div[2]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/input").send_keys(user_name) # Send username
    driver.find_element_by_xpath(r'//*[@id="id_login_password"]').send_keys(user_passwd) # Send password
    driver.find_element_by_xpath(r'//*[@id="id_login_button"]').click() # Submit
    time.sleep(0.5)

    # Dealing with student-teacher selection
    try:
        driver.find_element_by_xpath(r'/html/body/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]/div[1]/i').click() # Choose student
        driver.find_element_by_xpath(r'/html/body/div[2]/div/div[2]/div/div/div[1]/div[4]/a').click() # Submit
    except Exception:
        pass

    time.sleep(0.5)
    if (driver.current_url == r'https://teaching.applysquare.com/S/Index/index'):
        print("Login Successfully!")
    else:
        print("Login Error --- Please check your username & password")
        print("Disable headless mode for detailed information")




if __name__ == "__main__":
    # Load config from config.json
    with open('config.json', 'r') as f:
        config = json.loads(f.read())

    user_name = config.get('username')
    user_passwd = config.get('password')
    headless_mode = config.get('headless_mode')
    download_all_ext = config.get('download_all_ext')
    download_all_courses = config.get('download_all_courses')
    ext_list = config.get('ext_list')
    ext_expel_list = config.get('ext_expel_list')
    cid_list = config.get('cid_list')
    # sleep_time = config.get('sleep_time')

    driver = start_driver()
    log_in()
    father = './大学化学IB/'

    for cid in cid_list:
        ag = AutoGet(cid)
        while ag.current_page <= ag.max_page:
            ag.current_file = 1
            print('The page of {}'.format(ag.current_page))
            try:
                while ag.current_file <= 10:
                    ag.Update_page()
                    ag.Choose_attachment()
                    src_url, src_name = ag.Source_get()
                    ag.current_file += 1
                    if src_url is None:
                        continue
                    # with open(father + src_name, 'wb') as video:
                    #     video.write(requests.get(src_url).content)
            except selenium.common.exceptions.TimeoutException:
                pass
            ag.current_page += 1
    print("DONE!!!")
    driver.quit()


