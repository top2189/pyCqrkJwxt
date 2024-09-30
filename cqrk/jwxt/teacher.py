import pickle
from typing import Union
from datetime import datetime
from bs4 import BeautifulSoup
from ..base.core import core
import requests
from ..tools.tool import *
import re
import os


class jwxtTeacher(core):
    def __init__(self,cookies=None,use_web_vpn=False):
        super().__init__()

        self.domain = self.config.domain

        if use_web_vpn:
            # 开启webvpn后可以公网访问
            self.domain = self.config.webVpnJwxt
            
        self.cookies = cookies

    def get(self,
            url: str='',
            api:str='',
            headers: dict = None
            ) -> requests.Response:
        """发送get请求"""

        if headers is None:
            headers = self.config.headers
        if url == '':
            url = self.domain + api
        response = requests.get(url=url, headers=headers, cookies=self.cookies)
        return response
    
    def post(self,
             url: str='',
             api:str='',
             data:dict={},
             headers: dict = None
             ) -> requests.Response:
        """发送post请求"""
        if headers is None:
            headers = self.config.headers
        if url == '':
            url = self.domain + api
        response = requests.post(url=url,data=data, headers=headers, cookies=self.cookies)
        return response

    # def get_user_name(self) -> str:
    #     """获取已经登录的用户名称"""
    #     html = self.get(api=self.config.jsMainPage).text
    #     user_name = html.split('姓名：</div><div class="middletopdwxxcont">')[1].split('</div>')[0]

    #     return user_name

    def get_user_name(self) -> str:
        """获取已经登录的用户名称"""
        html = self.get(api=self.config.mainPage).text
        soup = BeautifulSoup(html, 'html.parser')

        user_name = soup.find('span', attrs={'class': 'glyphicon-class ckgrxx'}).text
        
        return user_name
    
    def get_my_info(self) -> Union[dict, None]:
        """获取我的信息

        Returns:
            (dict | None): 成功返回dict，失败返回None
        """
        response = self.get(api=self.config.jsMainPage)
        
        if response.status_code != 200:
            return None
        
        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        middletopdwxxcont = soup.find_all('div', {'class': 'middletopdwxxcont'})
        data = [ttxlr.text for ttxlr in middletopdwxxcont if ttxlr.text.replace('\xa0','') != '']
        
        result = {
            'name':   data[0],
            'uid':    data[1],
            'grade':  data[2],
            'college':data[3],
        }

        return result
        