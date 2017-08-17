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
# 【4】记录response里面的cookie信息至文件： -D cookie1.txt
# 【5】追加上次cookie信息至http request中： -b cookie1.txt
# 【6】盗链：
#     -e "${HOSTURL}/login_intro.cfm?CFID=${_CFID}&CFTOKEN=${_CFTOKEN}"
#
# 运行说明：
# 0. 环境查看：
#   0.1 查看是否安装curl（apt-get install curl）
#   0.2 查看是否支持date -d（date -d '12 days' "+%Y-%m-%d"）
# 1. crontab -e
#      # 每周一 早5:58分 开始运行脚本
#      58 5 * * 1 /root/xs-monday-6am.sh > ./xs-monday-log-6.00.txt
#      # 每周一 早6:18分 再次运行脚本
#      18 6 * * 1 /root/xs-monday-6am.sh > ./xs-monday-log-6.20.txt
# 2. crontab -l
#

if [[ -f "./success.txt" ]]; then
  rm ./success.txt
  exit 0;
fi

HOSTURL="https://rocksmarketonline.property.nsw.gov.au"
USERNAME="coolleather.sale@gmail.com"
PASSWORD="cole"
DATES_1=`date -d '12 days' "+%Y-%m-%d"`
DATES_2=`date -d '13 days' "+%Y-%m-%d"`

# Book Time
echo -e "Book time: dates_1=${DATES_1}, dates_2=${DATES_2}"

# 登陆认证
echo -e "\n\n--login--"
curl -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)" --insecure -d "user_name=${USERNAME}&user_password=${PASSWORD}" -D cookie1.txt "${HOSTURL}/newpass2.cfm"

# # 获取CFID和CFTOKEN
# s=`sed -n 8p ./cookie1.txt`
# _CFID=${s:17:7}
# s=`sed -n 9p ./cookie1.txt`
# _CFTOKEN=${s:20:52}

# # 模拟盗链
# PREURL="${HOSTURL}/login_intro.cfm?CFID=${_CFID}&CFTOKEN=${_CFTOKEN}"
# echo "--------------"
# curl -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)" -b cookie1.txt -e "${PREURL}" "${HOSTURL}/login_register.cfm"

# 预约请求
#
# stall_weeks=1%2C1%2C982%2C0%2C302%2C2 映射 1 weekend with electricity $302.00
# stall_weeks=1%2C0%2C982%2C0%2C272%2C2 映射 1 weekend $272.00
# stall_weeks=1%2C1%2C982%2C10%2C151%2C2 映射 1 Sunday with electricity $151
# stall_weeks=1%2C0%2C982%2C10%2C136%2C2 映射 1 Sunday $136
echo -e "\n\n--rush--"
arr=(
  "1%2C1%2C982%2C0%2C302%2C2"

  "1%2C0%2C982%2C0%2C272%2C2"

  "1%2C1%2C982%2C10%2C151%2C2"

  "1%2C0%2C982%2C10%2C136%2C2"
  )
for i in ${arr[@]}; do
  echo -e "\n\n--send-to--${i}--"

  recode=0
  while [[ $recode -eq 0 ]]; do
    echo -e "\n\n--Registrations CLOSED--"
    curl -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)" -b cookie1.txt -X POST --data "bFormSubmitted=yes&tenant_id_pay=&stall_weeks=$i&dates_1=%7Bd+%27${DATES_1}%27%7D&dates_2=%7Bd+%27${DATES_2}%27%7D&Submit=Finish" "${HOSTURL}/login_register.cfm" | grep "Registrations CLOSED"
    if [[ $? -eq 0 ]]; then
      continue;
    fi

    echo -e "\n\n--log--"
    curl -v -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)" -b cookie1.txt -X POST --data "bFormSubmitted=yes&tenant_id_pay=&stall_weeks=$i&dates_1=%7Bd+%27${DATES_1}%27%7D&dates_2=%7Bd+%27${DATES_2}%27%7D&Submit=Finish" "${HOSTURL}/login_register.cfm"

    curl -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)" -b cookie1.txt -X POST --data "bFormSubmitted=yes&tenant_id_pay=&stall_weeks=$i&dates_1=%7Bd+%27${DATES_1}%27%7D&dates_2=%7Bd+%27${DATES_2}%27%7D&Submit=Finish" "${HOSTURL}/login_register.cfm" | grep "PayPal - The safer, easier way to pay online."
    if [[ $? -eq 0 ]]; then
      echo -e "\n\n--complete pament--"
      echo "success" >> ./success.txt
      exit 0;
    fi

    echo -e "\n\n--The Spot has not been allocated--"
    curl -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)" -b cookie1.txt -X POST --data "bFormSubmitted=yes&tenant_id_pay=&stall_weeks=$i&dates_1=%7Bd+%27${DATES_1}%27%7D&dates_2=%7Bd+%27${DATES_2}%27%7D&Submit=Finish" "${HOSTURL}/login_register.cfm" | grep "The Spot has not been allocated"
    recode=$?

  done
done

# type=8 : SATURDAY ELECTRICITY WAITLIST
# type=3 : SUNDAY WAITLIST
# type=4 : SATURDAY WAITLIST
# curl #{HOSTURL}/login_register_waitlist.cfm?type=4&tenant_id=982
