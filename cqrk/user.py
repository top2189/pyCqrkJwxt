from cqrk.core import core


from typing import Union
import requests
from bs4 import BeautifulSoup
import pickle
import os
import re

class user(core):
    def __init__(self,username=None,password=None,use_web_vpn=False):
        """ 用户登录类

        Args:
            username (str, optional): 学生学号.
            password (str, optional): 登录密码.
            use_web_vpn (bool, optional): 是否开启webVpn模式.
        """
        super().__init__()

        self.username = username
        self.password = password

        self.webVpn = use_web_vpn
        self.domain = self.config.domain

        if self.username:
            self.cookie = 'webvpn_'+self.username
        else:
            self.cookie = self.username


        if self.webVpn:
            # 开启webvpn后可以公网访问
            self.domain = self.config.webVpnJwxt
    
    def auth(self):
        self.cookie = 'webvpn_'+self.username
        if not self.isCookieEnable():
            self.logger.warning('登录失效，重新登录中...')
            
            for i in range(3):
                if self.login():
                    return True
                else:
                    self.logger.warning(f'第{i+1}次登录失败，重新尝试中...')
            
            exit()

    def login(self,
              user=None,
              password=None,
              use_cookie=True,
              JSESSIONID=None
        ) -> bool:
        """登录教务系统

        Args:
            user (str, optional): 学号. Defaults to None.
            password (str, optional): 登录密码. Defaults to None.
            use_cookie (bool, optional): 是否直接使用cookie登录. Defaults to True.
            JSESSIONID (str, optional): 抓包获取cookie中的JSESSIONID. 传入可直接使用此凭证登录

        Returns:
            bool: 是否登录成功
        """


        if user is not None:
            self.username = user

        if password is not None:
            self.password = password

        if self.username is None:
            self.logger.debug('用户名不能为空')
            return False
        
        if JSESSIONID is not None:
            if self.webVpn:
                self.logger.warning('在webVpn下，不能传入JSESSIONID参数')
                self.cookie = 'webvpn_'+self.username
                return False
            
            # 使用 JSESSIONID 登录
            cookies = {
                'JSESSIONID':JSESSIONID,
                'Path':'/',
                'name': 'value'
            }

            if self.isLogin(cookies):
                self.resetCookie(JSESSIONID)
                return True
            else:
                return False


        if use_cookie:
            # 使用本地 cookie 登录
            if self.isCookieEnable():
                return True

            cookies = self.loadCookie()
        else:
            # 使用账号密码登录
            cookies = None
        
        if self.webVpn:
            cookies = self.loadCookie()

        if cookies is None and self.password is None:
            self.logger.debug('密码不能为空')
            return False

        if self.isCookieExists():
            if self.webVpn:
                self.logger.debug('使用webvpn登录教务系统中')
            
            else:
                self.logger.debug('cookie 已过期，正在重新登录中')
                # 删除过期 Cookie
                if not self.rmCookie():
                    self.logger.error('过期 cookie 删除失败')
                    return False
        else:
            self.logger.debug('正在登录中')

        request = requests.Session()
        dataStr = request.post(f'{self.domain}{self.config.getLoginScode}', headers=self.config.headers, cookies=cookies).text
        scode   = dataStr.split("#")[0]
        code    = f"{self.username}%%%{self.password}"
        sxh     = dataStr.split("#")[1]
        encoded = ""

        for i in range(0, len(code)):
            if i < 20:
                encoded += code[i] + scode[:int(sxh[i])]
                scode = scode[int(sxh[i]):]
            else:
                encoded += code[i:]
                break
            
        data = {
            "userAccount": "",
            "userPassword": "",
            "encoded":encoded
        }


        if self.webVpn:
            response = request.post(f'{self.domain}{self.config.loginPost}', headers=self.config.headers,cookies=cookies, data=data)
        else:
            response = request.post(f'{self.domain}{self.config.loginPost}', headers=self.config.headers, data=data)

        if response.status_code != 200:
            self.logger.warning(f'登录失败，错误码：{response.status_code}')
            return False
        
        # 保存cookie登录凭证
        cookies2 = request.cookies.get_dict()

        if self.webVpn:
            cookies.update(cookies2)
        else:
            cookies = cookies2

        response.close()


        if self.isLogin(cookies):
            cookiesPath = f'{self.ROOT}/cookies/{self.cookie}.pkl'
            if os.path.exists(cookiesPath):
                os.remove(cookiesPath)

            with open(cookiesPath, 'wb') as f:
                pickle.dump(cookies, f)
            
            return True
        else:
            return False
        
    
    def loadCookie(self) -> Union[dict, None]:
        """加载本地cookie

        Returns:
            (dict | None): 本地cookie加载成功，则返回 dict
        """
        if self.username is None:
            return None
        
        self.cookie = 'webvpn_'+self.username

        cookieFile = f'{self.ROOT}/cookies/{self.cookie}.pkl'
        if not os.path.exists(cookieFile):
            return None

        try:
            with open(cookieFile, 'rb') as f:
                return pickle.load(f)
        except:
            self.logger.error("读取cookie文件错误")
            return None
        
    def isCookieExists(self) -> bool:
        """检查cookie文件是否存在

        Returns:
            bool: 是否存在cookie文件
        """
        if os.path.exists(f'{self.ROOT}/cookies/{self.cookie}.pkl'):
            return True
        else:
            return False
    
    def rmCookie(self) -> bool:
        """删除cookie文件

        Returns:
            bool: 是否删除成功
        """
        if self.username is None:
            return False
        
        cookieFile = f'{self.ROOT}/cookies/{self.cookie}.pkl'
        if not self.isCookieExists():
            return True
                    
        try:
            os.remove(cookieFile)
            self.logger.debug('cookie 成功删除')
            return True
        except OSError:
            self.logger.error("文件未找到或无法删除")
            return False


    def isCookieEnable(self) -> bool:
        """cookies 是否可以用
        
        Returns:
            bool: cookies 是否可以用
        """
        
        if self.username is None:
            self.logger.error('学号为空')
            return False
        

        if os.path.exists(f'{self.ROOT}/cookies/{self.cookie}.pkl'):
            return self.isLogin(self.loadCookie())
        else:
            self.logger.debug('cookies文件不存在')
            return False
    
    def isLogin(self,cookies:dict) -> bool:
        """检查此cookie是否可以登录教务系统

        Args:
            cookies (dict): 用户的 cookies

        Returns:
            bool: 是否已经登录
        """
        classTable   = f'{self.domain}{self.config.classTable}'
        response   = requests.get(classTable, headers=self.config.headers, cookies=cookies)
        if response.status_code != 200:
            return False

        title = BeautifulSoup(response.text, 'html.parser').title.string

    
        if title == '登录':
            return False
        else:
            return True



    def resetCookie(self,JSESSIONID:str):
        """ 重置本地保存的cookie，
            该方法一般用于浏览器抓包后，
            直接传入JSESSIONID，
            已经登录的设备，
            不会被强制下线

        Args:
            JSESSIONID (str): 浏览器抓包后的JSESSIONID
        """
        if self.webVpn:
            self.logger.warning('此方法只能在非webvpn下使用')
            return
        
        file = f'{self.ROOT}/cookies/{self.cookie}.pkl'

        cookies = {
            'JSESSIONID':JSESSIONID,
            'Path':'/',
            'name': 'value'
        }

        self.rmCookie()

        with open(file, 'wb') as file:
            pickle.dump(cookies, file)
        