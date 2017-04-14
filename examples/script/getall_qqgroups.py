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
import platform
import pprint
import threading
import time

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
# Create console handler && set level to INFO && add ch to logger
ch = logging.StreamHandler() 
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch) 
#
# Create a filehandler and add to logger
if not os.path.exists("log/"): os.makedirs("log/");
fh = logging.FileHandler('./log/getall_qqgroups.log')  
fh.setFormatter(formatter)
logger.addHandler(fh)
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
#
# # # # # # # # # # # # # # # # # # # # # 


class Mode(object):
    """
    Set of supported modes.
    """
    DEBUG = "debug"
    DEVELOP = "develop"
    PRODUCTION = "production"


class GetAllQQGroups (threading.Thread) :
    def __init__(self, mode = Mode.DEVELOP) :
        threading.Thread.__init__(self)

        # driver
        system = platform.system()
        if operator.eq(mode, Mode.PRODUCTION):
            # Production
            if operator.eq(system, "Windows"):
                self.driver = webdriver.PhantomJS(
                        executable_path = "./libs/phantomjs-2.1.1-windows/bin/phantomjs.exe",
                        service_log_path = os.path.devnull
                    ) # Windows
            else:
                self.driver = webdriver.PhantomJS(
                        executable_path = "./libs/phantomjs-2.1.1-linux-x86_64/bin/phantomjs",
                        service_log_path = os.path.devnull
                    ) # Linux amd64
            self.driver.set_window_position(0, 0)
            self.driver.set_window_size(4096, 4096)
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
                # login
                while True :
                    if self.auto_login(task):
                        break
                    if self.manul_login() :
                        break
                
                self.behavior(task)

                # logout
                self.logout()
            else :
                break

        # close driver
        self.driver.close() 
        
        logger.info("thread end ")

    def behavior(self, task) :
        global GLOBAL_RESULT_QUEUE
        global GLOBAL_RESULT_QUEUE_LOCK
        global GLOBAL_ERROR_QUEUE
        global GLOBAL_ERROR_QUEUE_LOCK
                
        hash_task = str(hashlib.md5(str(task).encode()).hexdigest())
        logging.info("getall_qqgroups start(%s)" % (hash_task))
        driver = self.driver

        try :
            driver.get("http://qun.qzone.qq.com/group")
            
            element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#my_group_list_container"))
                )
            
            group_list = element.find_elements_by_css_selector("li > a")

            groups = list()
            for item in group_list :
                groupid = item.get_attribute("data-groupid")
                groupname = item.get_attribute("title")
                groups.append({'groupid': groupid, 'groupname': groupname})

            GLOBAL_RESULT_QUEUE_LOCK.acquire()
            GLOBAL_RESULT_QUEUE.append({'qq': task['qq'], 'groups': groups})
            GLOBAL_RESULT_QUEUE_LOCK.release()

        except Exception as e :
            logging.error("%s" % (str(e)))
            
            GLOBAL_ERROR_QUEUE_LOCK.acquire()
            GLOBAL_ERROR_QUEUE.append({'task': task, 'status': 'Error', 'message': str(e)})
            GLOBAL_ERROR_QUEUE_LOCK.release()
            
        logging.info("getall_qqgroups end(%s) " % (hash_task))
        return

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

    def check_login_status(self) :
        logger.info("checking login status")
        driver = self.driver

        try:
            driver.get("http://qun.qzone.qq.com/group")
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "userQuitBtn"))
            )

            return True
        except Exception as e:
            logger.error("login status false: %s" % (str(e)))
  
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
            
            driver.get("http://qun.qzone.qq.com/")
            
            input("waiting for user to manully login, (do not close browser manully) \n please press enter key after login succeed ")

            cookies = driver.get_cookies()
            driver.close()
        except :
            return False

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
    
    def auto_login(self, task) :
        logger.info("auto login start")
        driver = self.driver

        try:
            driver.get("http://ui.ptlogin2.qq.com/cgi-bin/login?appid=549000912&s_url=http://qun.qzone.qq.com/group")
            
            element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "bottom_qlogin"))
                )

            if operator.eq(element.get_attribute("style"), "display: block;"):
                self._click((By.ID, "switcher_plogin"))
            
            self._send_keys((By.ID, "u"), str(task['qq']), True)
            self._send_keys((By.ID, "p"), task['pw'], True)

            self._click((By.ID, "login_button"), after_click_sleep_time = 2)
      
        except Exception as e:
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
            driver.get("http://qun.qzone.qq.com/group")
            self._click((By.CSS_SELECTOR, "#userQuitBtn"))
            alert = driver.switch_to.alert
            alert.accept()
            time.sleep(2)
        except :
            pass
        finally :
            driver.delete_all_cookies()
        return

if __name__ == "__main__" :

    # -----------USER SETTING START-----------
    GLOBAL_THREADS_MAXNUM = 2

    GLOBAL_TASK_QUEUE.append({'qq': 100001, 'pw': 'abcdefght'})
    GLOBAL_TASK_QUEUE.append({'qq': 100002, 'pw': 'abcdefght'})
    GLOBAL_TASK_QUEUE.append({'qq': 100003, 'pw': 'abcdefght'})
    GLOBAL_TASK_QUEUE.append({'qq': 100004, 'pw': 'abcdefght'})
    # -----------USER SETTING  END -----------

    threads = []
    for index in range(GLOBAL_THREADS_MAXNUM) :
        # thread = GetAllQQGroups(mode = Mode.DEVELOP)
        thread = GetAllQQGroups(mode = Mode.PRODUCTION)
        thread.start()
        threads.append(thread)

    for t in threads :
        t.join()
    
    if len(GLOBAL_RESULT_QUEUE) > 0 :
        print ('-----------------RESULT--------------------')
        # print (json.dumps(GLOBAL_RESULT_QUEUE, indent = 4)) # dumps序列化采用 ascii编码， 中文编码unicode， 便于保存
        print (json.dumps(GLOBAL_RESULT_QUEUE, indent = 4, ensure_ascii = False)) # 便于查看
    if len(GLOBAL_ERROR_QUEUE) > 0 :
        print ('-----------------ERROR-----------------')
        print (json.dumps(GLOBAL_ERROR_QUEUE, indent = 4, ensure_ascii = False))