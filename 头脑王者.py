__author__ = '黄文洋'
# -*- coding:utf-8 -*-

import pytesseract
import os
import subprocess
import requests
import random
import time
from aip import AipOcr
from io import BytesIO
from PIL import Image

config = {
	'头脑王者':{
		'question':(80, 500, 1000, 880),
		'answers':(80, 960, 1000, 1720),
		'point':[
			(316, 933, 723, 1078),
			(316, 1174, 723, 1292),
			(316, 1366, 723, 1469),
			(316, 1570, 723, 1657),
		]
	}
}

# 获取手机截图
def get_screenshot():
	# 执行adb命令
	process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
	# 获取截图二进制内容
	screenshot = process.stdout.read()
	# 格式化,安卓和windows
	screenshot = screenshot.replace(b'\r\n',b'\n')
	# 把截图存到内存
	img_fb = BytesIO()
	img_fb.write(screenshot)
	# img = open('autojump.png', 'wb')
	# img.write(screenshot)
	# img.close()
    # 图片处理
	img = Image.open(img_fb)
	# 切出题目
	title_img = img.crop((80,500,1000,880))
	# 切出答案
	answers_img = img.crop((80,960,1000,1720))
	# 拼接
	new_img = Image.new('RGBA',(920,1140))
	new_img.paste(title_img, (0,0,920,380))
	new_img.paste(answers_img,(0,380,920,1140))
	# 内存对象
	new_img_fb = BytesIO()
	new_img.save(new_img_fb, 'png')
	return new_img_fb

def img_to_word(img):
    APP_ID = '10715440'
    APP_KEY = 'zVUUNVVGjuGsMtGMkebKGPzj'
    SECRET_KEY = 'dsGIGhvrWeY0qLfpdK1TXuMGVII9QXl8'
    client = AipOcr(APP_ID,APP_KEY,SECRET_KEY)
    res = client.basicGeneral(img)
    # pytesseract.pytesseract.tesseract_cmd='H:/python/Tesseract-OCR/tesseract'
    # subject = pytesseract.image_to_string(p,lang='chi_sim')
    # subject = "".join(subject.split())
    # subject = subject.split('.')[0]
    return res

# 帮我们搜索并算出最有可能的答案
def baidu(question, answers):
    url = 'https://www.baidu.com/s'
    headers = {
       'User-Agent':'Mozilla/5.0(Windows NT 10.0; WOW64; rv:57.0)Gecko/20100101 Firefox/57.0'
    }
    data = {
    	'wd':question
    }
    res = requests.get(url, params=data, headers=headers)
    res.encoding = 'utf-8'
    html = res.text
    # 分析
    for i in range(len(answers)):
    	answers[i] = (html.count(answers[i]), answers[i], i)
    answers.sort(reverse=True)
    return answers

# 根据搜索到的答案,点击屏幕
def click(point):
	cmd = 'adb shell input swipe %s %s %s %s %s'%(
		point[0],
		point[1],
		point[0] + random.randint(0, 3),
		point[1] + random.randint(0, 3),
		200
	)
	os.system(cmd)


# 主函数
def main():
	print("请准备开始答题!")
	while True:
		input("请输入回车开始解题:")
		start = time.time()
		# 获取手机截图
		img = get_screenshot()
		# 提取文字
		info = img_to_word(img.getvalue())
		if info['words_result_num'] < 5:
			continue
		# print(info)
		answers = [x['words']for x in info['words_result'][-4:]]
		question = ''.join([x['words']for x in info['words_result'][:-4]])
		print(question)
		res = baidu(question, answers)
		click(config['头脑王者']['point'][res[0][2]])
		print("耗时:" + str(time.time() - start))

if __name__ == '__main__':
	main()