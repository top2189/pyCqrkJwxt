import re
import os
import xlrd
import datetime

class schedule:
    def __init__(self,start=None,week=None):
        """
        使用说明：
        start: 传入开学日期 例如 [2024,2,25] ,切记此时间一定要是“周日”
        week: 当前是第几周，从教务系统中获取后传入
        """
        self.ROOT = os.getcwd()

        if start is not None:
            self.y    = start[0]
            self.m    = start[1]
            self.d    = start[2]
        else:
            self.week = week


        # 该列表按照重庆人文科技学院，课表排序
        # index 取值 [0,12] 一共代表13节课
        self.time = [
            (28800,31500),
            (32100,34800),
            (35400,38100),
            (38700,41400),
            (42000,44700),
            (52200,54900),
            (55500,58200),
            (58800,61500),
            (62100,64800),
            (68400,71100),
            (71700,74400),
            (75000,77700),
            (78300,81000)
        ]

        os.makedirs(self.ROOT+'/xls/', exist_ok=True)

    def load(self,file):
        """
        传入文件名称，初始化xlrd库
        """
        df = xlrd.open_workbook(self.ROOT+'/xls/'+file)
        return df
    
    def is_xls_file(self,file):
        try:
            xlrd.open_workbook(self.ROOT+'/xls/'+file)
            return True
        except:
            return False
    
    def getClassData(self,file):
        """
        获取课程数据
        """
        if not self.is_xls_file(file):
            return [[],[],[],[],[],[],[]]
        
        sheet1 = self.load(file)[0]

        Monday    = sheet1.col_values(1,3,9)
        Tuesday   = sheet1.col_values(2,3,10)
        Wednesday = sheet1.col_values(3,3,10)
        Thursday  = sheet1.col_values(4,3,10)
        Friday    = sheet1.col_values(5,3,10)

        return [Monday,Tuesday,Wednesday,Thursday,Friday]
    
    def parseClassData(self,file):
        tup = [[],[],[],[],[],[],[]]
        for datas in self.getClassData(file):
            for schedule_text in datas:
                course_name_pattern = re.compile(r'^(.*?)\n', re.MULTILINE)  
                
                # 匹配包含[周]的行的正则表达式  
                week_pattern = re.compile(r'.*\[周\]\n')  
                
                # 用于存储匹配结果的列表  
                courses = []  
                current_course_name = None  
                
                # 遍历课表的每一行  
                for line in schedule_text.split('\n'):  
                    # 查找课程名称  
                    course_name_match = course_name_pattern.match(line)  
                    if course_name_match:  
                        current_course_name = course_name_match.group(1).strip()  
                    
                    # 查找包含[周]的行  
                    if week_pattern.match(line):  
                        # 如果已经找到了课程名称，则存储结果  
                        if current_course_name:  
                            courses.append((current_course_name, line.strip()))  
                            # 重置课程名称为空，以便下一个匹配  
                            current_course_name = None  
                
                # 打印结果  
                for course_name, week_info in courses:  
                    print(f"课程名称: {course_name}")  
                    print(f"时间/周次: {week_info}")  
                    print()


        # i = 0
        # for datas in self.getClassData(file):
        #     for text in datas:
        #         pattern = re.compile(r'''
        #             (.*?)\n               # 名称
        #             (\d+(?:-\d+)?)\[周\]\n     # 周次  
        #             (\S+教\d+室)\n        # 教室  
        #             \[(\d+-(?:\d+-?\d*))\]节 # 上课节次（支持单节、双节和连续多节）  
        #             (?:(?!\1).)*?         # 非捕获组，确保下一个匹配从新的课程名称开始  
        #             (?=\n\n|$)            # 断言，确保匹配块之后是两个换行符或字符串结尾  
        #         ''', re.VERBOSE | re.DOTALL) 
            
        #         matches = pattern.finditer(text)  
        #         for ma in matches:  
        #             name, week, classroom, time = ma.groups()  
        #             lst_clean = [x for x in name.split('\n') if x]
        #             lst_clean2 = [x for x in lst_clean[1].split('(') if x]
                    
                    
        #             tup[i].append((lst_clean[0],lst_clean2[0],week.strip(), classroom.strip(), time.strip()))
        #     i+=1
        # return tup
    

    def getClassTime(self,file,timestamp=0):
        """
        获取课程上课时间

        timestamp 需要计算的时间戳值，不传默认获取当天的课程
        """
        tuples = [[],[],[],[],[],[],[]]

        # 当前第几周
        week = self.getWeek(timestamp)[0]
        l = 0

        # try:
        if True:
            for datas in self.getClassData(file):
                for data in datas:
                    # if len(data) < 10:
                    #     break

                    for i in range(1,len(data.split("[周]"))):
                        b = (data.split("]节")[i-1].split("["))[-1].replace("[0", "").split("-")
                        d = (data.split("[周]")[i-1].split("\n"))[-1]

                        print(data.split("[周]")[i-1])
                        

                        if len(d) == 1:
                            # 该课程只开设一周，特殊处理
                            if week < int(d) or week > int(d):
                                print(1231231)
                                continue
                        else:
                            # 课程是个范围区间，只有在此区间才可以返回
                            d_1 = int(d.split("-")[0])
                            d_2 = int(d.split("-")[1])

                            if week < d_1 or week > d_2:
                                # print(d.split("-"))
                                # break
                                pass
                        

                        for s in b:
                            # print(s)
                            tuples[l].append(self.time[int(s)-1])
                l += 1

            return tuples
        # except:
        #     return None

    
    def is_class(self,tuples=None,week=-1,start=0,end=0):
        """
        tuples: 每周的上课时间段，使用 self.getClassTime()获取
        week:   当天为周几
        start:  当天的第几秒，一天最大为 86400 秒
        end:    [不传参时，只计算start时刻] 当天的第几秒，一天最大为 86400 秒

        """
        if tuples is None:
            return False

        if week < -1 or week > 6:
            return False
        
        if start > end and end != 0:
            return False
        
        if week == -1:
            week = self.getWeek()[1]

        for lists in tuples[week]:
            ts = []
            for t in lists:
                ts.append(t)
            if end != 0:
                if start-ts[0]>=0 and end-ts[1]<=0:
                    # 活动完全在上课时间段内
                    return True
                if end-ts[0]>=0 and start-ts[1]<=0:
                    # 活动有点长，耽误了上课前的一段时间
                    return True
                if start-ts[0]<=0 and end-ts[1]>=0:
                    # 活动开始有点早，与课表有重叠
                    return True
                if start-ts[0]<=0 and end-ts[1]>=0:
                    # 活动时间非常长，完全覆盖了活动上课时间段
                    return True
            else:
                if start-ts[0]>=0 and start-ts[1]<=0:
                    # 当前时刻在上课范围内
                    return True
            ts = []
        
        return False
    
    def getSecond(self,timestamp = 0):
        """
        给定一个时间戳，返回是当天的第几秒
        """
        if timestamp == 0:
            time = datetime.datetime.now()
        else:
            time = datetime.datetime.fromtimestamp(int(timestamp))

        second_of_day = time.hour * 3600 + time.minute * 60 + time.second

        return second_of_day
    

    def getWeek(self,timestamp = 0):
        """
        传入timestamp时间戳

        返回以 (第几周,星期几) 的列表
            例如 [3,4] 是开学第三周的星期五
        """

        if timestamp == 0:
            time = datetime.datetime.now()
        else:
            time = datetime.datetime.fromtimestamp(int(timestamp))

        if self.week is None:
            self.week = time.isocalendar()[1] - datetime.date(self.y,self.m,self.d).isocalendar()[1]

        return [self.week,time.weekday()]