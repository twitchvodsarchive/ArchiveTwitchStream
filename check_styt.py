import streamlink
import subprocess
import requests
import datetime
import time
import os
import getopt
import logging
import re
import sys
import json
import unicodedata
import shutil
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.file_detector import LocalFileDetector
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
import config

TWITCH_CHANNEL = config.username
file_path = "./config.py"
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
fuckingbitch = config.streamfromyt       

def confirm_logged_in(driver: webdriver) -> bool:
          """ Confirm that the user is logged in. The browser needs to be navigated to a YouTube page. """
          try:
              WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "avatar-btn")))
              return True
          except:
              logging.info(f"cant login please renter the config.json with the cookie information")
              exit()

def login_using_cookie_file(driver: webdriver, cookie_file: str):
          """Restore auth cookies from a file. Does not guarantee that the user is logged in afterwards.
          Visits the domains specified in the cookies to set them, the previous page is not restored."""
          domain_cookies: Dict[str, List[object]] = {}
          with open(cookie_file) as file:
              cookies: List = json.load(file)
              # Sort cookies by domain, because we need to visit to domain to add cookies
          for cookie in cookies:
              try:
               domain_cookies[cookie["domain"]].append(cookie)
              except KeyError:
               domain_cookies[cookie["domain"]] = [cookie]

          for domain, cookies in domain_cookies.items():
              driver.get("https://www.youtube.com/")
              for cookie in cookies:
                  cookie.pop("sameSite", None)  # Attribute should be available in Selenium >4
                  cookie.pop("storeId", None)  # Firefox container attribute
                  try:
                      driver.add_cookie(cookie)
                  except:
                      logging.info(f"Couldn't set cookie {cookie['name']} for {domain}")

def selfromstream():
         refresh = 15
         username = config.username
         quality = "best"
         logging.info(f"checking for %s every %s seconds, recording with %s quality",
                     username, refresh, quality)
         logging.info('process of edit name started from stream')
         driver = webdriver.Chrome()
         login_using_cookie_file(driver, cookie_file = 'config.json')
         driver.get("https://www.youtube.com")
         
         assert "YouTube" in driver.title
         
         try:
                      confirm_logged_in(driver)
                      url_to_live = "https://studio.youtube.com/channel/" + config.channelid + "/livestreaming/dashboard"
                      driver.get(url_to_live)
                      time.sleep(20)
                      AbcS = config.youtubestudiotab
                      assert AbcS in driver.title
                      driver.file_detector = LocalFileDetector()
                      logging.info("waiting someone to stream first")
                      loop_check(driver)
                      
         finally:
            logging.info('edit finished contiue the stream')

def streamedit(driver):
            logging.info('checking stream')
            try:
              element = driver.find_element("xpath", "//div[@id='text' and contains(@class, 'instructions') and contains(@class, 'style-scope') and contains(@class, 'ytls-ingestion-prompt-renderer')]")
              elxt = element.text
              if config.youtubeoffine not in elxt:
                logging.info("finish bitxh")
              if config.youtubeoffine in elxt:
                logging.info('The stream is messed up. Trying again...')
                os.system('TASKKILL /f /im imskbidi.exe')
                os.system('start styt.py')
                time.sleep(25)
                streamedit(driver)
            except NoSuchElementException:
              logging.info("idk finish")

def loop_check(driver):
        try:
                url = "https://youtube.com/channel/" + config.username + "/live"
                streams = streamlink.streams(url)
                hls_stream = streams["best"]
                # start streamlink process
                os.system('start styt.py')
                os.system('start styt_rename.py')
                os.system('start check_styt_offine.py')
                logging.info("wait for repeat exit now...")
                streamedit(driver)
        except KeyError:
            time.sleep(9)
            loop_check(driver)

if __name__ == "__main__":
    logging.basicConfig(filename="check_styt.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().addHandler(logging.StreamHandler())
    sys.setrecursionlimit(81000)
    logging.info(sys.getrecursionlimit())
    selfromstream()
