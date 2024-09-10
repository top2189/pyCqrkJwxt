import pickle
from typing import Union

from bs4 import BeautifulSoup
from cqrk.core import core
from cqrk.tool import get_redirect
from urllib.parse import urlparse, parse_qs
import requests
import os

class webvpn(core):
    def __init__(self,username=None,password=None):
        super().__init__()

        self.headers  = self.config.headers
        self.username = username
        self.password = password

    def auth(self):
        if self.isCookieEnable():
            self.logger.debug('webvpn使用cookie登录成功')
        else:
            self.logger.warning('webvpn登录失效，重新登录中...')
            if not self.login():
                self.logger.warning('webvpn登录失败')
                exit()

    def isCookieEnable(self) -> bool:
        """cookies 是否可以用
        
        Returns:
            bool: cookies 是否可以用
        """
        
        if self.username is None:
            self.logger.error('学号为空')
            return False

        cookiesPath = f'{self.ROOT}/cookies/webvpn_{self.username}.pkl'

        if os.path.exists(cookiesPath):
            return self.isLogin(self.loadCookie())
        else:
            return False
        
    def loadCookie(self) -> Union[dict, None]:
        """加载本地cookie

        Returns:
            (dict | None): 本地cookie加载成功，则返回 dict
        """

        cookieFile = f'{self.ROOT}/cookies/webvpn_{self.username}.pkl'
        if not os.path.exists(cookieFile):
            self.logger.debug('loadCookie: cookies文件不存在')
            return None

        try:
            with open(cookieFile, 'rb') as f:
                return pickle.load(f)
        except:
            self.logger.error("读取cookie文件错误")
            return None
        
    def login(self,userName=None,password=None,loginType='userPassword',save_cookies=True):
        # TODO 这里后期直接通过实例化时，传用户名和密码
        # if userName is None:
        #     userName = self.username
        
        if userName is not None:
            self.username = userName
            
        if password is not None:
            self.password = password

        # if self.isLogin(self.loadCookie()):
        #     self.logger.debug('webvpn使用cookie登录成功')
            
        #     return True
        
        request = requests.Session()
        headers = self.headers

        url = 'https://auth-443.webvpn.cqrk.edu.cn:8480/cas/login?service=https%3A%2F%2Fwebvpn.cqrk.edu.cn%3A8480%2Fusers%2Fauth%2Fcas%2Fcallback%3Furl'

        serviceUri = parse_qs(urlparse(url).query)['service'][0]
        response = request.get(url=url,headers=headers)
        if response.status_code != 200:
            self.logger.warning(f'webvpn请求失败,错误码:{response.status_code}')
            return False
        
        soup = BeautifulSoup(response.text, 'html.parser')
        soup_clientId = soup.find('input', {'id': 'clientId'})
        if not soup_clientId:
            self.logger.warning(f'clientId解析错误')
            return False

        clientId = soup_clientId['value']

        postForm = {
            'client_id':clientId,
            'serviceUri':serviceUri,
            'errorMessage':'',
            'loginType':loginType,
            'userName':self.username,
            'password':self.password,
            'mobile':'',
            'mauthCode':'',
            'verificationCode':''
        }

        # 开启新的requests会话
        # request = requests.Session()


        response = request.post(url=url,data=postForm,headers=headers)
        if response.status_code != 200:
            self.logger.warning(f'webvpn的post请求失败,错误码:{response.status_code}')
            return False
        
        
        # 保存cookie登录凭证
        cookies = request.cookies.get_dict()
        response.close()

        if self.isLogin(cookies):
            if save_cookies:
                cookiesPath = f'{self.ROOT}/cookies/webvpn_{self.username}.pkl'
                if os.path.exists(cookiesPath):
                    os.remove(cookiesPath)

                with open(cookiesPath, 'wb') as f:
                    pickle.dump(cookies, f)
            
            
            self.logger.debug('webvpn登录成功')
            return True
        else:
            self.logger.debug('webvpn登录失败')
            return False
    

    def isLogin(self,cookies:dict) -> bool:
        """检查此cookie是否可以登录教务系统

        Args:
            cookies (dict): 用户的 cookies

        Returns:
            bool: 是否已经登录
        """
        
        # TODO 这里直接写weburl地址不行，会跳转过多，后期再看
        # response = requests.get('https://auth-443.webvpn.cqrk.edu.cn:8480/cas/login?service=https%3A%2F%2Fwebvpn.cqrk.edu.cn%3A8480%2Fusers%2Fauth%2Fcas%2Fcallback%3Furl', headers=self.headers, cookies=cookies)
        # print(get_redirect(self.config.webVpnUrl))
        try:
            response = requests.get(self.config.webVpnUrl, headers=self.headers, cookies=cookies)
        except requests.exceptions.TooManyRedirects:
            # 超过最大请求次数
            self.logger.debug('isLogin: 超过最大跳转次数')

            return False
        except:
            self.logger.error('网络请求失败')

        
        # TODO 删除cookie不会报错，这里可以用try捕获是否是超过最大跳转次数30次，超过则删除cookie

        if response.status_code != 200:
            return False
        
        title = BeautifulSoup(response.text, 'html.parser').title.string

        if title == '登录':
            return False
        else:
            return True
