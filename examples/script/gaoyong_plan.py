#!/usr/bin/python3
# -*- coding: utf-8 -*-
from basic import *

# # # # # # # # # # # # # # # # # # # # # 
# Create a filehandler and add to logger
if not os.path.exists("log/"): os.makedirs("log/");
fh = logging.FileHandler('./log/gaoyong_plan.log')  
fh.setFormatter(formatter)  
logger.addHandler(fh)
#
# # # # # # # # # # # # # # # # # # # # # 

# # # # # # # # # # # # # # # # # # # # # 
# Global variables for custom behavior
# name of daogou
GLOBAL_SITENAME = None
# name of tuiguangwei
GLOBAL_ADZONENAME = None
#
# # # # # # # # # # # # # # # # # # # # # 

class GaoYongPlan (Basic) :

    def behavior(self, url) :
        global GLOBAL_RESULT_QUEUE
        global GLOBAL_RESULT_QUEUE_LOCK
        global GLOBAL_ERROR_QUEUE
        global GLOBAL_ERROR_QUEUE_LOCK
        global GLOBAL_SITENAME
        global GLOBAL_ADZONENAME

        hash_url = str(hashlib.md5(url.encode()).hexdigest())
        logger.info("gaoyong_plan start(%s)" % (hash_url))
        driver = self.driver

        try :
            driver.get(url)
            self._driver_remove_popup_1()

            # -- 点击 ‘立即推广’
            try :
                self._click((By.CSS_SELECTOR, "#J_search_results > div > div > div.box-btn-group > a.box-btn-left"))
            except TimeoutException as e :   
                raise ValueError("no good")

            # -- 选择 ‘导购推广’
            self._click((By.CSS_SELECTOR, "#zone-form > div:nth-child(2) > div > label:nth-child(3) > input"))
    
            # -- 根据 sitename 选择导购名称
            self._click((By.CSS_SELECTOR, "#zone-form > div:nth-child(3) > div > button > span.caret_custom.caret_brixfont > span.brixfont.down"))

            select = driver.find_element(
                    By.CSS_SELECTOR ,
                    "#zone-form > div:nth-child(3) > div > div > ul"
                )

            all_options = select.find_elements_by_css_selector("li > a > span")
            no_option = True
            for option in all_options:
                if operator.eq(option.text, GLOBAL_SITENAME) :
                    option.click()
                    no_option = False
                    break
            
            if no_option : 
                raise ValueError("can not find sitename")

            # -- 选择 ‘选择已有推广位’
            self._click((By.CSS_SELECTOR, "#zone-form > div:nth-child(4) > div > label:nth-child(1) > input"))

            # -- 根据 adzonename 选择推广位
            self._click((By.CSS_SELECTOR, "#zone-form > div:nth-child(5) > div > button > span.caret_custom.caret_brixfont > span.brixfont.down"))
 
            select = driver.find_element(
                    By.CSS_SELECTOR ,
                    "#zone-form > div:nth-child(5) > div > div > ul"
                )

            all_options = select.find_elements_by_css_selector("li > a > span")
            no_option = True
            for option in all_options:
                if operator.eq(option.text, GLOBAL_ADZONENAME) :
                    option.click()
                    no_option = False
                    break

            if no_option : 
                raise ValueError("can not find adzonename")

            # -- 点击‘确认’
            self._click((By.CSS_SELECTOR, "#J_global_dialog > div > div.dialog-ft > button.btn.btn-brand.w100.mr10"))

            # -- 点击‘长连接’
            self._click((By.CSS_SELECTOR, "#magix_vf_code > div > div.dialog-hd > ul > li:nth-child(2)"))
            
            # -- 获取连接
            good_link = driver.find_element_by_id("clipboard-target-1").get_attribute("value")
            ticket_link = driver.find_element_by_id("clipboard-target-2").get_attribute("value")
            
            GLOBAL_RESULT_QUEUE_LOCK.acquire()
            GLOBAL_RESULT_QUEUE.append({'url': url, 'status': 'Ok', 'good_link': good_link, 'ticket_link': ticket_link})
            GLOBAL_RESULT_QUEUE_LOCK.release()

            # -- 点击‘关闭’
            self._click((By.CSS_SELECTOR, "#magix_vf_code > div > div.dialog-ft > button"))

        except ValueError as e :
            logger.info("ValueError %s : %s" % (str(e), url))
            
            GLOBAL_ERROR_QUEUE_LOCK.acquire()
            GLOBAL_ERROR_QUEUE.append({'url': url, 'status': 'ValueError', 'message': str(e)})
            GLOBAL_ERROR_QUEUE_LOCK.release()

        except Exception as e :
            logger.error("%s" % (str(e)))

            GLOBAL_ERROR_QUEUE_LOCK.acquire()
            GLOBAL_ERROR_QUEUE.append({'url': url, 'status': 'Error', 'message': str(e)})
            GLOBAL_ERROR_QUEUE_LOCK.release()

        logger.info("gaoyong_plan end(%s) " % (hash_url))
        return


if __name__ == "__main__" :

    # -----------USER SETTING START-----------
    GLOBAL_THREADS_MAXNUM = 3

    # 导购名称
    GLOBAL_SITENAME = 'xingwu-test2'
    # 推广位
    GLOBAL_ADZONENAME = 'wingwu-test2-2'

    GLOBAL_TASK_QUEUE.append("http://pub.alimama.com/promo/item/channel/index.htm?q=https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%3Fid%3D43843797537&channel=qqhd")
    GLOBAL_TASK_QUEUE.append("http://pub.alimama.com/promo/item/channel/index.htm?q=https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%3Fid%3D43843797537&channel=qqhd")
    GLOBAL_TASK_QUEUE.append("http://pub.alimama.com/promo/item/channel/index.htm?q=https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%3Fid%3D43843797537&channel=qqhd")
    GLOBAL_TASK_QUEUE.append("http://pub.alimama.com/promo/item/channel/index.htm?q=https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%3Fid%3D43843797537&channel=qqhd")
    # -----------USER SETTING  END -----------

    threads = []
    for index in range(GLOBAL_THREADS_MAXNUM) :
        # thread = GaoYongPlan(mode = Mode.DEVELOP)
        thread = GaoYongPlan(mode = Mode.PRODUCTION)
        thread.start()
        threads.append(thread)

    for t in threads :
        t.join()
    
    if len(GLOBAL_RESULT_QUEUE) > 0 :
        print ('-----------------RESULT--------------------')
        print (json.dumps(GLOBAL_RESULT_QUEUE, indent = 4))
    if len(GLOBAL_ERROR_QUEUE) > 0 :
        print ('-----------------ERROR-----------------')
        print (json.dumps(GLOBAL_ERROR_QUEUE, indent = 4))
