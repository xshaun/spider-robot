#!/usr/bin/python3
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
# available since 2.26.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
import hashlib
import json
import logging
import logging.config
import math
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
    fmt="[%(asctime)s %(threadName)s:%(thread)2d no:%(lineno)3d] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
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
#
# create result formatter
formatter = logging.Formatter(
    fmt="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
#
# Create a filehandler and add to logger
fh = logging.FileHandler('./result-part-d_10_.txt')
fh.setLevel(logging.WARNING)
fh.setFormatter(formatter)
#
# add ch to logger
logger.addHandler(fh)
#
# # # # # # # # # # # # # # # # # # # # #


class Mode(object):
    """
    Set of supported modes.
    """
    DEBUG = "debug"
    DEVELOP = "develop"
    PRODUCTION = "production"


class Basic(threading.Thread):

    def __init__(self, mode, url=None, news_time=None):
        threading.Thread.__init__(self)

        # driver
        system = platform.system()
        if operator.eq(mode, Mode.PRODUCTION):  # Production
            if operator.eq(system, "Windows"):
                self.driver = webdriver.PhantomJS(
                    executable_path="./libs/phantomjs-2.1.1-windows/bin/phantomjs.exe",
                    service_log_path=os.path.devnull,

                )  # Windows
            else:
                self.driver = webdriver.PhantomJS(
                    executable_path="./libs/phantomjs-2.1.1-linux-x86_64/bin/phantomjs",
                    service_log_path=os.path.devnull
                )  # Linux amd64
            self.driver.set_window_position(0, 0)
            self.driver.set_window_size(4096, 4096)
        else:  # Debug & Develop
            if operator.eq(system, "Windows"):
                self.driver = webdriver.Chrome(
                    executable_path="./libs/chromedriver_2.27_windows.exe",
                    service_log_path=os.path.devnull
                )  # Windows Chrome
            else:
                self.driver = webdriver.Chrome(
                    executable_path="./libs/chromedriver_2.27_linux64",
                    service_log_path=os.path.devnull
                )  # Linux Chrome
            self.driver.maximize_window()

        self.url = url
        self.news_time = news_time

    def run(self):
        """
        Called before running. This method may be overridden
        to define custom behavior.
        """
        pass


class Baidu (Basic):

    def run(self):
        driver = self.driver
        url = self.url
        news_time = self.news_time

        logger.info("Baidu is searching : %s" % (url))

        driver.get("https://www.baidu.com/s?wd=%s" % (url))

        flag = False
        for i in range(60):  # 尝试次数
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div#content_left > div:nth-child(1)"))
                )

                part_url = element.find_element(
                    By.CSS_SELECTOR, "div.f13 > a > b").text
                if part_url in url:
                    flag = True
                    break
            except:  # catch anything
                driver.refresh()

        news_timestamp = time.mktime(time.strptime(
            '2017-' + news_time, '%Y-%m-%d %H:%M'))
        current_timestamp = time.time()

        driver.quit()

        logger.warning("%s %s baidu %s %.2f" % (
            url, '2017-' + news_time, str(flag), (current_timestamp - news_timestamp) / 60.0))
        return


class Qihoo360 (Basic):

    def run(self):
        driver = self.driver
        url = self.url
        news_time = self.news_time

        logger.info("Qihoo360 is searching : %s" % (url))

        driver.get("https://www.so.com/s?q=%s" % (url))

        flag = False
        for i in range(60):  # 尝试次数
            try:
                nonews = True
                try:
                    # 无搜索结果：正常执行； 有搜索结果：抛异常
                    driver.find_element(By.CSS_SELECTOR, "#main > div")
                    time.sleep(5)
                except:  # catch anything
                    nonews = False
                if nonews:
                    raise

                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#main > ul > li:nth-child(1)"))
                )

                part_url = element.find_element(
                    By.CSS_SELECTOR, "p > cite").text
                part_url = part_url[:-3]
                if part_url in url:
                    flag = True
                    break
            except:  # catch anything
                driver.refresh()

        news_timestamp = time.mktime(time.strptime(
            '2017-' + news_time, '%Y-%m-%d %H:%M'))
        current_timestamp = time.time()

        driver.quit()

        logger.warning("%s %s qihoo360 %s %.2f" % (
            url, '2017-' + news_time, str(flag), (current_timestamp - news_timestamp) / 60.0))
        return


if __name__ == "__main__":

    driver = None
    system = platform.system()
    if operator.eq(system, "Windows"):
        # driver = webdriver.Chrome(
        #     executable_path="./libs/chromedriver_2.27_windows.exe",
        #     service_log_path=os.path.devnull
        # )  # Windows Chrome
        driver = webdriver.PhantomJS(
            executable_path="./libs/phantomjs-2.1.1-windows/bin/phantomjs.exe",
            service_log_path=os.path.devnull,
        )  # Windows
    else:
        # driver = webdriver.Chrome(
        #     executable_path="./libs/chromedriver_2.27_linux64",
        #     service_log_path=os.path.devnull
        # )  # Linux Chrome
        driver = webdriver.PhantomJS(
            executable_path="./libs/phantomjs-2.1.1-linux-x86_64/bin/phantomjs",
            service_log_path=os.path.devnull
        )  # Linux amd64
    driver.maximize_window()

    sinanews = "http://roll.news.sina.com.cn/s/channel.php?ch=01#col=89&spec=&type=&ch=01&k=&offset_page=0&offset_num=0&num=60&asc=&page=1"
    driver.get(sinanews)

    reload_button = WebDriverWait(driver, 1000).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#reloadButton"))
    )

    urls = list()
    threads = list()
    newscount = 1
    ignore_first = True
    while newscount <= 1500:  # 新闻条数
        try:
            reload_button.click()

            news_list = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#d_list"))
            )

            news_firstitem = news_list.find_element(
                By.CSS_SELECTOR, "ul > li:nth-child(1)")

            news_url = str(news_firstitem.find_element(
                By.CSS_SELECTOR, "span.c_tit > a").get_attribute('href'))
            news_time = news_firstitem.find_element(
                By.CSS_SELECTOR, "span.c_time").text

            if news_url not in urls:
                urls.append(news_url)

                if ignore_first:
                    ignore_first = False
                    continue

                print ('found ' + str(newscount) + ' news')
                newscount += 1

                # t_baidu = Baidu(Mode.DEVELOP, news_url, news_time)
                # t_qihoo360 = Qihoo360(Mode.DEVELOP, news_url, news_time)
                t_baidu = Baidu(Mode.PRODUCTION, news_url, news_time)
                t_qihoo360 = Qihoo360(Mode.PRODUCTION, news_url, news_time)

                t_baidu.start()
                t_qihoo360.start()

                threads.append(t_baidu)
                threads.append(t_qihoo360)
        except Exception as e:
            print (e)
            pass
        finally:
            time.sleep(3)

    # waiting for all threads end
    for t in threads:
        t.join()

    driver.quit()

    print ('END')
