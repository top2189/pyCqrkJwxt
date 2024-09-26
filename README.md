
<div align="center">
    <h1>重庆人科教务系统助手（<span style="color:pink">pyCqrkJwxt</span>）</h1>
    <p style="color:green">使用Python3来实现自动化调用教务系统Api接口</p>
    <p style="color:orange">注意：本代码仅用于学习Python爬虫</p>
    <p style="color:orange">任何人或组织使用本项目的代码进行的任何违法行为与本人无关</p>
</div>


## 安装
直接通过`pip`指令，安装项目所需依赖的包文件。
```sh
pip install -r requirements.txt
```


## 登录
登录教务系统，这里我们可以通过webvpn来登录，也可以通过内网直接登录教务系统。

`导入包文件，并实例化对象`
```python
import cqrk
```

#### `内网登录（需要连接校园网）`
```python
User = cqrk.user()
User.username = '用户名'
User.password = '密  码'
User.auth()
cookies = User.loadCookie()
Jwxt = cqrk.jwxt(cookies,use_web_vpn=False)
```

#### `外网登录（webvpn登录）`
```python
webVpn = cqrk.webvpn()
webVpn.username = '用户名'
webVpn.password = '密  码'
webVpn.auth()
cookies = webVpn.loadCookie()
Jwxt = cqrk.jwxt(cookies,use_web_vpn=True)
```

## 相关接口
#### [1.获取学生信息](#item1)
#### [2.获取登录用户名称](#item2)
#### [3.学生手动抢课](#item3)
#### [4.获取公选课列表](#item4)
#### [5.获取公选课里面的课程列表](#item5)
#### [6.获取学生课程成绩](#item6)
#### [7.获取当前是第几教学周](#item7)
#### [8.获取当前学期ID](#item8)
#### [9.获取当前学期课程表](#item9)
#### [10.查询班级课表](#item10)
#### [11.查询教师课表](#item11)
#### [12.获取课程表ID](#item12)
#### [13.下载学生课程表](#item13)


<span id="item1"></span>
#### `1.获取学生信息`
```python
print(Jwxt.get_student_info())
```


<span id="item2"></span>
#### `2.获取登录用户名称`
```python
print(Jwxt.get_user_name())
```

<span id="item3"></span>
#### `3.学生手动抢课`
```python
Jwxt.joinCourse('乒乓球','老师名称','体育')
```


<span id="item4"></span>
#### `4.获取公选课列表`
```python
print(Jwxt.get_select_course_lists())
```

<span id="item5"></span>
#### `5.获取公选课里面的课程列表`
```python
print(Jwxt.get_course_lists(jx0502zbid))
```

<span id="item6"></span>
#### `6.获取学生课程成绩`
```python
# show_all=True 显示所有课程
print(Jwxt.getCourseScore(show_all=True))
```

<span id="item7"></span>
#### `7.获取当前是第几教学周`
```python
# show_all=True 显示所有课程
print(Jwxt.getNowWeek())
```

<span id="item8"></span>
#### `8.获取当前学期ID`
```python
print(Jwxt.getSheetID())
```

<span id="item9"></span>
#### `9.获取当前学期课程表`
```python
courseSheet = Jwxt.getCourseSheet(parse=True,onlyName=True)

# 定义表头
headers = ['周一', '周二', '周三','周四','周五','周六','周日']
data = [*zip(*courseSheet)]

# 使用tabulate生成表格
table = tabulate(data, headers=headers, tablefmt='grid')

# 输出表格
print(table)
```

<span id="item10"></span>
#### `10.查询班级课表`
```python
print(Jwxt.getClassCourse(
    college_name='学院名称',
    grade='2023',
    major_name='专业名称',
    classes='1班'
))
```

<span id="item11"></span>
#### `11.查询教师课表`
```python
print(Jwxt.getTeacherCourse(teacherName='教师姓名'))
```


<span id="item12"></span>
#### `12.获取课程表ID`
```python
print(Jwxt.get_kbjcmsid())
```

<span id="item13"></span>
#### `13.下载学生课程表`
```python
print(Jwxt.downloadSheet(save_dir=''))
```
