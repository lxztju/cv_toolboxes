#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import os
import re
import sys
import urllib
import json
import socket
import urllib.request
import urllib.parse
import urllib.error
# 设置超时
from joblib import delayed
from joblib import Parallel

import time

timeout = 5
socket.setdefaulttimeout(timeout)


class Crawler:


    # 获取图片url内容等
    # t 下载图片时间间隔
    def __init__(self, t=0.1):
        self.time_sleep = t
        self.__amount = 0
        self.__start_amount = 0
        self.__counter = 0
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0',
                   'Cookie': ''}
        self.__per_page = 100

    # 获取后缀名
    @staticmethod
    def get_suffix(name):
        m = re.search(r'\.[^\.]*$', name)
        if m.group(0) and len(m.group(0)) <= 5:
            return m.group(0)
        else:
            return '.jpg'

    @staticmethod
    def handle_baidu_cookie(original_cookie, cookies):
        """
        :param string original_cookie:
        :param list cookies:
        :return string:
        """
        if not cookies:
            return original_cookie
        result = original_cookie
        for cookie in cookies:
            result += cookie.split(';')[0] + ';'
        result.rstrip(';')
        return result

    # 保存图片
    def save_image(self, rsp_data, word):
        if not os.path.exists("./" + word):
            os.mkdir("./" + word)
        # 判断名字是否重复，获取图片长度
        self.__counter = len(os.listdir('./' + word)) + 1
        for image_info in rsp_data['data']:
            try:
                if 'replaceUrl' not in image_info or len(image_info['replaceUrl']) < 1:
                    continue
                obj_url = image_info['replaceUrl'][0]['ObjUrl']
                thumb_url = image_info['thumbURL']
                url = 'https://image.baidu.com/search/down?tn=download&ipn=dwnl&word=download&ie=utf8&fr=result&url=%s&thumburl=%s' % (urllib.parse.quote(obj_url), urllib.parse.quote(thumb_url))
                time.sleep(self.time_sleep)
                suffix = self.get_suffix(obj_url)
                # 指定UA和referrer，减少403
                opener = urllib.request.build_opener()
                opener.addheaders = [
                    ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'),
                ]
                urllib.request.install_opener(opener)
                # 保存图片
                filepath = './%s/%s' % (word, str(self.__counter) + str(suffix))
                urllib.request.urlretrieve(url, filepath)
                if os.path.getsize(filepath) < 5:
                    print("下载到了空文件，跳过!")
                    os.unlink(filepath)
                    continue
            except urllib.error.HTTPError as urllib_err:
                print(urllib_err)
                continue
            except Exception as err:
                time.sleep(1)
                print(err)
                print("产生未知错误，放弃保存")
                continue
            else:
                print("图片+1,已有" + str(self.__counter) + "张图片")
                self.__counter += 1
        return

    # 开始获取
    def get_images(self, word):
        search = urllib.parse.quote(word)
        # pn int 图片数
        pn = self.__start_amount
        while pn < self.__amount:
            url = 'https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=' \
                  'result&queryWord=%s&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=&hd=' \
                  '&latest=&copyright=&word=%s&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1&fr=&expermode=' \
                  '&force=&pn=%s&rn=%d&gsm=1e&1594447993172=' % (search, search, str(pn), self.__per_page)
            # 设置header防403
            try:
                time.sleep(self.time_sleep)
                req = urllib.request.Request(url=url, headers=self.headers)
                page = urllib.request.urlopen(req)
                self.headers['Cookie'] = self.handle_baidu_cookie(self.headers['Cookie'], page.info().get_all('Set-Cookie'))
                rsp = page.read()
                page.close()
            except UnicodeDecodeError as e:
                print(e)
                print('-----UnicodeDecodeErrorurl:', url)
            except urllib.error.URLError as e:
                print(e)
                print("-----urlErrorurl:", url)
            except socket.timeout as e:
                print(e)
                print("-----socket timout:", url)
            try:
                # 解析json
                rsp_data = json.loads(rsp, strict=False)
                if 'data' in rsp_data:
                    self.save_image(rsp_data, word)
                    # 读取下一页
                    pn += self.__per_page
            except:
                pn += self.__per_page
                continue
        print("下载任务结束")
        return

    def start(self, word, total_page=100, start_page=1, per_page=100):
        """
        爬虫入口
        :param word: 抓取的关键词
        :param total_page: 需要抓取数据页数 总抓取图片数量为 页数 x per_page
        :param start_page:起始页码
        :param per_page: 每页数量
        :return:
        """
        self.__per_page = per_page
        self.__start_amount = (start_page - 1) * self.__per_page
        self.__amount = total_page * self.__per_page + self.__start_amount
        self.get_images(word)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--word", type=str, help="抓取关键词列表， txt格式")
    parser.add_argument("-tp", "--total_page", default=30, type=int, help="需要抓取的总页数")
    parser.add_argument("-sp", "--start_page", default=1, type=int, help="起始页数")
    parser.add_argument("-pp", "--per_page", default=50, type=int, help="每页大小", choices=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100], nargs='?')
    parser.add_argument("-d", "--delay", type=float, help="抓取延时（间隔）", default=0.05)
    args = parser.parse_args()

    crawler = Crawler(args.delay)

    # txt_contents = open(args.word, 'r').readlines()
    # words = []
    # for line in txt_contents:
    #     name = line.strip()
    #     words.append(name)
    words = ['湖泊河流','水果', '啤酒', '红酒','白酒', '数码产品', '相机', '截图', '建筑', '吉他', '架子鼓', '手风琴', '古筝', '活动聚会', '其他']
    print(words)
    Parallel(n_jobs=15)(delayed(crawler.start)(
        word) for word in words[::-1])
    #for word in words[::-1]:
    #    crawler.start(word, args.total_page, args.start_page, args.per_page)
