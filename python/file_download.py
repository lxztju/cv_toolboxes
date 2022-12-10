# -*- coding: utf-8 -*-


import requests
import os
import time
from tqdm import tqdm
from multiprocessing import Pool

# 进度条模块
def progressbar(url):
    UA = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36"

    headers = {"User-Agent": UA}
    start = time.time() #下载开始时间
    name = url.split('/')[-1] + '.mp4'
    filepath = os.path.join(target_path, name)
    response = requests.get(url, stream=True, headers=headers, timeout=100)
    size = 0    #初始化已下载大小
    chunk_size = 1024  # 每次下载的数据大小
    content_size = int(response.headers['content-length'])  # 下载文件总大小
    try:
        if response.status_code == 200:   #判断是否响应成功
            print('Start download,[File size]:{size:.2f} MB'.format(size = content_size / chunk_size /1024))   #开始下载，显示下载文件大小
            with open(filepath,'wb') as file:   #显示进度条
                for data in response.iter_content(chunk_size = chunk_size):
                    file.write(data)
                    size +=len(data)
                    print('\r'+'[下载进度]:%s%.2f%%' % ('>'*int(size*50/ content_size), float(size / content_size * 100)) ,end=' ')
        end = time.time()   #下载结束时间cle
        print('Download completed!,times: %.2f秒' % (end - start))  # 输出下载用时时间
    except:
        print('Error!')


if __name__ == '__main__':
    target_path = '../demo/down_files'
    os.makedirs(target_path, exist_ok=True)
    contents = open('../demo/urls.txt', 'r').readlines()
    num_works = 15
    pool = Pool(num_works)
    pool(progressbar, contents)
