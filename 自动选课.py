import cqrk

stdID = '学号'

User = cqrk.user()
User.username = stdID
User.password = '教务系统登录密码'
User.auth()
cookies = User.loadCookie()
Jwxt = cqrk.jwxt(cookies,use_web_vpn=False)

print(Jwxt.joinCourse('乒乓球','老师名称','体育'))
