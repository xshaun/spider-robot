#!/usr/bin/python3
# -*- coding: utf-8 -*-
from basic import *

# # # # # # # # # # # # # # # # # # # # # 
# Create a filehandler and add to logger
if not os.path.exists("log/"): os.makedirs("log/");
fh = logging.FileHandler('./log/getall_tuiguang_zones_under_daogou_platform.log')  
fh.setFormatter(formatter)  
logger.addHandler(fh)
#
# # # # # # # # # # # # # # # # # # # # # 

# # # # # # # # # # # # # # # # # # # # # 
# Global variables for custom behavior
# GLOBAL_PAGE
GLOBAL_PAGE = 0
# GLOBAL_PAGE
GLOBAL_PAGE_OVER = False
# Global GLOBAL_PAGE && GLOBAL_PAGE_OVER Lock
GLOBAL_PAGE_LOCK = threading.Lock()
#
# # # # # # # # # # # # # # # # # # # # # 

class GetallTuiGuangZones (Basic) :

    def run(self) :
        logger.info("thread start to run ")
  
        # login - alimama
        while True :
            if self.auto_login() :
                break
            if self.manul_login() :
                break

        while self.behavior():
            pass

        # logout alimama
        self.logout()

        # close driver
        self.driver.close() 
        
        logger.info("thread end ")

    def behavior(self) :
        global GLOBAL_TASK_QUEUE
        global GLOBAL_RESULT_QUEUE
        global GLOBAL_RESULT_QUEUE_LOCK
        global GLOBAL_ERROR_QUEUE
        global GLOBAL_ERROR_QUEUE_LOCK
        global GLOBAL_PAGE
        global GLOBAL_PAGE_OVER
        global GLOBAL_PAGE_LOCK
        
        GLOBAL_PAGE_LOCK.acquire()
        GLOBAL_PAGE += 1
        topage = GLOBAL_PAGE
        if GLOBAL_PAGE_OVER:
            GLOBAL_PAGE_LOCK.release()
            return False    
        GLOBAL_PAGE_LOCK.release()

        logger.info("getall_tuiguang_zones start(page = %d)" % (topage))
        driver = self.driver

        try :
            driver.get("http://pub.alimama.com/myunion.htm?#!/manage/zone/zone?tab=3&toPage=%d" % (topage))
            self._driver_remove_popup_2()

            recordsnum = int(driver.find_element_by_css_selector("#J_item_pagination > div.pagination-info > span:nth-child(5)").text)

            if recordsnum == 0 :
                logger.info("getall_tuiguang_zones end(page = %d): no records" % (topage))
                GLOBAL_PAGE_LOCK.acquire()
                GLOBAL_PAGE_OVER = True
                GLOBAL_PAGE_LOCK.release()
                return False

            records = driver.find_elements_by_css_selector("#J_vf_table > div.table-container > table > tbody > tr")
            
            for item in records :
                adzonename = item.find_element_by_css_selector("td:nth-child(1)").text
                pid = item.find_element_by_css_selector("td:nth-child(2)").text
                siteid = pid.split('_')[2]
                adzoneid = pid.split('_')[3]
                daogoun = item.find_element_by_css_selector("td:nth-child(3)").text # sitename

                if daogoun in GLOBAL_TASK_QUEUE:
                    GLOBAL_RESULT_QUEUE_LOCK.acquire()
                    GLOBAL_RESULT_QUEUE[daogoun].append({'adzonename':adzonename, 'adzoneid':adzoneid, 'pid': pid, 'siteid': siteid})
                    GLOBAL_RESULT_QUEUE_LOCK.release()

        except Exception as e :
            logger.error("%s" % (str(e)))

            GLOBAL_ERROR_QUEUE_LOCK.acquire()
            GLOBAL_ERROR_QUEUE.append({
                    'url': "http://pub.alimama.com/myunion.htm?#!/manage/zone/zone?tab=3&toPage=%d" % (topage), 
                    'status': 'Error', 
                    'message': str(e)
                })
            GLOBAL_ERROR_QUEUE_LOCK.release()

        logger.info("getall_tuiguang_zones end(page = %d)" % (topage))
        return True


if __name__ == "__main__" :

    # -----------USER SETTING START-----------
    GLOBAL_THREADS_MAXNUM = 3

    GLOBAL_TASK_QUEUE.append('xingwu-test2')
    GLOBAL_TASK_QUEUE.append('QQ_32336116')
    GLOBAL_TASK_QUEUE.append('互力微信淘客系统')
    
    # -----------USER SETTING  END -----------

    GLOBAL_RESULT_QUEUE = {}
    for item in GLOBAL_TASK_QUEUE: 
        GLOBAL_RESULT_QUEUE[item] = list()

    threads = []
    for index in range(GLOBAL_THREADS_MAXNUM) :
        # thread = GetallTuiGuangZones(mode = Mode.DEVELOP)
        thread = GetallTuiGuangZones(mode = Mode.PRODUCTION)
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
        print (json.dumps(GLOBAL_ERROR_QUEUE, indent = 4))
