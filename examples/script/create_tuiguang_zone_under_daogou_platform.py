#!/usr/bin/python3
# -*- coding: utf-8 -*-
from basic import *

# # # # # # # # # # # # # # # # # # # # # 
# Create a filehandler and add to logger
if not os.path.exists("log/"): os.makedirs("log/");
fh = logging.FileHandler('./log/create_tuiguang_zone_under_daogou_platform.log')  
fh.setFormatter(formatter)  
logger.addHandler(fh)
#
# # # # # # # # # # # # # # # # # # # # # 


class CreateTuiGuangZone (Basic) :

    def behavior(self, task) :
        global GLOBAL_RESULT_QUEUE
        global GLOBAL_RESULT_QUEUE_LOCK
        global GLOBAL_ERROR_QUEUE
        global GLOBAL_ERROR_QUEUE_LOCK

        hash_task = str(hashlib.md5(str(task).encode()).hexdigest())
        logger.info("create_tuiguang_zone start(%s)" % (hash_task))
        driver = self.driver

        try :
            driver.get(task['url'])
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
                if operator.eq(option.text, task['sitename']) :
                    option.click()
                    no_option = False
                    break
            
            if no_option : 
                raise ValueError("can not find sitename")

            # -- 选择 ‘新建推广位’
            self._click((By.CSS_SELECTOR, "#zone-form > div:nth-child(4) > div > label:nth-child(2) > input"))

            # -- 填入新增推广位
            self._send_keys((By.CSS_SELECTOR, "#zone-form > div:nth-child(5) > input"), task['newadzonename'])
            
            # -- 点击‘确认’
            # -----------USER CHANGE START-----------
            # self._click((By.CSS_SELECTOR, "#J_global_dialog > div > div.dialog-ft > button.btn.btn-brand.w100.mr10")) # 确认
            self._click((By.CSS_SELECTOR, "#J_global_dialog > div > div.dialog-ft > button.btn.btn-gray.w100")) # 取消
            # -----------USER CHANGE  END -----------

            GLOBAL_RESULT_QUEUE_LOCK.acquire()
            GLOBAL_RESULT_QUEUE.append({'task': task, 'status': 'Ok'})
            GLOBAL_RESULT_QUEUE_LOCK.release()

        except ValueError as e :
            logger.info("ValueError %s : %s" % (str(e), task['url']))
            
            GLOBAL_ERROR_QUEUE_LOCK.acquire()
            GLOBAL_ERROR_QUEUE.append({'task': task, 'status': 'ValueError', 'message': str(e)})
            GLOBAL_ERROR_QUEUE_LOCK.release()

        except Exception as e :
            logger.error("%s" % (str(e)))

            GLOBAL_ERROR_QUEUE_LOCK.acquire()
            GLOBAL_ERROR_QUEUE.append({'task': task, 'status': 'Error', 'message': str(e)})
            GLOBAL_ERROR_QUEUE_LOCK.release()

        logger.info("create_tuiguang_zone end(%s) " % (hash_task))
        return


if __name__ == "__main__" :

    # -----------USER SETTING START-----------
    # newadzonename : {maxLength: [64, '推广位名称最长64个字符']}
    GLOBAL_THREADS_MAXNUM = 2

    GLOBAL_TASK_QUEUE.append({
            'url': "http://pub.alimama.com/promo/item/channel/index.htm?q=https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%3Fid%3D43843797537&channel=qqhd", 
            'sitename': 'xingwu-test2', 
            'newadzonename': 'wingwu-test2-2'
        })
    GLOBAL_TASK_QUEUE.append({
            'url': "http://pub.alimama.com/promo/item/channel/index.htm?q=https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%3Fid%3D43843797537&channel=qqhd", 
            'sitename': 'xingwu-test2', 
            'newadzonename': 'wingwu-test2-3'
        })
    GLOBAL_TASK_QUEUE.append({
            'url': "http://pub.alimama.com/promo/item/channel/index.htm?q=https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%3Fid%3D43843797537&channel=qqhd", 
            'sitename': 'xingwu-test2', 
            'newadzonename': 'wingwu-test2-3'
        })
    # -----------USER SETTING  END -----------

    threads = []
    for index in range(GLOBAL_THREADS_MAXNUM) :
        # thread = CreateTuiGuangZone(mode = Mode.DEVELOP)
        thread = CreateTuiGuangZone(mode = Mode.PRODUCTION)
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
