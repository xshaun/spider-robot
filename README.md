# spider-robot
爬虫框架：自动登陆&amp;手动登陆、共享Cookies、多线程、终端运行、多级日志、多种模式等

## 简介
**spider-robot** 意在为简化 *数据爬取/自动化测试/操作* 等程序设计，使人们从重复性、耗时性的体力工作中解脱出来，用同样的时间做更多的事（比如购物、游泳、撸串等），提高个人工作效率和生活质量。

**spider-robot** 是一段功能简单、但非常实用的小程序。使用 Selenium（Python版）编写，同时默认采用的显示浏览器为 Chrome，终端式引擎为 PhantomJS。

----
***spider-robot由来：*** 项目由来于作者在接手爬虫相关任务时，通过多次任务实践，发现不同爬取任务但最终代码却不尽相同，以此整理分享任务代码，简化程序设计。希望人人都能设计编写自己的spider-robot，替代自己做部分工作，让自己从繁重的工作中得以解脱。

----
***spider-robot目标：*** 作者将持续维护和分享使用spider-robot编写的样例程序（/examples）。若您使用了spider-robot编写小程序，希望您能够分享给大家，非常欢迎您的加入。

## 安装步骤
> 操作系统：Linux（Ubuntu,RedHat...）, macOS, Windows等

1. 安装Python3
  1. 下载平台安装包并进行安装
  1. 配置环境变量PATH
  1. 测试是否安装成功   
    + 如：打开终端输入python --version

2. 安装Python HTTP Library
  + pip3 install requests
  
3. 安装Selenium
  + pip3 install selenium

4. 安装Chrome（支持用户自定义）
>spider-robot默认使用 Chrome 作为显示浏览器。   
>若用户有特殊需求，可修改源码，指定浏览器，并下载相应浏览器驱动；   
>否则需安装 Chrome。
  
5. 下载并运行spider-robot

## 目录说明


## 如何自己编写spider-robot


## 支持
**Python3.4**   
Docs:[https://docs.python.org/3.4/](https://docs.python.org/3.4/)

**Selenium** *[Apache 2.0 license]*   
Code:[https://github.com/SeleniumHQ/selenium](https://github.com/SeleniumHQ/selenium)   
Docs:[http://docs.seleniumhq.org/docs/](http://docs.seleniumhq.org/docs/)

**PhantomJS** *[BSD license]*   
Code:[https://github.com/ariya/phantomjs/](https://github.com/ariya/phantomjs/)   
Docs:[http://phantomjs.org/documentation/](http://phantomjs.org/documentation/)


