import cqrk

stdID = '用户名'

# # 使用webvpn登录，校外登录使用
# webVpn = cqrk.webvpn()
# webVpn.username = stdID
# webVpn.password = 'webVpn登录密码'
# webVpn.auth()
# cookies = webVpn.loadCookie()
# Jwxt = cqrk.jwxt(cookies,use_web_vpn=True)


# 使用webvpn登录时，use_web_vpn参数必须为True
User = cqrk.user()
User.username = stdID
User.password = '教务系统登录密码'
User.auth()
cookies = User.loadCookie()
Jwxt = cqrk.jwxt(cookies,use_web_vpn=False)

# 打印登录学生信息
print(Jwxt.get_user_name())