from ..config.config import headers
import time
import random
import base64
import json
import urllib
import re

# 神策平台，sensorsdata2015jssdkcross参数生成

class sensors:
    def __init__(self, userAgent=''):
        if userAgent == '':
            self.userAgent = headers['User-Agent']
        else:
            self.userAgent = userAgent
        
        self.screen_height = 960
        self.screen_width  = 1920
        self.screen_size   = str(self.screen_height * self.screen_width)

    def generate_hex_number(self,digits):
        # 生成一个介于 16^digits 和 16^(digits+1) 之间的随机整数
        random_integer = random.randint(16**digits, 16**(digits+1)-1)
        # 将整数转换为十六进制字符串
        hex_number = hex(random_integer)[2:].zfill(digits)
        return hex_number
    
    def generate_user_id(self):
        user_id = self.__e() + "-" + self.__t() + "-" + self.__r() + "-" + self.screen_size + "-" + self.__e()

        return user_id
    
    # def generate_cookies(self, length):

    def generate(self,user_id=''):
        if user_id == '':
            user_id = self.generate_user_id()

        _state = {
            "distinct_id": user_id,
            "first_id": "",
            "props": {
                "$latest_traffic_source_type": "直接流量",
                "$latest_search_keyword": "未取到值_直接打开",
                "$latest_referrer": ""
            },
            "identities": {
                "$identity_cookie_id": user_id
            },
            "history_login_id": {
                "name": "",
                "value": ""
            },
            "$device_id": user_id
        }

        json_identities = json.dumps(_state['identities'], ensure_ascii=False)

        _state['identities'] = self.__N(json_identities)
        json_str_state = json.dumps(_state, ensure_ascii=False)

        sensorsdata2015jssdkcross = urllib.parse.quote(json_str_state).replace('%20','')

        return sensorsdata2015jssdkcross



    def __e(self):
        e = int(time.time() * 1000)
        t = 0
        while e == int(time.time() * 1000):
            t += 1
        return hex(e)[2:] + hex(t)[2:]

    def __t(self):
        return str(0)+self.generate_hex_number(12)
    

    def __r_e(self,e, t):
        n = 0
        for r in range(len(t)):
            n |= t[r] << 8 * r
        return e ^ n

    def __r(self):
        i = []
        a = 0
        for t in self.userAgent:
            r = ord(t)
            i.insert(0, 255 & r)
            if len(i) >= 4:
                a = self.__r_e(a, i)
                i = []
        if len(i) > 0:
            a = self.__r_e(a, i)
        
        return hex(a)[2:]

    def __N(self,e):
        t = ""
        try:
            # 使用encodeURIComponent函数对输入的字符串e进行URL编码
            encoded_str = urllib.parse.quote(e).replace('%20','')
            # 使用replace方法替换所有百分号编码为对应的字符
            replaced_str = re.sub(r'%([0-9A-F]{2})', lambda m: chr(int(m.group(1), 16)), encoded_str)
            # 使用btoa函数将替换后的字符串转换为Base64编码
            t = base64.b64encode(replaced_str.encode('utf-8')).decode('utf-8')
        except Exception as r:
            t = e
        return t