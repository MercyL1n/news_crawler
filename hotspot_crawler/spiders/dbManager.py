#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/7/1 17:00
# @Author : My
# @Contact : lmy@bupt.edu.cn
# @desc : 数据库管理类
import traceback
import pymysql
from pymysql import escape_string


class MysqlOperation:
    def __init__(self):
        # 1. 建立数据库的连接
        self.connect = pymysql.connect(
            # localhost连接的是本地数据库
            host='120.26.184.50',
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
            insert_sql = "insert into text_storage values (null,'" + url + "','" + hashcode + "','" + \
                         escape_string(title) + "','" + sql_datetime + "','" + escape_string(content) + "');"
            # 执行sql语句
            self.cursor.execute(insert_sql)
            # 4. 提交操作
            self.connect.commit()
        except Exception as e:
            # 输出异常信息
            # 忽略重复插入错误
            if e.args[0] != 1062:
                print(e)
            self.connect.rollback()

    def get_website_list(self):
        try:
            get_list_sql = "SELECT * FROM `websites`"
            self.cursor.execute(get_list_sql)
            results = self.cursor.fetchall()
            return results
        except:
            # 输出异常信息
            traceback.print_exc()

    def dis_connect(self):
        self.connect.close()
