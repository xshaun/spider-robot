#!/usr/bin/python3
# -*- coding: utf-8 -*-
from basic import *

# # # # # # # # # # # # # # # # # # # # # 
# Create a filehandler and add to logger
if not os.path.exists("log/"): os.makedirs("log/");
fh = logging.FileHandler('./log/tuiguang_tongji.log')  
fh.setFormatter(formatter)
logger.addHandler(fh)
#
# # # # # # # # # # # # # # # # # # # # # 


class TuiGuangTongJi (Basic) :

    def behavior(self, task) :
        global GLOBAL_RESULT_QUEUE
        global GLOBAL_RESULT_QUEUE_LOCK
        global GLOBAL_ERROR_QUEUE
        global GLOBAL_ERROR_QUEUE_LOCK
                
        hash_task = str(hashlib.md5(str(task).encode()).hexdigest())
        logging.info("tuiguang_tongji start(%s)" % (hash_task))
        driver = self.driver

        try :
            adzoneId = task['adzoneId'] if 'adzoneId' in task.keys() else ''
            startTime = task['startTime'] if 'startTime' in task.keys() else time.strftime("%Y-%m-%d", time.localtime())
            endTime = task['endTime'] if 'endTime' in task.keys() else time.strftime("%Y-%m-%d", time.localtime())

            driver.get("http://pub.alimama.com/report/selfRpt.json?adzoneId=%s&startTime=%s&endTime=%s" % (str(adzoneId), startTime, endTime))
            
            result = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body>pre"))
                ).text
            
            # convert string to json
            info = json.loads(result)
            if not info['ok'] :
                raise Exception(json.dumps(info))

            GLOBAL_RESULT_QUEUE_LOCK.acquire()
            GLOBAL_RESULT_QUEUE.append({'task': task, 'status': 'Ok', 'result': result})
            GLOBAL_RESULT_QUEUE_LOCK.release()

        except Exception as e :
            logging.error("%s" % (str(e)))
            
            GLOBAL_ERROR_QUEUE_LOCK.acquire()
            GLOBAL_ERROR_QUEUE.append({'task': task, 'status': 'Error', 'message': str(e)})
            GLOBAL_ERROR_QUEUE_LOCK.release()

        logging.info("tuiguang_tongji end(%s) " % (hash_task))
        return


if __name__ == "__main__" :

    # -----------USER SETTING START-----------
    GLOBAL_THREADS_MAXNUM = 2

    GLOBAL_TASK_QUEUE.append({'startTime': '2017-02-17', 'endTime': '2017-02-23'})
    GLOBAL_TASK_QUEUE.append({'adzoneId': 71900791, 'startTime': '2017-02-10', 'endTime': '2017-02-23'})
    GLOBAL_TASK_QUEUE.append({'adzoneId': 71900791, 'startTime': '2016-02-10', 'endTime': '2017-02-23'})
    # -----------USER SETTING  END -----------

    threads = []
    for index in range(GLOBAL_THREADS_MAXNUM) :
        # thread = TuiGuangTongJi(mode = Mode.DEVELOP)
        thread = TuiGuangTongJi(mode = Mode.PRODUCTION)
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
