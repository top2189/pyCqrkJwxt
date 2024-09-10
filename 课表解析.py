import cqrk
from tabulate import tabulate

stdID = '学号'

# 使用webvpn登录，校外登录使用
webVpn = cqrk.webvpn()
webVpn.username = stdID
webVpn.password = 'webvpn密码'
webVpn.auth()

# 使用webvpn登录时，use_web_vpn参数必须为True
User = cqrk.user(use_web_vpn=True)
User.username = stdID
User.password = '教务系统密码'
User.auth()


Jwxt = cqrk.jwxt(User.loadCookie(),use_web_vpn=True)


courseSheet = Jwxt.getCourseSheet(parse=True,onlyName=True)

# 定义表头
headers = ['周一', '周二', '周三','周四','周五','周六','周日']
data = [*zip(*courseSheet)]

# 使用tabulate生成表格
table = tabulate(data, headers=headers, tablefmt='grid')

# 输出表格
print(table)

# 保存表格到文件
# Jwxt.downloadSheet(save_dir='./')