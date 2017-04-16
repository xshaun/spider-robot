#!/bin/bash
#
# 工具：
# curl ： url请求模拟工具
#
# 参数说明：
# 【1】模拟windows xp平台上的ie6：
#     -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)"
# 【2】访问https站点： --insecure
# 【3】模拟登陆(POST)：
#     -d "user_name=coolleather.sale@gmail.com&user_password=cole"
# 【4】记录response里面的cookie信息至文件： -D cookie5.txt
# 【5】追加上次cookie信息至http request中： -b cookie5.txt
# 【6】盗链：
#     -e "${HOSTURL}/login_intro.cfm?CFID=${_CFID}&CFTOKEN=${_CFTOKEN}"
#
# 运行说明：
# 0. 环境查看：
#   0.1 查看是否安装curl（apt-get install curl）
#   0.2 查看是否支持date -d（date -d '12 days' "+%Y-%m-%d"）
# 1. crontab -e
#      # 每周一 早6:29分 开始运行脚本
#      29 6 * * 1 /root/xs-monday-6_30am.sh > ./xs-monday-log-6.30.txt
# 2. crontab -l
#

HOSTURL="https://foodiesmarketonline.property.nsw.gov.au"
REGISTERURL="${HOSTURL}/FM_login_register.cfm"
USERNAME="coolleather.sale@gmail.com"
PASSWORD="cole"
BROWSER="Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)"


# 登陆认证
echo -e "\n\n--login--"
curl -A "${BROWSER}" --insecure -d "user_name=${USERNAME}&user_password=${PASSWORD}" -D cookie5.txt "${HOSTURL}/FM_newpass2.cfm"


# 预约请求
#
# stall_weeks=1%2C1%2C376%2C88.00%2C3%2C1 映射 1 Fridays $88.00 Electricity
# stall_weeks=1%2C0%2C376%2C73.00%2C3%2C1 映射 1 Fridays $73.00 No Electricity

arr=(
  "1%2C1%2C376%2C88.00%2C3%2C1"

  "1%2C0%2C376%2C73.00%2C3%2C1"
  )

for i in ${arr[@]}; do
  echo -e "--send-to--${i}--"

  postData="stall_weeks=${i}&Submit=Finish&bformsubmitted=yes"

  recode=0
  while [[ $recode -eq 0 ]]; do
    curl -A "${BROWSER}" -e "${HOSTURL}" -b cookie5.txt -X POST --data "${postData}" "${REGISTERURL}" | grep "Registrations CLOSED"
    if [[ $? -eq 0 ]]; then
      echo "-----Registrations CLOSED-----"
      continue;
    fi

    # 本周预约还未开始
    curl -A "${BROWSER}" -e "${HOSTURL}" -b cookie5.txt -X POST --data "${postData}" "${REGISTERURL}" | grep "You have already BOOKED for this week"
    if [[ $? -eq 0 ]]; then
      echo -e "--not start--"
      continue;
    fi

    echo "---log-----"
    curl -v -A "${BROWSER}" -e "${HOSTURL}" -b cookie5.txt -X POST --data "${postData}" "${REGISTERURL}"

    # 预约成功
    curl -A "${BROWSER}" -e "${HOSTURL}" -b cookie5.txt -X POST --data "${postData}" "${REGISTERURL}" | grep "\*\* Please choose with care as we cannot change your booking or offer a refund once you have booked and paid \*\*"
    if [[ $? -eq 0 ]]; then
      echo -e "--success--"
      exit 0;
    fi

    # 缺少预约失败的判断
    # curl -A "${BROWSER}" -e "${HOSTURL}" -b cookie5.txt -X POST --data "${postData}" "${REGISTERURL}" | grep "The Spot has not been allocated"
    # recode=$?

  done
done
