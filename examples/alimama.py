#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

"""
以下执行文件中都有代码块
  -- 'USER SETTING'
  -- 'USER CHANGE'

正式使用时，用户需将
  -- 数据添加至 -> 'USER SETTING' 
  -- 切换注释 -> 'USER CHANGE'

Debug && Develop
  -- 用户可直接取消以下行注释运行相应脚本

日志：采用终端和文件同步记录的方式
  -- 取消终端日志输出 -> 注释 script/basic.py 中 'logger.addHandler(ch)'
  -- 取消文件日志输出 -> 注释 script/[^basic].py 中 'logger.addHandler(fh)'

"""

# # 新增导购平台
# os.system(os.path.join('.', 'script', 'create_daogou_platform.py'))

# # 新增导购平台下的推广位
# os.systemos.path.join('.', 'script', 'create_tuiguang_zone_under_daogou_platform.py'))

# # 申请定向计划
os.system(os.path.join('.', 'script', 'dingxiang_plan.py'))

# # 申请高佣计划
# os.system(os.path.join('.', 'script', 'gaoyong_plan.py'))

# # 获取QQ群列表 -- chrome-js脚本
# """os.path.join('.', 'script', 'getall_qqgroups_chromeplugin.js)"""

# # 获取QQ群列表
# os.system(os.path.join('.', 'script', 'getall_qqgroups.py'))

# # 获取导购平台下的所有推广位 -- 通过调用返回json格式数据
# os.system(os.path.join('.', 'script', 'getall_tuiguang_zones_under_daogou_platform_json.py'))

# # 获取导购平台下的所有推广位 -- 通过页面抓取
# os.system(os.path.join('.', 'script', 'getall_tuiguang_zones_under_daogou_platform.py'))

# # 获取推广统计数据
# os.system(os.path.join('.', 'script', 'tuiguang_tongji.py'))

# # 新增导购平台
# os.system(os.path.join('.', 'script', 'download_dingdan_details_excel.py'))
# 

# os.system(os.path.join('.', 'script', 'dingxiang_plan_url.py'))

os.system('pause')