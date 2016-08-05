#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re
import time
import os.path

try:
    from PIL import Image
except:
    pass
from bs4 import BeautifulSoup
import json

# 构造 Request headers
# 登陆的url地址
logn_url = 'http://www.zhihu.com/#signin'

session = requests.session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
}

content = session.get(logn_url, headers=headers).content
soup = BeautifulSoup(content, 'html.parser')


def getxsrf():
    return soup.find('input', attrs={'name': "_xsrf"})['value']


# 获取验证码
def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha


def isLogin():
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, allow_redirects=False).status_code
    if int(x=login_code) == 200:
        return True
    else:
        return False


def login(secret, account):
    # 通过输入的用户名判断是否是手机号
    if re.match(r"^1\d{10}$", account):
        print("手机号登录 \n")
        post_url = 'http://www.zhihu.com/login/phone_num'
        postdata = {
            '_xsrf': getxsrf(),
            'password': secret,
            'remember_me': 'true',
            'phone_num': account,
        }
    else:
        print("邮箱登录 \n")
        post_url = 'http://www.zhihu.com/login/email'
        postdata = {
            '_xsrf': getxsrf(),
            'password': secret,
            'remember_me': 'true',
            'email': account,
        }
    try:
        # 不需要验证码直接登录成功
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = login_page.text
        print(login_page.status)
        print(login_code)
    except:
        # 需要输入验证码后才能登录成功
        postdata["captcha"] = get_captcha()
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = eval(login_page.text)
        print(login_code['msg'])


# 获取详细信息
# def getdetial():
#     followees_url = 'https://www.zhihu.com/people/GitSmile/followees'
#     followees_headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
#         'Referer': 'https://www.zhihu.com/people/GitSmile/about',
#         'Upgrade-Insecure-Requests': '1',
#         'Accept-Encoding': 'gzip, deflate, sdch, br'
#     }
#
#     myfollowees = session.get(followees_url, headers=followees_headers)
#     mysoup = BeautifulSoup(myfollowees.content, 'html.parser')
#     print(mysoup.find('span', attrs={'class': 'zm-profile-section-name'}).text)
#     for result in mysoup.findAll('a', attrs={'class': 'zm-item-link-avatar'}):
#         print(result.get('title'))
#         href = str(result.get('href'))
#         print(mysoup.find('a', attrs={'href': href + '/followers'}).text)
#         print(mysoup.find('a', attrs={'href': href + '/asks'}).text)
#         print(mysoup.find('a', attrs={'href': href + '/answers'}).text)
#         print(mysoup.find('a', attrs={'href': href, 'class': 'zg-link-gray-normal'}).text + '\n')
# 获取所有关注的人的信息
def getallview():
    nums = 26  # 这个是我关注的人数
    followees_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
        'Referer': 'https://www.zhihu.com/people/GitSmile/followees',
        'Origin': 'https://www.zhihu.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'CG - Sid': '57226ad5 - 793b - 4a9d - 9791 - 2a9a17e682ef',
        'Accept': '* / *'

    }
    count = 0
    for index in range(0, nums):
        fo_url = 'https://www.zhihu.com/node/ProfileFolloweesListV2'
        m_data = {
            'method': 'next',
            'params': '{"offset":' + str(
                index) + ',"order_by":"created","hash_id":"de2cb64bc1afe59cf8a6e456ee5eaebc"}',
            '_xsrf': str(getxsrf())
        }
        result = session.post(fo_url, data=m_data, headers=followees_headers)
        dic = json.loads(result.content.decode('utf-8'))
        li = dic['msg'][0]
        mysoup = BeautifulSoup(li, 'html.parser')
        for result in mysoup.findAll('a', attrs={'class': 'zm-item-link-avatar'}):
            print(index + 1)
            print(result.get('title'))
            href = str(result.get('href'))
            print(mysoup.find('a', attrs={'href': href + '/followers'}).text)
            print(mysoup.find('a', attrs={'href': href + '/asks'}).text)
            print(mysoup.find('a', attrs={'href': href + '/answers'}).text)
            print(mysoup.find('a', attrs={'href': href, 'class': 'zg-link-gray-normal'}).text + '\n')
            count += 1
    print('一共关注了 %d人' % count)


if __name__ == '__main__':

    if isLogin():
        print('您已经登录')
    else:
        account = input('请输入你的用户名\n>  ')
        secret = input("请输入你的密码\n>  ")
        login(secret, account)
    getallview()
    # getdetial()
