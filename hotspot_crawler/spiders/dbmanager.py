import traceback
import pymysql


class MysqlOperation():
    def __init__(self):
        # 1. 建立数据库的连接
        self.connect = pymysql.connect(
            # localhost连接的是本地数据库
            host='localhost',
            # mysql数据库的端口号
            port=3306,
            # 数据库的用户名
            user='root',
            # 本地数据库密码
            passwd='20200406',
            # 数据库名
            db='covid_db',
            # 编码格式
            charset='utf8'
        )
        # 2. 创建一个游标cursor, 是用来操作表。
        self.cursor = self.connect.cursor()

    def insert_data(self, url, hashcode, title, sql_datetime, content):
        try:
            insert_sql = "insert into text_storage values (null,'" + url + "','" + hashcode + "','" + title + "','" + sql_datetime + "','" + content + "');"
            # 执行sql语句
            self.cursor.execute(insert_sql)
            # 4. 提交操作
            self.connect.commit()
        except:
            # 输出异常信息
            traceback.print_exc()

    def dis_connect(self):
        self.connect.close()
