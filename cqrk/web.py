from .tool import *
from .core import core
from .powerList import Power

from enum import Enum

from flask import Flask, render_template, request,abort, redirect, send_file, url_for, session, flash
from flask_session import Session

from flask.json import jsonify
from threading import Thread
from .config import *
from datetime import datetime
import logging
import uuid
import math
import os
import time
import json
import sys

class Error(Enum):
    ERROR_STATE = 'error_state'
    ERROR_POWER = 'error_403'
    ERROR_LOGIN = 'login'

class web(core):
    def __init__(self,DEBUG=None):
        super().__init__(DEBUG)

        # TODO: 本地测试使用
        # url = 'http://185.242.234.55:6443'

        self.authKey = md5(get_serial_number())

        self.app = Flask('frp_console_web')
        self.app.logger.setLevel(logging.ERROR)

        self.app.config['SECRET_KEY'] = uuid.uuid4().hex[:16]
        self.app.template_folder      = self.ROOT+'/libs/templates'
        self.app.static_folder        = self.ROOT+'/libs/static'

        self.__session()

        self.__routes()
    

    def jwxt(self):
        from .user import user
        from .webvpn import webvpn
        from .jwxt import jwxt

        stdID = '学号'

        webVpn = webvpn()
        webVpn.username = stdID
        webVpn.password = ''
        webVpn.auth()

        User = user(use_web_vpn=True)
        User.username = stdID
        User.password = ''
        User.auth()

        cookies = User.loadCookie()

        return jwxt(cookies,use_web_vpn=True)

    
    def runServer(
            self,
            port=7200,
            debug=False
        ) -> None:

        self.logger.info('Web server start at http://{}:{}'.format(get_local_ip(),port))
        self.logger.info('Auth key: {}'.format(self.authKey))
        self.logger.debug('AES key: {}'.format(md5(get_serial_number()+self.config.keyStr,True)))
        self.logger.debug('AES iv: {}'.format(get_iv()))

        if debug:
            self.app.run(debug=True,host='0.0.0.0',port=port)
        else:

            from gevent import pywsgi
            server = pywsgi.WSGIServer(('0.0.0.0', port), self.app)
            server.serve_forever()
    
    def __session(self):
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SESSION_FILE_DIR'] = self.ROOT+'/cache/session'  # 设置 session 文件存储目录
        self.app.config['SESSION_FILE_THRESHOLD'] = 1000  # 设置 session 文件数量上限
        self.app.config['SESSION_PERMANENT'] = True  # 设置 session 是否为永久有效
        self.app.config['SESSION_USE_SIGNER'] = True  # 设置是否对 session 进行签名

        Session(self.app)
    
    def __routes(self):
        self.routes_public()
        self.routes_api()
        self.routes_web()

        self.app.route('/plugins/auth', methods=['POST'])(self.user_auth)
        # self.app.route('/plugins/', methods=['POST'])(self.user_auth)
        self.app.route('/action/logout')(self.action_logout)
        
    def routes_public(self):
        self.app.errorhandler(403)(self.public_error_403)
        self.app.errorhandler(404)(self.public_error_404)
        self.app.add_url_rule('/error_state', 'error_state', self.page_error_state)
        self.app.add_url_rule('/error_403', 'error_403', self.public_error_403)


    def routes_api(self):
        """
        API接口
        """
        self.app.route('/api/user/login', methods=['POST'])(self.user_login)
        self.app.route('/api/user/register', methods=['POST'])(self.user_register)
        self.app.route('/api/console/fresh', methods=['POST'])(self.console_fresh)
        self.app.route('/api/console/settings/save', methods=['POST'])(self.console_settings_save)

        self.app.route('/student/init/loadSelect')(self.api_init_loadSelect)

        self.app.route('/api/data/major.json', methods=['GET','POST'])(self.api_data_major)


        self.app.route('/api/student/classTable.json', methods=['POST'])(self.student_class_table)

        self.app.route('/api/teacher/classTable.json', methods=['POST'])(self.teacher_class_table)



    def routes_web(self):
        """
        WEB页面
        """
        self.app.add_url_rule('/student/class/query', 'student_class_query', self.page_student_class_query)

        self.app.add_url_rule('/teacher/class/query', 'teacher_class_query', self.page_teacher_class_query)

        



        self.app.add_url_rule('/', 'index', self.page_index)
        self.app.add_url_rule('/index', 'index', self.page_index)
        self.app.add_url_rule('/index.html', 'index', self.page_index)

        self.app.add_url_rule('/proxies', 'proxies', self.page_proxies)
        self.app.add_url_rule('/proxies.html', 'proxies', self.page_proxies)
        
        self.app.add_url_rule('/users', 'users', self.page_users)
        self.app.add_url_rule('/users.html', 'users', self.page_users)

        self.app.add_url_rule('/settings', 'settings', self.page_settings)
        self.app.add_url_rule('/settings.html', 'settings', self.page_settings)
        
        self.app.add_url_rule('/login', 'login', self.page_login)
        self.app.add_url_rule('/login.html', 'login', self.page_login)

    def public_error_403(self, e=None):
        return render_template('error/403.html')
    
    def public_error_404(self, e=None):
        return render_template('error/404.html')


    def page_student_class_query(self):
        """
        教师查询课程页面
        """

        return render_template('student/query_class.html',webConfig=self.getWebConfig())


    def page_teacher_class_query(self):
        """
        教师查询课程页面
        """

        return render_template('teacher/query_class.html',webConfig=self.getWebConfig())
        

    def page_index(self):
        """
        服务器基本信息页面
        """
        auth = self.login_auth()
        if auth != 'SUCCESS':
            return redirect(url_for(getattr(Error, auth).value))
        
        if session['power'] == Power.ADMIN.value:
            return render_template('admin/index.html',auth=self.__aesEncode(),webConfig=self.getWebConfig())
        
        # if not self.checkPower(Power.USER.value):
        #     return redirect(url_for('error_auth'))
        
        return render_template('user/index.html',webConfig=self.getWebConfig())


    def page_proxies(self):
        """
        代理连接管理页面
        """
        auth = self.login_auth(Power.ADMIN.value)
        if auth != 'SUCCESS':
            return redirect(url_for(getattr(Error, auth).value))
        
        
        return render_template('admin/proxies.html',auth=self.__aesEncode(),webConfig=self.getWebConfig())

    def page_users(self):
        """
        用户管理页面
        """
        auth = self.login_auth(Power.ADMIN.value)
        if auth != 'SUCCESS':
            return redirect(url_for(getattr(Error, auth).value))
        
        return render_template('admin/users.html',auth=self.__aesEncode(),webConfig=self.getWebConfig())


    def page_settings(self):
        """
        系统设置页面
        """
        auth = self.login_auth(Power.ADMIN.value)
        if auth != 'SUCCESS':
            return redirect(url_for(getattr(Error, auth).value))
        
        return render_template('admin/settings.html',auth=self.__aesEncode(),webConfig=self.getWebConfig(),frpConfig=self.getFrpConfig())


    def page_login(self):
        """
        登录页面
        """
        return render_template('public/login.html',webConfig=self.getWebConfig())


    def user_auth(self):
        try:
            data = request.get_data(as_text=True)
            content = json.loads(data)['content']
            
            timestamp = int(content['timestamp'])

            if abs(int(time.time()) - timestamp) > 60:
                # 错误，请求超时，默认60s
                return jsonify({"reject": True,"reject_reason": "timestamp error"})

            username  = content['user']
            token     = content['metas']['token']

            userData  = load_json(self.ROOT+'/user/'+username+'.json')

            if len(userData) == 0:
                # 错误，用户不存在
                return jsonify({"reject": True,"reject_reason": "用户不存在"})
            
            # 开始验证
            if token != userData['token']:
                # 错误，token不匹配
                return jsonify({"reject": True,"reject_reason": "token认证失败"})
            
            if userData['state'] != 1:
                # 错误，用户已被封禁
                return jsonify({"reject": True,"reject_reason": "用户已被封禁"})

            # 更新最后登录时间
            userData['last_login'] = int(time.time())
            userData['address']    = content['client_address']

            state = save_json(self.ROOT+'/user/'+username+'.json',userData)

            if state:
                return jsonify({"reject":False,"reject_reason":"","unchange":True,"content":None})
            else:
                return jsonify({"reject": True,"reject_reason": "用户数据更新失败，请联系管理员"})
            
        except:
            self.logger.error('请求非法')
            return jsonify({'msg': 'EOF'})
    
    def page_error_state(self):
        return render_template('error/error_state.html')
    

    def user_login(self):
        username = request.form['username']
        password = request.form['password']

        # 校验数据是否合法
        if len(username) < 4 or len(password) < 6:
            return jsonify({"code": 2120,'msg':'Username or password is too short.'})
        
        if filter_str(username) != username or filter_str(password) != password:
            return jsonify({"code": 2125,'msg':'Username or password contains illegal characters.'})
        path = self.ROOT+'/user/'+username+'.json'
        if not os.path.exists(path):
            # 实际上用户不存在，为了安全，这里返回账号或密码错误，防止用户猜到用户名
            return jsonify({"code": 305,'msg':'账号或密码错误'})
        
        userData = load_json(path)

        if userData['password'] == sha256(password+self.authKey):
            if username != 'admin' and userData['state'] == 0:
                return jsonify({"code": 304,'msg':'用户已被封禁'})
            
            session['username'] = username
            session['power']    = userData['power']
            return jsonify({"code": 200,'msg':'success'})
        else:
            return jsonify({"code": 305,'msg':'账号或密码错误'})
    
    def user_register(self):
        # if not self.console_auth():
        #     return jsonify({"code": 302,'msg':'Authentication failed.'})
        
        username = request.form['username']
        password = request.form['password']

        # 校验数据是否合法
        if len(username) < 4 or len(password) < 6:
            return jsonify({"code": 2120,'msg':'Username or password is too short.'})
        
        if filter_str(username) != username or filter_str(password) != password:
            return jsonify({"code": 2125,'msg':'Username or password contains illegal characters.'})

        # 检查用户名是否已经存在
        if os.path.exists(self.ROOT+'/user/'+username+'.json'):
            return jsonify({"code": 2431,'msg':'Username already exists.'})
        
        uid   = str(uuid.uuid4())
        token = sha256(uid+str(int(time.time()*1000)))
        # 注册用户
        userData = {
            'uid': uid,
            "qq": request.form['qq'],
            "email": request.form['email'],
            'username': username,
            'password': sha256(password+self.authKey),
            'address': '0.0.0.0',
            'token': token,
            'create_time': int(time.time()),
            'last_login': 0,
            'power': 1,
            'state': 1
        }

        state = save_json(path=self.ROOT+'/user/'+username+'.json', data=userData)

        if state:
            # 注册成功
            return jsonify({"code": 200,'msg':'success','data':{'uid': uid, 'token': token}})
        else:
            # 注册失败
            return jsonify({"code": 2125,'msg':'Register failed.'})
    

    def data_getUserLists(self):
        if not self.console_auth():
            return jsonify({"code": 302,'msg':'Authentication failed.'})
        
        userLists = get_files(directory=self.ROOT+'/user/',exclude_prefixes=['admin'])

        if len(userLists) == 0:
            return jsonify({"code": 200,'msg':'目前没有注册用户','sums':0,'data':None})
        
        userData = []

        try:
            for user in userLists:
                userData.append(load_json(self.ROOT+'/user/'+user))
        except:
            return jsonify({"code": 3012,'msg':'查询用户列表出错','sums':0,'data':None})

        return jsonify({"code": 200,'msg':'success','sums':len(userLists),'data':userData})
    
    def action_logout(self):
        session.pop('username', None)
        session.pop('power', None)

        return redirect(url_for('login'))


    def console_fresh(self):
        if not self.console_auth():
            return jsonify({"code": 302,'msg':'Authentication failed.'})
        

        return jsonify({"code": 200,'msg':'success','auth':self.__aesEncode()})




        # return jsonify({"code": 200,'msg':'success','data_tcp':data_tcp,'data_udp':data_udp,'data_http':data_http,'data_https':data_https,'data_tcpmux':data_tcpmux,'data_stcp':data_stcp,'data_sudp':data_sudp})
    def console_settings_save(self):
        if not self.console_auth():
            return jsonify({"code": 302,'msg':'Authentication failed.'})
        
        data = request.form

        webConfig = {
            "name":data['name'],
            "url":data['url'],
            "keywords":data['keywords'],
            "description":data['description'],
            "copyright":data['copyright']
        }

        frpConfig = {
            "domain":data['frpSrc'],
            "username":data['frpUser'],
            "password":data['frpPwd'],
        }

        save_json(self.ROOT+'/libs/data/web.json',webConfig)
        # bug
        save_json(self.ROOT+'/libs/data/api.json',frpConfig)

        return jsonify({"code": 200,'msg':'success'})
    
    def api_init_loadSelect(self):
        college_path = self.ROOT+'/libs/data/college.json'

        if not os.path.exists(college_path):
            return jsonify({"code": 404,'msg':'Not Found'})

        data_college = load_json(college_path)
        data = {}

        data['college'] = data_college

        return jsonify({"code": 200,'msg':'success','data':data})


    def api_data_major(self):
        try:
            college_id = request.form['collegeId']

            path = self.ROOT+'/libs/data/major.json'

            if not os.path.exists(path):
                return jsonify({"code": 404,'msg':'Not Found'})

            data = load_json(path)
            result = self.__load_major_data(data,college_id)

            return jsonify({"code": 200,'msg':'success','data':result})
        except Exception as e:
            return jsonify({"code": 500,'msg':str(e)})

    def __load_major_data(self,data,college_id):
        for item in data:
            for key, value in item.items():
                if college_id == key:
                    return value
        return []

    
    def student_class_table(self):
        try:
            data       = request.form
            college_id = data['collegeId']
            major_id   = data['majorId']
            grade      = data['grade']
            classes    = data['class']

            getClassCourse = self.jwxt().getClassCourse(college_id=college_id,grade=grade,classes=classes,major_id=major_id)

            result = getClassCourse[-1]
            classScheduleTime = [self.config.classScheduleTime]

            return jsonify({"code": 200,'msg':'success','sums':len(result),'title':getClassCourse[1],'data':[*zip(*(classScheduleTime+result))]})
        except Exception as e:
            self.logger.error(e)
            return jsonify({"code": 500,'msg':'error'})
        

    def teacher_class_table(self):
        try:
            data = request.form
            teacherCourse = self.jwxt().getTeacherCourse(data['teacherName'])

            if teacherCourse is None:
                return jsonify({"code": 3041,'msg':'参数不合法'})

            title  = f"{data['teacherName']}的课程表【{teacherCourse[0]}】"
            result = teacherCourse[1]

            classScheduleTime = [self.config.classScheduleTime]
 
            return jsonify({"code": 200,'msg':'success','sums':len(result),'title':title,'data':[*zip(*(classScheduleTime+result))]})
        except Exception as e:
            self.logger.error(e)
            return jsonify({"code": 500,'msg':'error'})


    def __aesEncode(self):
        t = str(int(time.time()))

        return encode_aes(t+self.authKey)
    


    def console_auth(self):
        # 签名验证
        try:
            t    = int(request.form['t'])
            sign = request.form['sign']
            s    = request.form['s']
        except:
            return False
        
        aesKey = decode_aes(s)

        try:
            if self.authKey in aesKey:
                t2 = int(aesKey.replace(self.authKey,''))
            else:
                return False
        except:
            return False
        
        t3 = int(time.time())

        try:
            if sign != md5(str(t)+s) or abs(t3 - t) > 60 or abs(t3 - t2) > 60:
                return False
        except:
            return False
        
        return True
    
    def login_auth(self,min_view_power=1):
        if 'username' in session:
            username = session['username']
            path = self.ROOT+'/user/'+username+'.json'
            if os.path.exists(path):
                userData = load_json(path)

                if userData['power'] < 10:
                    if userData['state'] != 1:
                        return 'ERROR_STATE'

                    if userData['power'] >= min_view_power:
                        return 'SUCCESS'
                    else:
                        return 'ERROR_POWER'
                else:
                    return 'SUCCESS'
                
        return 'ERROR_LOGIN'
    

    def getWebConfig(self):
        return load_json(self.ROOT+'/libs/data/web.json')
    
    def getFrpConfig(self):
        return load_json(self.ROOT+'/libs/data/api.json')
    
    def checkPower(self, power):
        """ 检查权限

        Args:
            power: 页面所需要的最低权限
        """

        if session['power'] < power:
            return False
        
        return True
