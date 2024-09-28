
[_返回首页_](../README.md)

## 登录
登录教务系统，这里我们可以通过webvpn来登录，也可以通过内网直接登录教务系统。

`导入包文件`
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
Jwxt = cqrk.jwxtStudent(cookies)
```

#### `外网登录（webvpn登录）`
```python
webVpn = cqrk.webvpn()
webVpn.username = '用户名'
webVpn.password = '密  码'
webVpn.auth()
cookies = webVpn.loadCookie()
Jwxt = cqrk.jwxtStudent(cookies,use_web_vpn=True)
```

## 相关接口
#### [1.获取登录姓名](#item1)
#### [2.获取学生信息](#item2)
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
#### `1.获取登录姓名 -> str`
```python
Jwxt.get_user_name()
```

<span id="item2"></span>
#### `2.获取学生信息 -> dict`
```python
Jwxt.get_my_info()
```

<span id="item3"></span>
#### `3.学生手动抢课 -> bool`
```python
try:
    Jwxt.joinCourse('乒乓球','老师名称','体育')
except Exception as e:
    print(e)
```


<span id="item4"></span>
#### `4.获取公选课列表 -> list`
```python
Jwxt.get_select_course_lists()
```

<span id="item5"></span>
#### `5.获取公选课里面的课程列表 -> list`
```python
Jwxt.get_course_lists(jx0502zbid)
```

<span id="item6"></span>
#### `6.获取学生课程成绩 -> dict`
```python
# show_all=True 显示所有课程
Jwxt.getCourseScore(show_all=True)
```

<span id="item7"></span>
#### `7.获取当前是第几教学周 -> int`
```python
# show_all=True 显示所有课程
Jwxt.getNowWeek()
```

<span id="item8"></span>
#### `8.获取当前学期ID -> str`
```python
Jwxt.getSheetID()
```

<span id="item9"></span>
#### `9.获取当前学期课程表 -> list`
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
#### `10.查询班级课表 -> list`
```python
Jwxt.getClassCourse(
    college_name='学院名称',
    grade='2023',
    major_name='专业名称',
    classes='1班'
)
```

<span id="item11"></span>
#### `11.查询教师课表 -> tuple`
```python
Jwxt.getTeacherCourse(teacherName='教师姓名')
```


<span id="item12"></span>
#### `12.获取课程表ID -> str`
```python
Jwxt.get_kbjcmsid()
```

<span id="item13"></span>
#### `13.下载学生课程表 -> bool`
```python
Jwxt.downloadSheet(save_dir='')
```
