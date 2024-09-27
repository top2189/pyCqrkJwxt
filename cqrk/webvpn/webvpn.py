import pickle
from typing import Union

from bs4 import BeautifulSoup
from ..base.core import core
from cqrk.tools.sensorsdata import sensors
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
        if self.jwxtSSO():
            self.logger.info('教务系统SSO登录成功')
        else:
            self.logger.warning('教务系统SSO登录失败')
            self.rmoveCookie()
        

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
    
    def jwxtSSO(self):
        # 单点登录
        request = requests.Session()
        cookies = self.loadCookie()

        url = 'https://jwxt-18080.webvpn.cqrk.edu.cn:8480/jsxsd/sso.jsp'
        res = request.get(url, cookies=cookies)

        
        if "href='" not in res.text:
            return True
        
        url = res.text.split("href='")[1].split("'")[0]
        res = request.get(url, cookies=cookies, allow_redirects=True)

        cookies['JSESSIONID'] = request.cookies.get_dict()['JSESSIONID']

        if '登录' in res.text:
            return False
        else:
            self.save_cookies(cookies)
            return True
        
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
        # request.headers.update(self.headers)        
        url = 'https://webvpn.cqrk.edu.cn:8480'

        res_1             = request.get(url=url,headers=headers, allow_redirects=False)
        headers['cookie'] = res_1.headers['Set-Cookie']
        url_1             = res_1.headers['Location']
        
        res_2             = request.get(url=url_1,headers=headers, allow_redirects=False)
        headers['cookie'] = res_2.headers['Set-Cookie']
        cas_cookie        = res_2.headers['Set-Cookie']
        url_2             = res_2.headers['Location']
        
        res_3             = request.get(url=url_2,headers=headers, allow_redirects=False)
        headers['cookie'] = res_3.headers['Set-Cookie']
        url               = res_3.headers['Location']

        serviceUri        = parse_qs(urlparse(url).query)['service'][0]

        # 这一次请求，用于获取clientId参数
        headers['Host']   = 'auth-443.webvpn.cqrk.edu.cn:8480'

        response          = request.get(url=url,headers=headers)
        CQRK_AUTHID       = response.headers['Set-Cookie'].split('CQRKAUTHID=')[1].split(';')[0]
        # headers['cookie'] = CQRK_AUTHID
        # request.cookies['CQRK_AUTHID'] = CQRK_AUTHID
        self.logger.debug(f'GET : /cas/login -> CQRKAUTHID: {CQRK_AUTHID}')

        # 神策数据，用户ID生成
        sensorsdata2015jssdkcross = sensors().generate()
        request.cookies['sajssdk_2015_cross_new_user'] = '1'
        request.cookies['sensorsdata2015jssdkcross']   = sensorsdata2015jssdkcross

        # print(response.cookies.get_dict())
        if response.status_code != 200:
            self.logger.warning(f'webvpn请求失败,错误码:{response.status_code}')
            return False
        
        self.logger.debug(f"Cookies: {response.cookies.get_dict()}")

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

        request.headers['Referer'] = 'https://auth-443.webvpn.cqrk.edu.cn:8480/cas/login?service=https%3A%2F%2Fwebvpn.cqrk.edu.cn%3A8480%2Fusers%2Fauth%2Fcas%2Fcallback%3Furl'

        response = request.post(url=url,data=postForm,allow_redirects=False)

        # 这里注意一下需要302重定向的响应结果，所以上面需要设置allow_redirects=False
        if response.status_code != 302:
            errorMessage = response.text.split('name="errorMessage" value="')[1].split('"')[0]
            self.logger.warning(f'{errorMessage}')
            return False
        
        # 获取webvpn回调地址
        callback_url = response.headers['Location']
        uaa_sso_sid  = response.cookies['uaa_sso_sid']

        self.logger.debug(f"Set-cookie: {response.headers['Set-cookie']}")

        callback_cookies = {
            '_astraeus_session': cas_cookie.split('_astraeus_session=')[1].split(';',1)[0],
            'sajssdk_2015_cross_new_user':'1',
            'sensorsdata2015jssdkcross': sensorsdata2015jssdkcross,
            'SERVERID':'Server1',
            'CQRKAUTHID': CQRK_AUTHID,
            'uaa_sso_sid': uaa_sso_sid
        }

        request = requests.Session()
        response = request.get(url=callback_url,cookies=callback_cookies,allow_redirects=False)

        if response.status_code != 302:
            self.logger.warning(f'callback_url 请求失败,错误码:{response.status_code}')
            return False
        
        vpn_key_update_url = response.headers['Location']
        callback_cookies['_astraeus_session'] = response.headers['Set-cookie'].split('_astraeus_session=')[1].split(';',1)[0]
        response = request.get(url=vpn_key_update_url,cookies=callback_cookies,allow_redirects=False)

        if response.status_code != 302 or response.headers['Location'] != 'https://webvpn.cqrk.edu.cn:8480/':
            self.logger.warning(f'vpn_key_update_url 请求失败,错误码:{response.status_code}')
            return False

        # 保存cookie登录凭证
        cookies = request.cookies.get_dict()
        cookies.update(callback_cookies)
        response.close()

        # sso = requests.get(url='https://jwxt-18080.webvpn.cqrk.edu.cn:8480/jsxsd/sso.jsp',cookies=cookies)
        # self.logger.debug(f"sso单点登录响应 : {sso.headers['Set-cookie']}")

        if self.isLogin(cookies):
            if save_cookies:
                self.save_cookies(cookies)

            self.logger.debug('webvpn登录成功')
        
            return True
        else:
            self.logger.debug('webvpn登录失败')
            return False
    
    def rmoveCookie(self):
        cookiesPath = f'{self.ROOT}/cookies/webvpn_{self.username}.pkl'
        if os.path.exists(cookiesPath):
            os.remove(cookiesPath)

    def save_cookies(self,cookies:dict):
        cookiesPath = f'{self.ROOT}/cookies/webvpn_{self.username}.pkl'
        if os.path.exists(cookiesPath):
            os.remove(cookiesPath)

        with open(cookiesPath, 'wb') as f:
            pickle.dump(cookies, f)

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
            response = requests.get(self.config.webVpnUrl, cookies=cookies)
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
