


<center>
    <h1>重庆人科教务系统助手（pyCqrkJwxt）</h1>
    <p>使用Python3实现自动化调用强智教务系统接口</p>
    <p>注意：本代码仅用于学习Python爬虫</p>
    <p>任何人或组织使用本项目的代码进行的任何违法行为与本人无关</p>
</center>

## 项目介绍
本项目使用Python3实现自动化调用`强智教务系统`相关接口，教师端和学生端均可使用本项目的代码。

学生端目前已支持自动登录、自动获取课程表、自动获取成绩、自动抢课等功能；教师端目前仅支持获取本人的基本信息。

本项目的webvpn功能，仅限于`重庆人文科技学院`使用，其他学校请自行修改代码，这里以学生端为例，仅需把登录成功的cookies传给`cqrk.jwxtStudent(cookies)`即可，教师端同理。

## 项目结构
```sh
cqrk/
  __init__.py  -----------  项目入口

  base/
    core.py --------------  日志记录
  config/
    config.py ------------  变量接口配置
    powerList.py ---------  网站权限列表
    schedule.py ----------  上课时间配置
  jwxt/
    student.py -----------  教务系统学生端
    teacher.py -----------  教务系统教师端
    user.py --------------  教务系统用户类
  tools/
    sensorsdata.py -------  伪造cookies
    tool.py --------------  常用工具类
  web/
    web.py ---------------  web服务功能
  webvpn/
    webvpn.py ------------  webvpn校外登录
```

## 安装
直接通过`pip`指令，安装项目所需依赖的包文件。
```sh
pip install -r requirements.txt
```


## 使用

本项目以重庆人文科技学院的 `强智教务系统` 为例，其他学校在使用过程中如出现问题，请自行修改代码，具体的使用方法请参考以下接口文档：

### [1.学生端接口文档](./docx/student.md)
### [2.教师端接口文档](./docx/student.md)


## 免责声明
$\color{red}{本代码仅用于学习Python爬虫}$
$\color{red}{任何人或组织使用本项目的代码进行的任何违法行为与本人无关}$