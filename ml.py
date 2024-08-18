import pymysql
from init import *

class Mysql:
    """初始化"""

    def __init__(self, ip, port, user, pwd):
        self.mysql_on_off = False
        # 连接数据库
        try:
            self.cone = pymysql.connect(host=ip, port=port, user=user, password=pwd, charset='utf8')
            self.cursor = self.cone.cursor()
            self.mysql_on_off = True
            logger.info(f"ip: {ip},port: {port}，user: {user}, password: {pwd}")
            # 初始化方法
        except Exception as f:
            logger.error(f"连接出现错误:{f}")
        # 启动后台检测

    """初始化数据"""

    def init_data(self):
        if self.mysql_on_off:
            logger.info(f"检测数据库")
            # 获取数据表
            self.cursor.execute('show databases')
            table = self.cursor.fetchall()
            # 对比-筛选
            data = ["teacher", "student", "course", "class", "grades", "attendance"]
            for i in table:
                for j in data:
                    if j == i[0]:
                        data.remove(j)
            # 将没有的创建数据库
            if data:
                logger.warning(f"数据库缺少表 : {data}")
                for i in data:
                    self.cursor.execute(f"create database {i} DEFAULT CHARSET utf8 COLLATE utf8_general_ci")
                    logger.info(f"数据库: {i} 已创建")
            else:
                logger.info(f"数据库完整")
            return True
        else:
            return False