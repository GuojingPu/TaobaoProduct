#!/usr/bin/python3
# -*- coding:utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import pymongo
from urllib.parse import quote
from pyquery import PyQuery as pq
from config import *

brower = webdriver.Chrome()

wait = WebDriverWait(brower, 5)

client = pymongo.MongoClient(host='localhost',port=27017)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]


def index_page(page):
    """
    抓取索引页
    :param page: 索引页码
    :return: 无
    """
    print('正在爬取 ',page,' 页...')


    try:

        url = 'https://s.taobao.com/search?q='+quote(KEYWORD)+'&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20180901&ie=utf8'

        #url = quote(url)#是urllib.parse.quote（）屏蔽特殊的字符、比如如果url里面的空格
        print('url:',url)
        brower.get(url)
        if page > 1:

            search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager div.form > input')))

            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#mainsrp-pager div.form > span.btn.J_Submit')))
            search_input.clear()
            search_input.send_keys(page)
            submit.click()

        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager li.item.active > span'),str(page))
        )
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.m-itemlist .items .item')))

        get_products()
        print('over')


    except TimeoutException:
        index_page(page)
    except Exception as e:
        print(e)


def get_products():
    html = brower.page_source
    #print(html)
    doc = pq(html)
    #print(doc)
    items = doc('#mainsrp-itemlist .items .item').items()
    #print(type(items))
    #print(items)
    for item in items:
        product = {
            'image':'https://'+ item.find('.pic .img').attr('data-src'),
            'price':item.find('.price').text().strip('¥').strip(),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text(),
        }

        print(product.values())
        save_to_maongon(product)

def save_to_maongon(data):
    """
    :param data: 
    :return: 
    """

    try:
        collection.insert_one(data)
        print('存储到MongoDB成功')
    except Exception as e:
        print('存储到MongoDB失败')
        print(e)


def main():

    for page in range(1,2):
        index_page(page)
        pass

    brower.close()

if __name__ == '__main__':
    main()

