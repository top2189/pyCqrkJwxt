
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
Jwxt = cqrk.jwxtTeacher(cookies)
```

#### `外网登录（webvpn登录）`
```python
webVpn = cqrk.webvpn()
webVpn.username = '用户名'
webVpn.password = '密  码'
webVpn.auth()
cookies = webVpn.loadCookie()
Jwxt = cqrk.jwxtTeacher(cookies,use_web_vpn=True)
```

## 相关接口
#### [1.获取登录姓名](#item1)
#### [2.获取个人信息](#item2)



<span id="item1"></span>
#### `1.获取登录姓名 -> str`
```python
Jwxt.get_user_name()
```

<span id="item2"></span>
#### `2.获取个人信息 -> dict`
```python
Jwxt.get_my_info()
```