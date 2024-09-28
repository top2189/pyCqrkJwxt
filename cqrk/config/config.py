# 是否开启DEBUG模式，开启后会输出调试信息
DEBUG = True

# keyStr 可以更换，用于AES加密
# AES 加密的key通过md5(get_serial_number()+keyStr)得到，截取16位
keyStr = "&)9ssa01k"

# 通用请求头
headers = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
   "Accept-Encoding": "gzip, deflate, br, zstd",
   "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"  # 伪造浏览器 User-Agent
}

# 相关接口域名
domain          = 'http://192.168.10.150:18080'
webVpnUrl       = 'https://webvpn.cqrk.edu.cn:8480'
webVpnJwxt      = 'https://jwxt-18080.webvpn.cqrk.edu.cn:8480'

# 相关接口方法
jsMainPage      = '/jsxsd/framework/jsMain_new.jsp'


mainPage        = '/jsxsd/framework/xsMain_new.jsp'
getLoginScode   = '/Logon.do?method=logon&flag=sess'
loginPost       = '/Logon.do?method=logon'
classTable      = '/jsxsd/xskb/xskb_list.do'
xskbPrint       = '/jsxsd/xskb/xskb_print.do'
cjcxList        = '/jsxsd/kscj/cjcx_list'
teacherTable    = '/jsxsd/kbcx/kbxx_teacher_ifr'
classData       = '/jsxsd/kbcx/kbxx_xzb'
kbxx_xzb_ifr    = '/jsxsd/kbcx/kbxx_xzb_ifr'

getZyByAjax     = '/jsxsd/kbcx/getZyByAjax'

classSchedule = [
   # 上午课程
    (1,2),
    (3,5),
   # 下午课程
    (6,7),
    (8,9),
   # 晚上课程
    (10,11),
    (12,13),
]

classScheduleTime = [
   '08:00-09:40',
   '09:50-12:25',
   '14:30-16:10',
   '16:20-18:00',
   '19:00-20:40',
   '20:50-22:30'
]

classTime = [
   (28800,31500),
   (32100,34800),
   (35400,38100),
   (38700,41400),
   (42000,44700),
   (52200,54900),
   (55500,58200),
   (58800,61500),
   (62100,64800),
   (68400,71100),
   (71700,74400),
   (75000,77700),
   (78300,81000)
]
