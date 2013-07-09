#!/usr/bin/env python
#coding=utf-8
import sqlite3
import random
import web
import datetime
from jinja2 import Environment, PackageLoader
#url设置
urls = (
#    '/',"INDEX",
    '/',"TEST",
    '/test/(.*)','TEST',
)
app = web.application(urls,globals())
web.config.debug = False
#数据库类
class OS:
    #将题目保存到数据库
    def savetodb(self):
        conn = sqlite3.connect("os.db")
        cur = conn.cursor()
        sql_create = '''create table if not exists os(
        id integer primary key autoincrement,
        problem text,
        answer text
        )'''
        cur.execute(sql_create)
        cur.execute('''create table if not exists rank(
            id integer primary key autoincrement,
            score integer
            )''')
        conn.commit()
        problem_set = open("os.txt").readlines()
        sql_insert = "insert into os(problem,answer) values('%s','%s')"
        for problem in problem_set:
            temp = problem.split("\t")
#            print '.',temp[0],temp[1][:-1],'.'
            cur.execute(sql_insert%(temp[0],temp[1][:-1]))
            conn.commit()
        cur.close()
        conn.close()

    #从题库中随机抽取n个题目
    def get_problem(self,n):
        conn = sqlite3.connect("os.db")
        cur = conn.cursor()
        problem = cur.execute("select distinct problem from os")
        problem_list = []
        for row in problem:
            problem_list.append(row[0])
        total = len(problem_list)
        ret = []
        while n>0:
            temp = random.randint(0,total-1)
            if problem_list[temp] not in ret:
                ret.append(problem_list[temp])
                n -= 1
        cur.close()
        conn.close()
#        for i in ret:
#            print '='*50
#            print i
#            self.get_answer(i)
        return ret

    #获取某个题目的答案和答案个数
    def get_answer(self,problem):
        conn = sqlite3.connect("os.db")
        cur = conn.cursor()
        answer = cur.execute("select upper(answer) from os where problem='%s'"%problem)
        ans_ret=[]
        for row in answer:
            ans_ret.append(row[0])
        cur.close()
        conn.close()
        return ans_ret,len(ans_ret)

    #保存成绩信息以便统计排名
    def save_score(self,sc):
        conn = sqlite3.connect("os.db")
        cur = conn.cursor()
        cur.execute("insert into rank(score) values(%s)"%sc)
        conn.commit()
        cur.close()
        conn.close()

    #获取排名信息
    def get_rank(self,sc):
        conn = sqlite3.connect("os.db")
        cur = conn.cursor()
        ret = cur.execute("select count(*) from rank where score > %s"%sc)
        for i in ret:
            r = i
        cur.close()
        conn.close()
#        print "r=",r[0]
        return r[0]+1

#测试页面
class TEST():
    start_time=0   #测试开始时间
    total_time=0   #总测试时间
    os = OS()
    problem = []   #题目列表
    total_blank = 0#空数
    accept = 0     #正确数
    session=0      #防止不刷新的标记
    level=1.0      #难度系数
    time = {       #难度系数对应的时间
        '1.0':6,
        '2.0':5,
        '3.0':4,
    }
    #GET方法，获取题目
    def GET(self,args = None):
        try:
            TEST.start_time=datetime.datetime.now() #开始计时
            input = web.input()                     #获取输入
            try:
                TEST.level=input['level']
            except:
                TEST.level="2.0"
            TEST.session=0
            TEST.problem = self.os.get_problem(6)   #随机抽取6个题目
            std_ans = []         #标准答案
            TEST.total_blank=0
            for i in TEST.problem:  #计算空数，以便控制时间
                std_ans,num= self.os.get_answer(i)
                TEST.total_blank += num
            env = Environment(loader=PackageLoader('osweb', './')) #模板
            template = env.get_template('os.html')
            a = map(chr,range(66,71))
            num = range(0,6)
    #        print "total",TEST.total_blank
            TEST.total_time=TEST.total_blank*TEST.time[TEST.level]
            return template.render(time=TEST.total_time,problem=TEST.problem,td=a,num=num)
        except:
            return '<h1>System Error<br/><br/><a href="/">back</a></h1>'

    #POST方法，获取用户提交的数据并进行处理
    def POST(self,name=None):
#        try:
        end_time=datetime.datetime.now()
#            print TEST.start_time,end_time
        try:
            use=end_time-TEST.start_time
        except:
            return '<h1>Please click button at the end of rank page<br/><br/><a href="/">back</a></h1>'
#            print use.seconds,TEST.total_time
        if use.seconds-10 > TEST.total_time: #防止禁用JS而使时间停止作弊
            return "<h1>Please NOT Forbid JS！</h1>"
        input = web.input()
        error_pro=[]
        error_user=[]
        right_ans=[]
        for row in range(0,6):#1-6
#                if TEST.session==1:     #防止后退以后不刷新而而直接做题
#                    return "<h1>请刷新页面后再开始做题</h1>"
#            if input["A%s"%row] not in TEST.problem:#判断题目是否在题库中，防止非法提交
#                return '<h1>Please refresh before test<br/><br/><a href="/test/">back</a></h1>'
            std_ans,num= self.os.get_answer(input["A%s"%row])
            user_ans = []
            user_all_ans = []
            tag=0
            for line in map(chr,range(66,71)):#65-71/
                a = "%s%s"%(line,row)
                input[a]=input[a].upper().replace(" ","") #删除用户输入的两边空格，并将字母转成大写
#                print input[a]
                user_all_ans.append(input[a])
#                    print input[a]
                #回答正确的标准：输入的信息在正确答案中并且输入的信息不重复
                if (input[a] in std_ans) and (input[a] not in user_ans) and input[a]!='':
                    user_ans.append(input[a])
                    self.accept += 1
                    tag+=1
            #统计出错题目
            if tag<num and input["A%s"%row] not in error_pro:
                error_user.append(user_all_ans)
                error_pro.append('%s'%input["A%s"%row])
                right_ans.append(std_ans)
        print "total2",self.total_blank
        score = int(self.accept*100/TEST.total_blank)#计算成绩
        print "score=",score
        self.os.save_score(score)   #保存成绩
        TEST.session=1
        env = Environment(loader=PackageLoader('osweb', './'))#成绩页面
        template = env.get_template('rank.html')
        num = range(len(error_pro))
        return template.render(num = num,err_ans=error_user,score=score,rank=self.os.get_rank(score),problem=error_pro,answer=right_ans)
#        except:
 #           return '<h1>System Error<br/><br/><a href="/">back</a></h1>'


#首页
class INDEX():
    def GET(self):
        try:
            env = Environment(loader=PackageLoader('osweb', './'))
            template = env.get_template('index.html')
            return template.render()
        except:
            return '<h1>System Error<br/><br/><a href="/">back</a></h1>'

if __name__=="__main__":
    app.run()
#    test = OS()
#    test.get_problem(6)
#    test.get_answer("OS设计目标")
application = app.wsgifunc()
