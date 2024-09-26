import cqrk

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

print(Jwxt.joinCourse('乒乓球','老师名称','体育'))
