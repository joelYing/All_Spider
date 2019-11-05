#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 19/3/12
#

import os
import re
from Crypto.Cipher import AES
import requests

"""
一、Python os.system()出现乱码
该情况可能是由于pycharm编码设置导致的问题，在"File--Setting--FileEncodings--GlobalEncoding"中修改编码为GBK即可

二、TypeError: Object type class 'str' cannot be passed to C code
--> https://blog.csdn.net/zhangpeterx/article/details/96351648
--> https://www.cnblogs.com/huangjianting/p/8666446.html

三、from Crypto.Cipher import AES
--> https://www.cnblogs.com/zhangningyang/p/9117626.html
"""


class KoKoJia:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        }
        self.cookie = {
            'Cookie': 'Hm_lvt_f530f7624f8a05758b78e413af3d70ca=1572921480; Hm_lvt_69a9e7b64ab4ee86e58df7fde25d232a=1572921480; PHPSESSID=p3hk075mhc4hg91gnuug9emkh1; kkj_path=33a2e38c6d7050120ae0a0b025b1a6fe; kkj_userid=10524698; kkj_key=215e6c1c04e698d2fdcc0dc1765a900d; course_player_lesson=51931; course_player_time=577; Hm_lpvt_f530f7624f8a05758b78e413af3d70ca=1572922143; Hm_lpvt_69a9e7b64ab4ee86e58df7fde25d232a=1572922143; issldd=y'
        }

    @staticmethod
    def mkd():
        # 创建存放ts文件以及mp4文件的文件夹
        paths = ['D:\\Python\\PycharmProject\\KoKoJia', 'D:\\Python\\PycharmProject\\FinalKoKoJia']
        for path in paths:
            f = os.path.exists(path)
            if not f:
                os.makedirs(path)
                print('make file success...')
            else:
                print('file already exists...')

    def gethtml(self):
        s = requests.session()
        r1 = s.get("http://www.kokojia.com/course-3643.html")
        r1.encoding = "utf-8"
        lesson_url_list = re.findall(r'<span class="f-fl f-thide ks">(.*?)</span>.*?<h4><a class='
                                     r'"f-fl f-thide ksname" title="(.*?)" href="(.*?)".*?>.*?</h4>', r1.text, re.S)
        for i in range(1, len(lesson_url_list) + 1):
            ts_path = 'D:\\Python\\PycharmProject\\KoKoJia\\{}'.format(i)
            f = os.path.exists(ts_path)
            if not f:
                os.makedirs(ts_path)
                print('make file success...')
            else:
                print('file already exists...')
            # 构造访问每个视频的信息，处理部分非常规标题
            title = lesson_url_list[i - 1][0] + lesson_url_list[i - 1][1]
            lesson_url = lesson_url_list[i - 1][2]
            print(title, lesson_url)
            # 判断是否已存在最终合成视频，用于中断后继续操作
            final_path = "D:\\Python\\PycharmProject\\FinalKoKoJia\\{}.mp4".format(i)
            f = os.path.exists(final_path)
            if not f:
                r2 = s.get(lesson_url, headers=self.headers, cookies=self.cookie)
                r2.encoding = "utf-8"
                m3u8_url = re.findall('"name":".*?", "url":"(.*?)"', r2.text, re.S)
                # print(m3u8_url)
                url_head = re.sub('kokojia_\d+\.m3u8', '', m3u8_url[0])
                r_m3u8 = s.get(m3u8_url[0])
                uri_key = re.findall('EXT-X-KEY:METHOD=AES-128,URI="(.*?)"', r_m3u8.text, re.S)
                key = s.get(uri_key[0], cookies=self.cookie).text
                print(key)
                # 得到m3u8文件内容
                ts_tail_list = re.findall('#EXTINF:.*?,(.*?)\.ts', r_m3u8.text, re.S)
                nums = len(ts_tail_list)
                for num in range(1, nums + 1):
                    # if num < 100:
                    # 请求m3u8文件中，每个ts链接
                    ts_url = url_head + ts_tail_list[num - 1].replace('\n', '') + '.ts'
                    print(ts_url)
                    vi = bytes('{:016}'.format(num - 1).encode('utf-8'))
                    # vi = bytes('0b' + '{:014b}'.format(num - 1))
                    # print(key, vi)
                    cryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, vi)
                    res_ts = s.get(ts_url)
                    b_num = num
                    if num < 10:
                        b_num = '00' + str(num)
                    if 9 < num < 100:
                        b_num = '0' + str(num)
                    with open('D:\\Python\\PycharmProject\\KoKoJia\\{}\\{}.ts'.format(i, b_num), 'wb') as f:
                        f.write(cryptor.decrypt(res_ts.content))
                        print('OK')
                    # break
                # 在为视频命名时注意文件名不能包含空格
                os.system("copy /b D:\\Python\\PycharmProject\\KoKoJia\\{}\\*.ts "
                          "D:\\Python\\PycharmProject\\FinalKoKoJia\\{}.mp4".format(i, i))
                print('make vedio success...')
            else:
                print('vedio already exists...')
            # break


if __name__ == '__main__':
    kokojia = KoKoJia()
    kokojia.mkd()
    kokojia.gethtml()
