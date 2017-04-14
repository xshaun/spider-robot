#!/usr/bin/python3
# -*- coding: utf-8 -*-
from basic import *

# # # # # # # # # # # # # # # # # # # # # 
# Create a filehandler and add to logger
if not os.path.exists("log/"): os.makedirs("log/");
fh = logging.FileHandler('./log/create_daogou_platform.log')  
fh.setFormatter(formatter)  
logger.addHandler(fh)
#
# # # # # # # # # # # # # # # # # # # # # 

# # # # # # # # # # # # # # # # # # # # # 
# Global variables for custom behavior
#
# # # # # # # # # # # # # # # # # # # # # 

class CreateDaoGouPlatform (Basic) :

    def behavior(self, task) :
        global GLOBAL_RESULT_QUEUE
        global GLOBAL_RESULT_QUEUE_LOCK
        global GLOBAL_ERROR_QUEUE
        global GLOBAL_ERROR_QUEUE_LOCK
                
        hash_task = str(hashlib.md5(str(task).encode()).hexdigest())
        logging.info("create_daogou_platform start(%s)" % (hash_task))
        driver = self.driver

        try: 
            driver.get("http://pub.alimama.com/myunion.htm?toPage=1#!/manage/site/site?toPage=1&tab=4")
            self._driver_remove_popup_2()
            
            # -- 点击 ‘新增导购推广’
            self._click((By.CSS_SELECTOR, "#J_item_list > div > div > a"))
            
            # -- 输入 ‘导购名称’
            self._send_keys((By.CSS_SELECTOR, "#J_cat_form > ul > li:nth-child(1) > input"), task['name'], True)
            
            # -- 选择 ‘聊天工具’
            selected = driver.find_element(
                    By.CSS_SELECTOR ,
                    "#J_guide_dropdown > span > span"
                )

            if operator.ne(selected.text, "聊天工具"):
                self._click((By.CSS_SELECTOR, "#J_guide_dropdown > span > i"))
                
                select = driver.find_element(
                        By.CSS_SELECTOR ,
                        "#J_guide_dropdown > ul"
                    )

                all_options = select.find_elements_by_css_selector("li > span")
                no_option = True
                for option in all_options:
                    if operator.eq(option.text, "聊天工具") :
                        option.click()
                        no_option = False
                        break
                
                if no_option : 
                    raise ValueError("现导购类型中无‘聊天类型’")
            
            # -- 选择 ‘QQ’
            selected = driver.find_element(
                    By.CSS_SELECTOR ,
                    "#J_media_dropdown > span > span"
                )

            if operator.ne(selected.text, "QQ"):
                self._click((By.CSS_SELECTOR, "#J_media_dropdown > span > i"))
                
                select = driver.find_element(
                        By.CSS_SELECTOR ,
                        "#J_media_dropdown > ul"
                    )

                all_options = select.find_elements_by_css_selector("li > span")
                no_option = True
                for option in all_options:
                    if operator.eq(option.text, "QQ") :
                        option.click()
                        no_option = False
                        break
                
                if no_option : 
                    raise ValueError("现媒体类型中无‘QQ’")

            # -- 输入 QQ账号
            self._send_keys((By.CSS_SELECTOR, "#J_site_form > ul > li:nth-child(1) > div > input"), str(task['qq']), True)

            # -- 输入 QQ群号
            self._send_keys((By.CSS_SELECTOR, "#J_site_form > ul > li:nth-child(2) > div > input"), str(task['qqgroup']), True)

            #-- 点击 ‘确认’
            # -----------USER CHANGE START-----------
            # self._click((By.CSS_SELECTOR, "#vf-dialog > div > div:last-child > a:nth-child(1)")) # 确认
            self._click((By.CSS_SELECTOR, "#vf-dialog > div > div:last-child > a:nth-child(2)")) # 取消
            # -----------USER CHANGE  END -----------
            
            GLOBAL_RESULT_QUEUE_LOCK.acquire()
            GLOBAL_RESULT_QUEUE.append({'task': task, 'status': 'Ok'})
            GLOBAL_RESULT_QUEUE_LOCK.release()

        except Exception as e :
            logging.error("%s" % (str(e)))
            
            GLOBAL_ERROR_QUEUE_LOCK.acquire()
            GLOBAL_ERROR_QUEUE.append({'task': task, 'status': 'Error', 'message': str(e)})
            GLOBAL_ERROR_QUEUE_LOCK.release()
        
        logging.info("create_daogou_platform end(%s) " % (hash_task))
        return


if __name__ == "__main__" :

    # -----------USER SETTING START-----------
    GLOBAL_THREADS_MAXNUM = 1

    GLOBAL_TASK_QUEUE.append({'name': 'test-name', 'qq': 23423423, 'qqgroup': 86786786})
    GLOBAL_TASK_QUEUE.append({'name': 'test-name2', 'qq': 2342343, 'qqgroup': 8672386786})
    GLOBAL_TASK_QUEUE.append({'name': 'test-name2', 'qq': 2342343423, 'qqgroup': 867826786})
    # -----------USER SETTING  END -----------

    threads = []
    for index in range(GLOBAL_THREADS_MAXNUM) :
        # thread = CreateDaoGouPlatform(mode = Mode.DEVELOP)
        thread = CreateDaoGouPlatform(mode = Mode.PRODUCTION)
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
