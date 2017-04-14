#!/usr/bin/python3
# -*- coding: utf-8 -*-
from basic import *

# # # # # # # # # # # # # # # # # # # # # 
# Create a filehandler and add to logger
if not os.path.exists("log/"): os.makedirs("log/");
fh = logging.FileHandler('./log/download_dingdan_details_excel.log')  
fh.setFormatter(formatter)
logger.addHandler(fh)
#
# # # # # # # # # # # # # # # # # # # # # 


class DingDanDetailsExcel (Basic) :

    def behavior(self, task) :
        global GLOBAL_RESULT_QUEUE
        global GLOBAL_RESULT_QUEUE_LOCK
        global GLOBAL_ERROR_QUEUE
        global GLOBAL_ERROR_QUEUE_LOCK
                
        hash_task = str(hashlib.md5(str(task).encode()).hexdigest())
        logging.info("download_dingdan_details_excel start(%s)" % (hash_task))
        driver = self.driver

        try :
            url = "http://pub.alimama.com/report/getTbkPaymentDetails.json?queryType=1"
            driver.get("%s&startTime=%s&endTime=%s" % (url, task['startTime'], task['endTime']))
            
            result = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body>pre"))
                ).text
            
            # convert string to json
            info = json.loads(result)
            if not info['ok'] :
                raise Exception(json.dumps(info))

            download_link = ("%s&DownloadID=DOWNLOAD_REPORT_INCOME_NEW&startTime=%s&endTime=%s") % (url, task['startTime'], task['endTime'])
            
            session = requests.Session()
            cookies = driver.get_cookies()

            for cookie in cookies: 
                session.cookies.set(cookie['name'], cookie['value'])
            response = session.get(download_link)
            
            if not os.path.exists("Download/"): 
                os.makedirs("Download/")
            xls = open("Download/TaokeDetail-%s-%s.xls" % (task['startTime'], task['endTime']), "wb")
            xls.write(response.content)
            xls.close()
    
            GLOBAL_RESULT_QUEUE_LOCK.acquire()
            GLOBAL_RESULT_QUEUE.append({
                    'task': task, 
                    'status': 'Ok', 
                    'filename': "TaokeDetail-%s-%s.xls" % (task['startTime'], task['endTime'])
                })
            GLOBAL_RESULT_QUEUE_LOCK.release()

        except Exception as e :
            logging.error("%s" % (str(e)))
            GLOBAL_ERROR_QUEUE_LOCK.acquire()
            GLOBAL_ERROR_QUEUE.append({'task': task, 'status': 'Error', 'message': str(e)})
            GLOBAL_ERROR_QUEUE_LOCK.release()

        logging.info("download_dingdan_details_excel end(%s) " % (hash_task))
        return


if __name__ == "__main__" :

    # -----------USER SETTING START-----------
    GLOBAL_THREADS_MAXNUM = 5

    GLOBAL_TASK_QUEUE.append({'startTime': '2017-02-17', 'endTime': '2017-02-23'})
    GLOBAL_TASK_QUEUE.append({'startTime': '2017-01-17', 'endTime': '2017-02-20'})
    GLOBAL_TASK_QUEUE.append({'startTime': '2017-02-17', 'endTime': '2017-02-26'})
    GLOBAL_TASK_QUEUE.append({'startTime': '2016-02-10', 'endTime': '2017-02-26'})
    GLOBAL_TASK_QUEUE.append({'startTime': '2015-02-10', 'endTime': '2017-02-27'})
    # -----------USER SETTING  END -----------

    threads = []
    for index in range(GLOBAL_THREADS_MAXNUM) :
        thread = DingDanDetailsExcel(mode = Mode.DEVELOP)
        # thread = DingDanDetailsExcel(mode = Mode.PRODUCTION)
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
