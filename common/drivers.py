#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright 2017 sunxiaoyang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .modes import Modes
from selenium import webdriver
import os
import platform

PhantomJS_Version = "2.1.1"
ChromeDriver_Version = "2.27"


class WebDrivers(object):
    """Create a new webdriver"""

    def __init__(self, mode=None):
        super(WebDrivers, self).__init__()

        self.driver = None

        if (mode is Modes.PRODUCTION) or (mode is Modes.DEVELOPMENT_PRODUCTION):
            self.__driver_phantomjs()
        else:
            self.__driver_chrome()

    @property
    def instance(self):
        """Returns the webdriver instance.

        :Usage:
         - WebDrivers().instance
         """
        return self.driver

    def __driver_phantomjs(self):
        system_os = platform.system()

        if "Windows" == system_os:
            self.driver = webdriver.PhantomJS(
                executable_path="./libs/phantomjs-%s-windows/bin/phantomjs.exe" % (
                    PhantomJS_Version),
                service_log_path=os.path.devnull,
            )  # Windows

        elif "Linux" == system_os:
            self.driver = webdriver.PhantomJS(
                executable_path="./libs/phantomjs-%s-linux-x86_64/bin/phantomjs" % (
                    PhantomJS_Version),
                service_log_path=os.path.devnull,
            )  # Linux amd64

        else:
            """
            Future work
                do something such as download source code and compile
            """
            pass

        if self.driver is not None:
            self.driver.set_window_position(0, 0)
            self.driver.set_window_size(4096, 4096)

    def __driver_chrome(self):
        system_os = platform.system()

        if "Windows" == system_os:
            self.driver = webdriver.Chrome(
                executable_path="./libs/chromedriver-%s-windows.exe" % (
                    ChromeDriver_Version),
                service_log_path=os.path.devnull,
            )  # Windows

        elif "Linux" == system_os:
            self.driver = webdriver.Chrome(
                executable_path="./libs/chromedriver-%s-linux-x86_64" % (
                    ChromeDriver_Version),
                service_log_path=os.path.devnull,
            )  # Linux amd64

        else:
            """
            Future work
                do something such as download source code and compile
            """
            pass

        if self.driver is not None:
            self.driver.maximize_window()
