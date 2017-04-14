#!/usr/bin/python3
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
import hashlib
import json
import logging
import logging.config
import operator
import os
import pickle
import platform
import pprint
import requests
import threading
import time
import urllib
import urllib.request

# # # # # # # # # # # # # # # # # # # # # 
# logging basic configure
# 
# print information 
#   -- logging.debug('logger debug message')     
#   -- logging.info('logger info message')
#   -- logging.warning('logger warning message')
#   -- logging.error('logger error message')
#   -- logging.critical('logger critical message')
#     
# create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
#
# create formatter
formatter = logging.Formatter(
        fmt = "[%(asctime)s %(threadName)s:%(thread)2d no:%(lineno)3d] [%(levelname)s] %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S"
    )
#
# create console handler and set level to INFO
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
#
# add ch to logger
logger.addHandler(ch) 
#
# # # # # # # # # # # # # # # # # # # # # 


# # # # # # # # # # # # # # # # # # # # # 
# Global variables for multiple threads
# 
# Global Task Queue
GLOBAL_TASK_QUEUE = list()
# Global Task Queue Lock
GLOBAL_TASK_QUEUE_LOCK = threading.Lock()
# Global Error Queue
GLOBAL_ERROR_QUEUE = list()
# Global Error Queue Lock
GLOBAL_ERROR_QUEUE_LOCK = threading.Lock()
# Global Result Queue
GLOBAL_RESULT_QUEUE = list()
# Global Error Queue Lock
GLOBAL_RESULT_QUEUE_LOCK = threading.Lock()
# Maximum number of threads
GLOBAL_THREADS_MAXNUM = 0
# Share cookies with all threads
GLOBAL_COOKIES_LOCK = threading.Lock()
#
# # # # # # # # # # # # # # # # # # # # # 


class Mode(object):
    """
    Set of supported modes.
    """
    DEBUG = "debug"
    DEVELOP = "develop"
    PRODUCTION = "production"


class Basic (threading.Thread) :
    def __init__(self, mode = Mode.DEVELOP) :
        threading.Thread.__init__(self)

        # driver
        system = platform.system()
        if operator.eq(mode, Mode.PRODUCTION):
            # Production
            if operator.eq(system, "Windows"):
                self.driver = webdriver.PhantomJS(
                        executable_path = "./libs/phantomjs-2.1.1-windows/bin/phantomjs.exe",
                        service_log_path = os.path.devnull,
                    ) # Windows
            else:
                self.driver = webdriver.PhantomJS(
                        executable_path = "./libs/phantomjs-2.1.1-linux-x86_64/bin/phantomjs",
                        service_log_path = os.path.devnull
                    ) # Linux amd64
            self.driver.set_window_position(0, 0)
            self.driver.set_window_size(4096, 4096)
            self.driver.set_page_load_timeout(300)
            self.driver.set_script_timeout(300)
            # self.driver.implicitly_wait(300)
        else :
            # Debug & Develop
            if operator.eq(system, "Windows"):
                # windows - debug
                # IE 问题太多， 暂时换成 Chrome
                # self.driver = webdriver.Ie() 
                self.driver = webdriver.Chrome(
                        service_log_path = os.path.devnull
                    ) # Windows IE
            else:
                self.driver = webdriver.Chrome(
                        service_log_path = os.path.devnull
                    ) # Linux Chrome
            self.driver.maximize_window()

    def run(self) :
        logger.info("thread start to run ")
        global GLOBAL_COOKIES_LOCK

        # login - alimama
        GLOBAL_COOKIES_LOCK.acquire()
        while True :
            if os.path.isfile('alimama.cookies') :
                cookies_file = open('alimama.cookies', 'rb')
                cookies = pickle.loads(cookies_file.read())
                cookies_file.close()
                for cookie in cookies :
                    try : self.driver.add_cookie(cookie);
                    except : pass;

                if self.check_login_status() :
                    break

            if self.auto_login() :
                break
            if self.manul_login() :
                break

        cookies = self.driver.get_cookies()
        cookies_file = open('alimama.cookies', 'wb')
        cookies_file.write(pickle.dumps(cookies))
        cookies_file.close()
        GLOBAL_COOKIES_LOCK.release()

        while True:
            global GLOBAL_TASK_QUEUE
            global GLOBAL_TASK_QUEUE_LOCK

            GLOBAL_TASK_QUEUE_LOCK.acquire()
            
            is_queue_empty = True
            if len(GLOBAL_TASK_QUEUE) > 0 :
                task = GLOBAL_TASK_QUEUE.pop()
                is_queue_empty = False

            GLOBAL_TASK_QUEUE_LOCK.release()

            if not is_queue_empty :
                self.behavior(task)
            else :
                break

        # logout alimama
        # 所有线程共享cookies，不进行登出
        # self.logout()

        # close driver
        self.driver.close() 
        
        logger.info("thread end ")

    def behavior(self, task) :
        """
        Called before running. This method may be overridden
        to define custom behavior.
        """
        pass

    def _send_keys(self, element_selector, keys, is_clear = False) :
        element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(element_selector)
            )
        
        if is_clear :
            element.clear()

        for item in keys :
            element.send_keys(item)
            time.sleep(0.1)

    def _click(self, element_selector, after_click_sleep_time = 1) :
        element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(element_selector)
            )
        element.click()
        time.sleep(after_click_sleep_time)

    def _driver_remove_popup_1(self):
        """
        Clear popup box or unuseful guide

        suitable for following sites:
          -- http://pub.alimama.com/promo/item/channel/index.htm?q=*
        """

        driver = self.driver
        try :
            # -- click guide box
            element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        "#dxjhGuide span.close-btn"
                    ))
                )
            element.click()
        except :
            # -- click guide box
            try : driver.execute_script("$('#dxjhGuide span.close-btn').click()"); 
            except : pass;
        finally :
            # -- hide anyhelp box
            try : driver.execute_script("$('div.aw-dialog-wrapper.samll iframe.aw-dialog').hide()");
            except : pass;
            # -- hide selection bar
            try : driver.execute_script("$('div#J_selection_bar').hide()"); 
            except : pass;

    def _driver_remove_popup_2(self) :
        """
        Clear popup box or unuseful guide

        suitable for following sites:
          -- http://pub.alimama.com/myunion.htm
        """
       
        driver = self.driver
        try :
            # -- click guide box
            element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        "div[bx-tmpl='head-guide'] > div > span.close-btn"
                    ))
                )
            element.click()
        except :
            # -- hide guide box
            try : driver.execute_script("$('div[bx-tmpl='head-guide']').hide()"); 
            except : pass;

        try :
            # -- click guide box
            element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        "body > div.dialog-overlay.dialog-ext-position.dialog.dialog-down.dialog-overlay-shown > a"
                    ))
                )
            element.click()
        except :
            # -- hide guide box
            try : driver.execute_script("$('body > div.dialog-overlay.dialog-ext-position.dialog.dialog-down.dialog-overlay-shown').hide()"); 
            except : pass;

    def check_login_status(self) :
        logger.info("checking login status")
        driver = self.driver

        url = "http://pub.alimama.com/common/getUnionPubContextInfo.json"
        try:
            driver.get(url)
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body>pre"))
            )

            info = json.loads(element.text)
            info["data"]["memberid"]
            
            logger.info("login status ok ")
            return True

        except (KeyError, TypeError) as e:
            logger.info("login status false")
        except Exception as e:
            logger.error("%s" % (str(e)))
  
        return False
    
    def manul_login(self) :
        logger.info("manul login start")
        
        try :
            system = platform.system()
            if operator.eq(system, "Windows") :
                # windows - debug
                # IE 问题太多， 暂时换成 Chrome
                # driver = webdriver.Ie() # Windows IE
                driver = webdriver.Chrome(
                        service_log_path = os.path.devnull
                    )
            else : 
                driver = webdriver.Chrome(
                        service_log_path = os.path.devnull
                    ) # Linux Chrome
            
            driver.get("https://login.taobao.com/member/login.jhtml?style=mini&from=alimama")
            
            input("waiting for user to manully login, (do not close browser manully) \n please press enter key after login succeed ")

            cookies = driver.get_cookies()
        except :
            return False
        finally :
            try: driver.close();
            except: pass;

        # logger.info("manul login cookies: %s" % (json.dumps(cookies)))
        logger.info("add cookies to console driver")

        # self.driver.delete_all_cookies()
        for cookie in cookies :
            try :
                self.driver.add_cookie(cookie)
            except :
                pass
        time.sleep(5)        

        if self.check_login_status() :
            logger.info("manul login succeed")
            return True
        else :
            logger.info("manul login failure, please try next one ")
            return False
    
    def auto_login(self) :
        logger.info("auto login start")
        driver = self.driver
    
        try :
            driver.get("https://login.taobao.com/member/login.jhtml?style=mini&from=alimama")
            
            self._send_keys((By.ID, "TPL_username_1"), "yiranlandtour", True)
            self._send_keys((By.ID, "TPL_password_1"), "Taozigege1990", True)
            
            # show the slide bar to verify human or machine
            if driver.find_element_by_id("nocaptcha").get_attribute("style") :
                logger.info("show slide bar to verify human or machine, auto login quits, please manully login")
                return False

            self._click((By.ID, "J_SubmitStatic"), after_click_sleep_time = 5)   
        except :
            pass
        finally :
            if self.check_login_status() :
                logger.info("auto login succeed")
                return True
            else :
                logger.info("auto login failure, please try manully login ")
                return False

    def logout(self) :
        logger.info("logout")
        driver = self.driver
 
        try :
            driver.get("http://www.alimama.com/index.htm")
            self._click((By.CSS_SELECTOR, "#J_menu_login_out div.menu-hd span.menu-loginout"))
        except :
            pass
        finally :
            driver.delete_all_cookies()
        return