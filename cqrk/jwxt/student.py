import pickle
from typing import Union
from datetime import datetime
from bs4 import BeautifulSoup
from ..base.core import core
import requests
from ..tools.tool import *
import re
import os

class jwxtStudent(core):
    def __init__(self,cookies=None,use_web_vpn=False):
        super().__init__()

        self.domain = self.config.domain

        if use_web_vpn:
            # 开启webvpn后可以公网访问
            self.domain = self.config.webVpnJwxt
            
        self.cookies = cookies

    def get(self,
            url: str='',
            api:str='',
            headers: dict = None
            ) -> requests.Response:
        """发送get请求"""

        if headers is None:
            headers = self.config.headers
        if url == '':
            url = self.domain + api
        response = requests.get(url=url, headers=headers, cookies=self.cookies)
        return response
    
    def post(self,
             url: str='',
             api:str='',
             data:dict={},
             headers: dict = None
             ) -> requests.Response:
        """发送post请求"""
        if headers is None:
            headers = self.config.headers
        if url == '':
            url = self.domain + api
        response = requests.post(url=url,data=data, headers=headers, cookies=self.cookies)
        return response
    
    def get_collegeID(self,collegeName:str) -> str:
        """获取学院ID"""
        if collegeName == '':
            return ''

        path = self.ROOT+'/libs/data/college.json'
        collegeData = None
        if not os.path.exists(path):
            collegeData = self.getClassParams(grade=False,major=False,use_cache=False)['college']
        else:
            collegeData = load_json(path)

        searchData = find_dict_key(collegeData,collegeName)

        if len(searchData) == 0:
            return ''
        
        for key, value in searchData[0].items():
            return value
    
    def get_majorID(self,college_id='',college_name='',major_name=''):
        """获取专业ID"""

        if college_id == '' and college_name == '':
            self.logger.error('未提供学院ID或学院名称')
            return ''
        
        if college_id == '':
            college_id = self.get_collegeID(college_name)
        
        path = self.ROOT+'/libs/data/major.json'

        if not os.path.exists(path):
            self.getClassParams(grade=False,use_cache=False)
            self.get_majorID(college_id=college_id,major_name=major_name)
        
        majorData = load_json(path)

        major_id = ''

        # for d in find_dict_key(majorData,college_id):
        #     if major_name in d['dmmc']:
        #         return d['dm']
        for m in majorData:
            if college_id in m:
                s = m[college_id]

                for f in s:
                    if major_name in f['dmmc']:
                        return f['dm']
                break
                    
        return major_id
    
    def get_user_name(self) -> str:
        """获取已经登录的用户名称"""
        html = self.get(api=self.config.jsMainPage).text
        soup = BeautifulSoup(html, 'html.parser')
        user_name = soup.find('span', attrs={'class': 'glyphicon-class ckgrxx'}).text
        
        return user_name
        
    
    def joinCourse(self,course_name,teacher_name='',xk_name='',preview_course=False) -> bool:
        """ 加入指定名称的课程

        Args:
            course_name: 需要选的课程名称，具体某一门课程，例如：篮球，乒乓球
            xk_name: 开放的学期选课名称，例如体育XXX，不是具体课程，不传默认使用获取到的第一个选课信息

        Returns:
            返回选课结果
        """
        student_info = self.get_my_info()
        # self.logger.info(f"你好，{student_info['name']}，抢课程序已启动")
        self.logger.info(f"你好，{student_info['name']}，抢课程序已启动")
        jx0502zbid = ''
        coures_xk_name = ''
        select_course_lists = self.get_select_course_lists()

        if xk_name == '':
            jx0502zbid = select_course_lists[0][-1]
            coures_xk_name = select_course_lists[0][1]
        else:
            for c in select_course_lists:
                if xk_name in c[1]:
                    jx0502zbid = c[-1]
                    coures_xk_name = c[1]

                    break

        if jx0502zbid == '':
            raise Exception('未找到选课名称为“{}”的学期选课'.format(xk_name))
        
        self.logger.info(f"已选择【{coures_xk_name}】")
        course_lists = self.get_course_lists(jx0502zbid=jx0502zbid,preview_course=preview_course)

        self.logger.info(f"课程列表加载完成，共 {len(course_lists)} 门课程")

        xk_list = []

        for c in course_lists:
            if course_name in c[0] and teacher_name in c[1]:
                xk_list = c
                break
        
        c_name        = xk_list[0]
        c_teacher     = xk_list[1]
        jx0404id      = xk_list[2]
        optional_nums = xk_list[3]
        xk_type       = xk_list[-1]

        if c_teacher == '':
            c_teacher = '无'

        self.logger.warning(f"目标课程【{c_name}】，教师 “{c_teacher}”，可选人数 {optional_nums} 人")

        if optional_nums == 0:
            self.logger.error('可选人数为0，无法选课')
            raise Exception('可选人数为0，无法选课')

        __oper_lists = [
            'xxxkOper',
            'bxxkOper',
            'ggxxkxkOper'
        ]

        oper_name = ''

        for oper in __oper_lists:
            if str(xk_type).lower() in oper:
                oper_name = oper
                break

        if jx0404id == '':
            # return {'success': False, 'message': '目标课程不存在，请重新选择！'}
            return False
        
        api = f'/jsxsd/xsxkkc/{oper_name}?jx0404id={jx0404id}'

        data = self.get(api=api).json()

        self.logger.info(f"请求选课接口：{api}")

        if data['success']:
            # return {'success': True, 'message': '选课成功！'}
            self.logger.info('选课成功！')
            return True
        else:
            # return {'success': False, 'message': data['message']}
            self.logger.error(data['message'])
            return False

    def get_select_course_lists(self) -> list:
        "获取选课列表"

        xklc_list_text = self.get(api='/jsxsd/xsxk/xklc_list').text

        soup = BeautifulSoup(xklc_list_text, 'html.parser')
        tr_tags = soup.find_all('tr')

        result = []
        # 遍历每个<tr>标签，并找到其下的所有<td>标签
        for tr in tr_tags:
            td_tags = tr.find_all('td')
            i = 0
            _c = []
            for td in td_tags:
                td_text = td.text.strip()
                if i in range(3):
                    _c.append(td_text)
                elif '进入选课' in td_text:
                    a = td.find('a')
                    _c.append(a['href'].split('=')[1])
                i += 1

            if len(_c) > 0:
                result.append(_c)

        return result


    def get_course_lists(
            self,
            jx0502zbid,
            only_online_course=False,
            only_optional=True,
            preview_course=False
        ) -> list:
        """获取课程列表

        Args:
            jx0502zbid: 通过get_select_course_lists()方法，获取到的参数list[i][-1]
            only_online_course: 只返回线上课程，默认为False
            only_optional: 只返回可以选择的课程，即剩余人数大于0的课程，默认为True
            preview_course: 预览选课，未开抢时，可以预览课程列表，默认为False

        Raises:
            ValueError: 课程数据获取失败

        Returns:
            list: 课程列表
        """

        _paths = [
            "xsxkBxxk",
            "xsxkXxxk",
            "xsxkGgxxkxk"
        ]

        # if course_type not in range(3):
        #     raise ValueError("course_type must be in range(3)")
        
        # api = '/jsxsd/xsxkkc/'+_paths[course_type]
        
        if preview_course:
            api_index = 'yxxsxk_index'
        else:
            api_index = 'xsxk_index'
            
        api = f'/jsxsd/xsxk/{api_index}?jx0502zbid={jx0502zbid}'
        
        xsxk_index_html = self.get(api=api).text

        try:
            course_type = xsxk_index_html.split('comeIn')[1].split('"')[0]
        except:
            self.logger.debug('课程列表为空，已修改“preview_course”参数为True')
            return self.get_course_lists(jx0502zbid,only_online_course,only_optional,True)
        
        
        api   = ''
        _type = ''
        for path in _paths:
            if course_type in path:
                api = f'/jsxsd/xsxkkc/{path}'
                _type = path[4:]
                break
        
        if api == '':
            raise ValueError('课程列表获取失败_2')
        
        data = {
            'sEcho': 1,
            'iColumns': 11,
            'iDisplayStart': 0,
            'iDisplayLength': 999,
        }

        # http://jwxt.cqrk.edu.cn:18080/jsxsd/xsxkkc/yl_xsxkGgxxkxk?kcxx=&skls=&skxq=&skjc=&sfym=false&sfct=false&szjylb=&sfxx=true

        response = self.post(api=api,data=data)

        course_lists = response.json()
        data_lists = []

        for course in course_lists['aaData']:
            # 授课老师姓名
            teacher_name = ''
            try:
                teacher_name = course['kkapList'][0]['jgxm']
            except:
                pass

            # 这里需要注意一下，公选课的课程名字需要获取 course['kcmc']
            if course_type == 'Ggxxkxk':
                course_name = course['kcmc']
                optional_nums = int(course['syrs'])
            else:
                course_name = course['ktmc']
                # 这里没有测试，先些成1
                optional_nums = 1
            
            if only_optional == 0:
                continue

            if only_online_course and teacher_name != '':
                continue

            data_lists.append([course_name,teacher_name,course['jx0404id'],optional_nums,_type])
        
        return data_lists

    def get_my_info(self) -> Union[dict, None]:
        """获取学生基本信息

        Returns:
            (dict | None): 成功返回dict，失败返回None
        """
        response = self.get(api=self.config.mainPage)
        
        if response.status_code != 200:
            return None
        
        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        middletopttxlr = soup.find('div', {'class': 'middletopttxlr'})
        data = []
        for ttxlr in middletopttxlr.contents:
            if ttxlr.name != 'div' : continue
            wxxcont = ttxlr.find(class_='middletopdwxxcont')
            if wxxcont and len(wxxcont.text.replace('\xa0','')) != 0:
                data.append(wxxcont.text)
        
        result = {
            'name':   data[0],
            'uid':    data[1],
            'college':data[2],
            'major':  data[3],
            'class':  data[4]
        }

        return result
        
        
    def getCourseScore(self,sheetID=None,show_all=False) -> Union[dict, None]:
        if sheetID is None and show_all is False:
            sheetID = self.getSheetID()

        data = {
            'kksj':sheetID,
            'kcxz':'',
            'kcmc':'',
            'xsfs':'all',
            'kcsx':''
        }
        response = self.post(api=self.config.cjcxList,data=data)
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        div_tag = soup.find('div')

        # 获取div中的所有文字内容
        try:
            cjInfo = div_tag.get_text().split('查询条件')[1].split('\n')[0].replace('\r','').split(' ')
        except:
            return None

        # 查找id="dataList"的table标签
        table = soup.find('table', {'id': 'dataList'})

        # 查找table标签下的所有tr标签
        rows = table.find_all('tr')

        # 创建一个空字典，用于存储解析后的数据
        data = []

        # 遍历所有tr标签
        for row in rows:
            # 提取td标签中的内容，并将其转换为列表
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]

            if len(cols) == 0:
                continue

            if cols[0] == '未查询到数据':
                return {}

            data.append({
                'id':cols[0],
                'name':cols[3],
                'score':cols[5],
                'credit':cols[7],
                'hour':cols[8],
                'classGPA':cols[9],
                'type':cols[-4]
            })


        result = {
            'nums':len(data),
            'totalCredit':cjInfo[-3].split(':')[1],
            'GPA':cjInfo[-2].split(':')[1],
            'avrScore':cjInfo[-1].split(':')[1],
            'data':data,
        }
            
        # 返回解析后的字典
        return result


    def getSheetID(self) -> str:
        """获取当前学期ID
        
        例如: 2023-2024-2

        Returns:
            str: xnxq01id 参数
        """
        response = self.get(api=self.config.classTable)

        if response.status_code != 200:
            self.logger.error(f'响应码错误，错误码{response.status_code}')
            return ''
        
        soup = BeautifulSoup(response.text, 'html.parser')

        return str(soup.find(selected="selected")['value'])

    def getNowWeek(self) -> int:
        """获取当前是第几周

        Returns:
            int: 当前的周数
        """

        mainPageSoup = self.__getMainPageSoup()

        return int(mainPageSoup.find(class_='main_text main_color').text[1:-1])
    
    def getCourseSheet(self,sheetID=None,parse=False,onlyName=False) -> Union[list,None]:
        """获取学生课程表

        Args:
            sheetID (str, optional): 当前学期ID. Defaults to None.
            parse (bool, optional): 是否解析输出. Defaults to False.
            onlyName (bool, optional): 仅输出课程名称. Defaults to False.

        Returns:
            (list | None): 成功返回list，失败返回None
        """
        if self.cookies is None:
            self.logger.warning('缺少必要参数：cookies')
            return None
        
        if sheetID is None:
            sheetID = self.getSheetID()
        
        rowTup = [[],[],[],[],[],[],[]]

        classTable =  f'{self.domain}{self.config.classTable}'

        data = {
            'xnxq01id':sheetID
        }

        try:
            response = self.post(api=self.config.classTable, data=data)
        except:
            self.logger.error('网络连接超时！')
            return None
        
        
        soup = BeautifulSoup(response.text, 'html.parser')
        valigns = soup.find_all(valign="top")

        i = 0
        for valign in valigns:
            kbcontent  = valign.find(class_="kbcontent")
            kbcontent1 = valign.find(class_="kbcontent1")

            kbstr = kbcontent1.get_text()
            if len(kbstr.strip()) != 0:
                kb_name = kbstr.split('----------------------')

            d = []
            kb_teacher = valign.find_all(title="老师")
            kb_week    = kbcontent.find_all(title="周次(节次)")
            kb_room    = kbcontent.find_all(title="教室")
    

            if len(kb_teacher) == 0:
                if parse:
                    r = ''
                else:
                    r = []
                rowTup[i%7].append(r)
                i += 1
                continue

            for n in range(len(kb_teacher)):
                c_teacher = kb_teacher[n].text.strip()
                c_week    = kb_week[n].text.strip().split('(周)')
                
                # 修复解析体育课的教室时，报错的Bug
                if len(kb_room) == len(kb_teacher):
                    c_room = kb_room[n].text.strip()
                else:
                    c_room = '无教室'

                c_name    = kb_name[n].split(c_week[0])[0].replace('&nbsp',' ')
                c_time    = c_week[1].replace('节','')[1:-1]

                if onlyName:
                    r2 = (c_name)
                else:
                    r2 = (
                        c_name,
                        c_teacher,
                        c_week[0],
                        c_time,
                        c_room
                    )

                if parse:
                    r2 = ''.join(r2)
                    d.append(r2)
                else:
                    d.append(r2)


            if parse:
                rowTup[i%7].append('\n'.join(d))
            else:
                rowTup[i%7].append(d)

            i += 1
        
        return rowTup
    
    def getClassParams(self,college=True,grade=True,major=True,use_cache=True):
        response = self.get(api=self.config.classData)
        
        soup = BeautifulSoup(response.text, 'html.parser')

        data = {}

        if college:
            data['college'] = []

            college_cache_path = self.ROOT+'/libs/data/college.json'
            if use_cache and os.path.exists(college_cache_path):
                college_data = load_json(college_cache_path)

                data['college'] = college_data
            else:
                select_element = soup.find('select', {'id': 'skyx'})
                options = select_element.find_all('option')
                for option in options:
                    if option['value']:
                        data['college'].append({
                            option.text.split(']',1)[1]: option['value'],
                        })
                
                save_json(college_cache_path,data['college'])
                
        if grade:
            data['grade'] = []
            select_element = soup.find('select', {'id': 'sknj'})
            options = select_element.find_all('option')

            i = 0
            for option in options:
                value = option['value']
                if value and i < 4:
                    data['grade'].append({
                        option.text+'级': value,
                    })

                    i += 1
        
        if major:
            data['major'] = []
            major_cache_path = self.ROOT+'/libs/data/major.json'

            # 读取缓存
            if use_cache and os.path.exists(major_cache_path):
                major_data = load_json(major_cache_path)

                data['major'].append(major_data)
                data['major'] = data['major'][0]
            elif college:
                for c in data['college']:
                    sid = list(c.values())[0]
                    response = self.get(api=self.config.getZyByAjax)
                    if response.status_code == 200:
                        data['major'].append({
                            sid : response.json(),
                        })
                
                # 自动缓存
                save_json(major_cache_path,data['major'])


                
            else:
                self.logger.warning('college参数和use_cache不能同时为False')
        

        return data
    
    def getClassCourse(self,
                       college_id:str='',
                       college_name:str='',
                       grade='',
                       major_id='',
                       major_name='',
                       classes=''
                       ) -> list:

        if college_id == '' and college_name == '':
            self.logger.warning('college_id和college_name不能同时为空')
            return []
        
        if major_id == '' and major_name == '':
            self.logger.warning('major_id和major_name不能同时为空')
            return []
        

        if college_id == '':
            college_id = self.get_collegeID(college_name)

        if major_id == '':
            major_id = self.get_majorID(college_id=college_id,major_name=major_name)

        pattern = r'^\d{1,2}班$'
        if not re.match(pattern,classes):
            self.logger.warning('classes参数格式错误')
            return []
            

        if grade == '':
            grade = str(datetime.now().year)

        xnxqh = self.getSheetID()

        data = {
            'xnxqh': xnxqh,
            'kbjcmsid': self.get_kbjcmsid(),
            'skyx': college_id,
            'sknj': grade,
            'skzy': major_id,
            'skbjid': '',
            'skbj': classes,
            'zc1': '',
            'zc2': '',
            'skxq1': '',
            'skxq2': '',
            'jc1': '',
            'jc2': ''
        }

        headers = self.config.headers
        response = self.post(api=self.config.kbxx_xzb_ifr,data=data,headers=headers)

        soup        = BeautifulSoup(response.text, 'html.parser')
        td_elements = soup.find_all('td')
        td_tags     = soup.find_all('td', align="center", valign=lambda x: x != "top")
        pattern     = r'(\d{4}级.*?班)'

        class_name  = td_tags[-1].text.strip()

        td_texts    = [re.sub(r'(\d{4}级.*?班)', '\n',td.get_text(strip=True)) for td in td_elements][44:]
        data        = [td_texts[i:i+6] for i in range(0, len(td_texts), 6)]

        # for i in range(len(data)):
        #     for j in range(len(data[i])):
        #         match = re.search(pattern, data[i][j])
        #         if match:
        #             data[i][j] = data[i][j].replace(match.group(1), '\n&#'+match.group(1)+'#&')

        # courseSheet = [*zip(*data)]

        return (xnxqh,class_name,data)

    def getTeacherCourse(self,teacherName='',save_cache=True,save_path=None):
        """ 获取教师课表

        Returns:
            (dict | None): 成功返回list，失败返回None
        """
        if teacherName == '':
            return None
        
        xnxqh = self.getSheetID()
        
        data = {
            'xnxqh': xnxqh,
            'skjs': teacherName
        }

        response    = self.post(api=self.config.teacherTable,data=data)
        soup        = BeautifulSoup(response.text, 'html.parser')
        td_elements = soup.find_all('td')
        pattern     = r'(\d{4}级.*?班)'

    
        td_texts    = [td.get_text(strip=True).replace(teacherName,'') for td in td_elements][44:]
        data        = [td_texts[i:i+6] for i in range(0, len(td_texts), 6)]



        for i in range(len(data)):
            for j in range(len(data[i])):
                match = re.search(pattern, data[i][j])
                if match:
                    data[i][j] = data[i][j].replace(match.group(1), '\n#'+match.group(1)+'#')

        courseSheet = [*zip(*data)]

        return (xnxqh,courseSheet)

    def get_kbjcmsid(self) -> str:
        """ 获取课程表ID
        """
        # 解析HTML内容
        mainPageSoup = self.__getMainPageSoup()
        
        # 获取所有的 option 标签
        options = mainPageSoup.find_all('option')
        # 遍历 option 标签并获取 value 属性
        kbjcmsid = [option['value'] for option in options][0]

        return kbjcmsid
    
    def downloadSheet(self,sheetID=None,week='',download_all=False,save_dir='') -> bool:
        """下载学生课程表

        Args:
            sheetID (str, optional): 当前学期ID. Defaults to None.
            week (str, optional): 下载第几周的数据. Defaults to ''.
            download_all (bool, optional): 下载当前学期的所有课程. Defaults to False.

        Returns:
            bool: 是否保存成功
        """
        if self.cookies is None:
            self.logger.warning('缺少必要参数：cookies')
            return False
        
        if sheetID is None:
            sheetID = self.getSheetID()

        if not download_all and len(week) == 0:
            try:
                week = self.getNowWeek()
            except:
                week = ''

        kbjcmsid = self.get_kbjcmsid()
        download =  f'{self.domain}{self.config.xskbPrint}?xnxq01id={sheetID}&zc={week}&kbjcmsid={kbjcmsid}'

        try:
            # file = requests.get(download, headers=self.config.headers, cookies=self.cookies).content
            file = self.get(url=download).content
        except:
            self.logger.error('网络连接超时！')
            return False
        kb_name = f'{self.get_my_info()["name"]}-{sheetID}.xls'

        if save_dir == '' or not os.path.exists(save_dir):
            kb_path = f"{self.ROOT}/xls/{kb_name}"
        else:
            kb_path = f"{save_dir}/{kb_name}"

        if os.path.exists(kb_path):
            os.remove(kb_path)
        
        try:
            with open(kb_path,'wb') as f:
                f.write(file)
            print(f'课表保存成功！保存路径：{kb_path}')
            return True
        except:
            return False


    def __getMainPageSoup(self) -> BeautifulSoup:
        """获取主页面的soup对象

        Returns:
            BeautifulSoup: soup对象
        """
        response = self.get(api=self.config.mainPage)
        if response.status_code != 200:
            self.logger.error(f'响应码错误，错误码{response.status_code}')
            False
        
        soup = BeautifulSoup(response.text, 'html.parser')


        return soup
    