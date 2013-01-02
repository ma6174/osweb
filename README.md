<head><meta charset="UTF-8"></head>
#操作系统词汇在线测试软件

###功能
- 测试操作系统词汇的掌握程度
- 可以选择难度系数
- 自动根据难度系数和空数确定提交时间
- 时间到自动提交
- 随机抽取题目
- 测试页面防止复制，防止粘贴，防止右键
- 自动计算成绩
- 自动统计排名
- 自动给出正确答案

###实现
整个程序用python的web.py模块进行驱动，使用sqlite3数据库存储题目和排名数据。
使用jinja2作为模板引擎。前台页面用HTML，CSS实现，由后台通过jinja2添加内容。
时间控制和自动提交控制，还有防止复制，粘贴，右键等功能由Javascript实现。

###架设方法
- 下载源码：`git clone git@github.com:ma6174/osweb.git`
- 安装python相关模块
> `easy_install web.py`  
  `easy_install jinja2`

- 执行：`python osweb.py 80`
- 本地访问：`http://127.0.0.1/`

###其他
- 前台美工：zhangchengzhi
- 后台设计：ma6174
