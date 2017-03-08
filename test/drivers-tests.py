#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import sys
import os

sys.path.append(os.getcwd())


def main():
    webdriver = WebDrivers(Modes.DEBUG)
    print (type(webdriver))

    driver = webdriver.instance
    print (type(driver))

    driver.get("http://cn.bing.com/")

    time.sleep(10)

    driver.quit()


if __name__ == '__main__':

    from common import Modes
    from common import WebDrivers

    main()
