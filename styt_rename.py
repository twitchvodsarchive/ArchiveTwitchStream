import streamlink
import subprocess
import requests
import datetime
import time
import os
import enum
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

client_id = config.client_id
client_secret = config.client_secret
TWITCH_CHANNEL = config.username
file_path = "./config.py"
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
refresh = 15
token_url = "https://id.twitch.tv/oauth2/token?client_id=" + client_id + "&client_secret=" \
                         + client_secret + "&grant_type=client_credentials"

class TwitchResponseStatus(enum.Enum):
    ONLINE = 0
    OFFLINE = 1
    NOT_FOUND = 2
    UNAUTHORIZED = 3
    ERROR = 4           

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


def streamedit(driver: WebDriver,
               twitchname,
               dixk,
               ):
            logging.info('start edit the stream name')
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ytcp-button#edit-button"))).click()
            time.sleep(2)
            textbox1 = driver.find_element("xpath", "//ytcp-social-suggestion-input/div[@id='textbox']")
            time.sleep(2)
            textbox1.clear()
            time.sleep(0.5)
            textbox1.send_keys(twitchname)
            time.sleep(0.5)
            textbox2 = driver.find_element("xpath", config.youtubedescription)
            time.sleep(2)
            textbox2.clear()
            time.sleep(0.5)
            textbox2.send_keys(dixk)
            time.sleep(1)
            logging.info('edit finish')
            save_button = driver.find_element(By.XPATH, "//ytcp-button[@id='save-button']")
            save_button.click()
            time.sleep(7)
            return

def selwebdriver():
        url = "https://api.twitch.tv/helix/streams"
        access_token = fetch_access_token()
        info = None
        status = TwitchResponseStatus.ERROR
        try:
            headers = {"Client-ID": client_id, "Authorization": "Bearer " + access_token}
            r = requests.get(url + "?user_login=" + TWITCH_CHANNEL , headers=headers, timeout=15)
            r.raise_for_status()
            info = r.json()
            if info is None or not info["data"]:
                status = TwitchResponseStatus.OFFLINE
            else:
                status = TwitchResponseStatus.ONLINE
        except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    status = TwitchResponseStatus.UNAUTHORIZED
                if e.response.status_code == 404:
                    status = TwitchResponseStatus.NOT_FOUND
        channels = info["data"]
        channel = next(iter(channels), None)
        try:
            titletv = channel.get('title')
            textnoemo = ''.join('[EMOJI]' if unicodedata.category(c) == 'So' else c for c in titletv)
            if "<" in textnoemo or ">" in textnoemo:
                   textnoemo = textnoemo.replace("<", "[ERROR]").replace(">", "[ERROR]")
            filenametwitch = TWITCH_CHANNEL +  " | " + datetime.datetime.now() \
                     .strftime("%Y-%m-%d")
        except AttributeError:
            logging.info('the stream is not live please start at check_styt.py first! try again')
            selwebdriver()
        else:
         deik = "this stream is from twitch.tv/" + TWITCH_CHANNEL + "(Stream Name:" + textnoemo + ")"
         logging.info('process of edit name started')
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
                      streamedit(driver, twitchname=filenametwitch, dixk=deik)
                      
         finally:
            logging.info('edit finished contiue the stream')
        
def check_user():
        url = "https://api.twitch.tv/helix/streams"
        access_token = fetch_access_token()
        info = None
        status = TwitchResponseStatus.ERROR
        try:
            headers = {"Client-ID": client_id, "Authorization": "Bearer " + access_token}
            r = requests.get(url + "?user_login=" + TWITCH_CHANNEL , headers=headers, timeout=15)
            r.raise_for_status()
            info = r.json()
            if info is None or not info["data"]:
                status = TwitchResponseStatus.OFFLINE
            else:
                status = TwitchResponseStatus.ONLINE
        except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    status = TwitchResponseStatus.UNAUTHORIZED
                if e.response.status_code == 404:
                    status = TwitchResponseStatus.NOT_FOUND
        return status, info

def fetch_access_token():
        token_response = requests.post(token_url, timeout=15)
        token_response.raise_for_status()
        token = token_response.json()
        return token["access_token"]

if __name__ == "__main__":
    logging.basicConfig(filename="styt_rename.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info('script is started now')
    selwebdriver()
