import json
import time
import traceback

import xlwt
from bs4 import BeautifulSoup
import requests
import hashlib

headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"Connection": "keep-alive",
}


def log(level, msg):
	print("[" + time.strftime('%H:%M:%S', time.localtime(time.time())) + "] [" + level + "]: " + msg)


def parse_score(html):
	soup = BeautifulSoup(html, 'html.parser')
	trs = soup.findAll("tr")
	result = {}
	for tr in trs:
		if tr.parent.name == "thead":
			continue
		tds = tr.findAll("td")
		result[tds[0].getText()] = tds[1].getText()
	return result


def get_sessionid():
	response1 = requests.get("http://www.dgcz.cn/jjwtMobile/CasmCenter/login.jsp")
	return response1.cookies["JSESSIONID"]


def login(username, password, h):
	response2 = requests.post("http://www.dgcz.cn/jjwtMobile/login.htm", data={"username": username, "password": password}, headers=h)
	response3 = requests.get("http://www.dgcz.cn/jjwtMobile/main.htm?action=stu", headers=h)
	if response3.url.find("token=") == -1:
		return None
	else:
		return response3.url[response3.url.find("token=") + 6:len(response3.url)]


def get_score(h, examid):
	response4 = requests.get("http://www.dgcz.cn/jjwtMobile/getclazzexamsub.htm", headers=h)
	response7 = requests.post("http://www.dgcz.cn/jjwtMobile/getscore.htm", headers=h, data={"exam": examid})
	response8 = requests.get(response7.url, headers=h)
	return response8.text


def write_to_book(scores):
	workbook = xlwt.Workbook(encoding='utf-8')
	worksheet = workbook.add_sheet('test')
	worksheet.write(0, 0, "涂卡号")
	worksheet.write(0, 1, "九总")
	worksheet.write(0, 2, "三总")
	worksheet.write(0, 3, "语文")
	worksheet.write(0, 4, "数学")
	worksheet.write(0, 5, "英语")
	worksheet.write(0, 6, "历史")
	worksheet.write(0, 7, "物理")
	worksheet.write(0, 8, "化学")
	worksheet.write(0, 9, "生物")
	worksheet.write(0, 10, "政治")
	worksheet.write(0, 11, "地理")
	r = 1
	for (id, ss) in scores.items():
		worksheet.write(r, 0, id)
		worksheet.write(r, 1, ss["九总"] if ss["九总"] != "" else "0.0")
		worksheet.write(r, 2, ss["三总"] if ss["三总"] != "" else "0.0")
		worksheet.write(r, 3, ss["语文"] if ss["语文"] != "" else "0.0")
		worksheet.write(r, 4, ss["数学"] if ss["数学"] != "" else "0.0")
		worksheet.write(r, 5, ss["英语"] if ss["英语"] != "" else "0.0")
		worksheet.write(r, 6, ss["历史"] if ss["历史"] != "" else "0.0")
		worksheet.write(r, 7, ss["物理"] if ss["物理"] != "" else "0.0")
		worksheet.write(r, 8, ss["化学"] if ss["化学"] != "" else "0.0")
		worksheet.write(r, 9, ss["生物"] if ss["生物"] != "" else "0.0")
		worksheet.write(r, 10, ss["政治"] if ss["政治"] != "" else "0.0")
		worksheet.write(r, 11, ss["地理"] if ss["地理"] != "" else "0.0")
		r += 1
	workbook.save('D:/qwq12.xls')


def save_score(examid):
	fail_list = []
	score_null = []
	scores = {}
	known_password = {}
	for i in range(1, 1304, 1):
		try:
			un = "2020" + str(i).zfill(6)
			if un in known_password.keys():
				pw = known_password[un]
			else:
				pw = hashlib.md5("123456".encode("utf-8")).hexdigest()
			log("INFO", "logging in " + un)
			sid = get_sessionid()
			headers["Cookie"] = "JSESSIONID=" + sid
			token = login(un, pw, headers)
			if token is None:
				fail_list.append(un)
				log("WARNING", un + " login failed")
				continue
			score = parse_score(get_score(headers, examid))
			if score == {}:
				score_null.append(un)
				continue
			if score["九总"] == "":
				score_null.append(un)
				continue
			scores[un] = score
			log("INFO", un + " get score success: " + json.dumps(score, ensure_ascii=False))
		except Exception as e:
			fail_list.append(un)
			log("ERROR", str(e))
	print("failed list: " + json.dumps(fail_list))
	print("score error list: " + json.dumps(score_null))
	print(json.dumps(scores, ensure_ascii=False))
	write_to_book(scores)


if __name__ == "__main__":
	un = input("请输入学号: ")
	pw = hashlib.md5(input("请输入密码: ").encode("utf-8")).hexdigest()
	sid = get_sessionid()
	log("INFO", "JSESSIONID: " + sid)
	headers["Cookie"] = "JSESSIONID=" + sid
	log("INFO", "logging in " + un)
	token = login(un, pw, headers)
	if token is None:
		log("WARNING", "login failed!")
		exit(0)
	log("INFO", "token: " + token)
	log("INFO", "getting score...")
	html = get_score(headers, "3")
	log("INFO", "parsing score...")
	score = parse_score(html)
	print(score)
	print("========score========")
	for (k, v) in score.items():
		print(k + "  " + v)
	# save_score()
