
<div align="center">
    <h1>重庆人科教务系统助手（CqrkJwxt）</h1>
    <p>使用Python3来实现自动化调用教务系统Api接口</p>
    <p>目前支持登录功能，下载课程表，解析课程表等相关功能</p>
    <p>注意：本代码仅用于学习Python爬虫</p>
    <p>任何人或组织使用本项目的代码进行的任何违法行为与本人无关</p>
</div>


## 安装
直接通过pip指令，安装对应包文件。
```sh
pip install -r requirements.txt
```


## 使用
登录教务系统
```python
from cqrk.user import user
from cqrk.jwxt import jwxt

username = '学号'
password = '密码'

User = user(username,password)
Jwxt = jwxt(User.loadCookie())

if not User.isCookieEnable():
    if User.login():
        print('登录成功')

studentInfo = Jwxt.get_student_info()
print(f"你好，{studentInfo['name']}。")
```

解析学生课表
```python
from tabulate import tabulate
from cqrk.jwxt import jwxt
from cqrk.user import user

username = '学号'
password = '密码'

User = user(username,password)

if not User.login() : exit()

Jwxt = jwxt(User.loadCookie())
courseSheet = Jwxt.getCourseSheet(parse=True,onlyName=True)

# 定义表头
headers = ['周一', '周二', '周三','周四','周五','周六','周日']
data = [*zip(*courseSheet)]

# 使用tabulate生成表格
table = tabulate(data, headers=headers, tablefmt='grid')

# 输出表格
print(table)


```