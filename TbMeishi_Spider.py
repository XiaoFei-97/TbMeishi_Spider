#!/usr/bin/env python
# coding=utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq
from config import *
import re
import pymongo

# 创建一个MongoDB对象
client = pymongo.MongoClient(MONGO_URL)

# 创建一个数据库，注意是[]而不是()
db = client[MONGO_DB]

# browser = webdriver.Chrome()
# 无界面浏览器
browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)

# 十秒内寻找元素失败，将报出TimeoutException异常
wait = WebDriverWait(browser, 10)

# 设置PlantomJS的窗口大小，可能会影响内容下载
browser.set_window_size(1400, 900)

def search():
    """
        作用：通过关键字搜索得到搜索内容第一页产品信息，并返回搜索内容共计页码
    """
    print('正在搜索')
    try: 
        browser.get('https://www.taobao.com')
        # print(browser.page_source)

        # 获取input输入框对象
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))  
        )

        # 获取button提交对象
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button"))
        )
        
        # KEYWORD是config.py文件中定义的搜索关键字，可修改
        input.send_keys(KEYWORD)

        # 点击button提交按钮
        submit.click()
        
        # 通过CSS_SELECTOR选择器获取total页码
        total_page = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.total"))  
        )

        # 解析页面内容，并将数据保存至MongoDB中
        get_products()
        return total_page.text

    except TimeoutException:

        # 出现超时访问就重新调用一次search
        return search()

def next_page(page_number):
    """
        作用：作人为翻页功能，并得到该页产品信息
        page_number：循环的页码，将页码写入input框中
    """
    print('正在翻页', page_number)
    try:
        # 获取input输入框对象
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))  
        )
        
        # 获取button提交对象
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div > div > div > div.form > span.btn.J_Submit"))
        )

        # 将input框清空
        input.clear()

        # 向input框中输入页码
        input.send_keys(page_number)

        # 点击button提交按钮
        submit.click()

        wait.until(
            # 验证输入框内的页码是否为当前高亮页码，如果是，则继续执行
            # text参数是否在该span元素内，此处需要注意text的参数位置
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number))
        )

        # 获取产品信息并保存至MongoDB
        get_products()

    except TimeoutException:
        # 超时异常，则继续解析该页
        next_page(page_number)
    
def get_products():
    """
        作用：通过页面源代码，将产品信息保存至MongoDB中
    """
    # 通过CSS_SELECTOR选择器，验证页面中是否存在产品对象
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-itemlist .items .item"))
    )

    # 拿到页面源码
    html = browser.page_source

    # 通过pyquery找到产品对象
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()

    # 遍历每个产品对象，组建数据内容
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        # print(product)
        # 将组建好的每个产品信息保存至MongoDB
        save_to_mongo(product)

def save_to_mongo(result):
    """
        作用：将信息保存至MongoDB中
    """
    try:
        if db[MONGO_TABLE].insert(result):
            print('Successfully save to MongoDB', result)
    except Exception:
        print('Failed save to MongoDB', result)
    
def TbMeishi_Spider():
    """
        作用：淘宝美食爬取调度器
    """
    try:
        total_page = search()

        # 通过正则将search返回的total页码内容解析成数字形式
        pattern = re.compile('(\d+)')
        total_page = int(pattern.search(total_page).group(1))
        # print(total_page)

        # 遍历页码，传入next_page函数中，做整站爬取
        for i in range(2, total_page + 1):
            next_page(i)
    except Exception:
        print('有错误产生...')
    finally:
        browser.close()


if __name__ == "__main__":
    TbMeishi_Spider()
