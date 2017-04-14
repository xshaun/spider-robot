#!/usr/bin/python3
# -*- coding: utf-8 -*-
from basic import *

# # # # # # # # # # # # # # # # # # # # # 
# Create a filehandler and add to logger
if not os.path.exists("log/"): os.makedirs("log/");
fh = logging.FileHandler('./log/dingxiang_plan.log')  
fh.setFormatter(formatter)  
logger.addHandler(fh)
#
# # # # # # # # # # # # # # # # # # # # # 

# # # # # # # # # # # # # # # # # # # # # 
# Global variables for custom behavior
#
# # # # # # # # # # # # # # # # # # # # # 

class DingXiangPlan (Basic) :

    def behavior(self, url) :
        global GLOBAL_RESULT_QUEUE
        global GLOBAL_RESULT_QUEUE_LOCK
        global GLOBAL_ERROR_QUEUE
        global GLOBAL_ERROR_QUEUE_LOCK
                
        hash_url = str(hashlib.md5(url.encode()).hexdigest())
        logging.info("dingxiang_plan start(%s)" % (hash_url))
        driver = self.driver

        try :
            driver.get(url)
            self._driver_remove_popup_1()

            all_goods = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((
                        By.CSS_SELECTOR, 
                        "#J_item_list #J_search_results div.block-search-box.tag-wrap"
                    ))
                )

            for item in all_goods :
                ele_a = item.find_element(
                        By.CSS_SELECTOR, 
                        "div.box-shop-info div.tags-container a.tag-plan"
                    )
                ele_a_title = ele_a.get_attribute("title")

                # Choose ‘定向计划’
                if ele_a_title != "点击申请定向计划" :
                    continue
                ele_a.click()
                
                # Choose the greatest ratio plan
                # -- list all plans
                all_plans = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((
                            By.CSS_SELECTOR, 
                            "#J_global_dialog div.dialog-bd div.table-scroll table.table tbody tr"
                        ))
                    )
                # -- choose first plan
                plan = driver.find_element(
                        By.CSS_SELECTOR, 
                        "#J_global_dialog div.dialog-bd table.table tbody tr:first-child td:last-child a:last-child"
                    )
                plan_ratio = 0.0
                # -- compare ratios with each other
                for item in all_plans :
                    item_plan_ratio = item.find_element(
                            By.CSS_SELECTOR , 
                            "td.left.w50 span:first-child"
                        ).text
                    item_plan_ratio = float(item_plan_ratio)
    
                    if item_plan_ratio > plan_ratio :
                        plan_ratio = item_plan_ratio
                        plan = item.find_element(
                                By.CSS_SELECTOR , 
                                "td:last-child a:last-child"
                            )
                plan.click()

                # Give a promotion Reason
                # 
                # -----------USER CHANGE START-----------
                reason = "Apply -- Reasons"
                self._send_keys((By.ID, "J_applyReason"), reason)
                
                # self._click((By.CSS_SELECTOR, "#J_global_dialog div.block-campaign div.dialog-ft button.btn-brand")) # 确认
                self._click((By.CSS_SELECTOR, "#J_global_dialog div.block-campaign div.dialog-ft button.btn-gray")) # 取消
                # 
                # -----------USER CHANGE  END -----------
                
                GLOBAL_RESULT_QUEUE_LOCK.acquire()
                GLOBAL_RESULT_QUEUE.append({'url': url, 'status': 'Ok'})
                GLOBAL_RESULT_QUEUE_LOCK.release()

                break

        except Exception as e :
            logging.error("%s" % (str(e)))
            
            GLOBAL_ERROR_QUEUE_LOCK.acquire()
            GLOBAL_ERROR_QUEUE.append({'url': url, 'status': 'Error', 'message': str(e)})
            GLOBAL_ERROR_QUEUE_LOCK.release()
            

        logging.info("dingxiang_plan end(%s) " % (hash_url))
        return


if __name__ == "__main__" :

    # -----------USER SETTING START-----------
    GLOBAL_THREADS_MAXNUM = 3

    for i in range(50):
        GLOBAL_TASK_QUEUE.append("http://pub.alimama.com/promo/search/index.htm?q=%E3%80%90%E7%BA%A2%E7%BC%80%E3%80%91holiday%E7%B3%BB%E5%88%97%E8%BD%BB%E4%BE%BF%E6%92%9E%E8%89%B2%E5%8F%AF%E6%8A%98%E5%8F%A0%E5%8F%8C%E8%82%A9%E5%8C%85")
    # -----------USER SETTING  END -----------

    threads = []
    for index in range(GLOBAL_THREADS_MAXNUM) :
        # thread = DingXiangPlan(mode = Mode.DEVELOP)
        thread = DingXiangPlan(mode = Mode.PRODUCTION)
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
