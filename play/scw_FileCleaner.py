#!/usr/bin/python
#encoding=utf-8

import os
import time
import re
class FileCleaner():
	@staticmethod
	def __visit(arg,dirname,names):
		"callback function: clean files"
		nowTime = time.time()
		for f in names:
			f = os.path.join(dirname,f)
			if os.path.isfile(f):
				mtime = os.path.getmtime(f)
				if nowTime - mtime >= arg:
					#os.remove(f)
					print nowTime-mtime ,'>',arg,f, 'done'
	@staticmethod
	def clean(filePath,cleanTime):
		"filePath is the one you want to clean;clearTime's unit is day"
		if not os.path.exists(filePath):
			print 'filePath does\'t exists!'
			return
		if not FileCleaner.isNum(cleanTime):
			print 'Time is wrong !'
			return 
		cleanSeconds = cleanTime * 3600
		os.path.walk(filePath,FileCleaner.__visit,cleanSeconds)

	@staticmethod
	def isNum(number):
		number = str(number)
		m1 = re.match('\d+[\.\d]?\d*',number);
		if m1 == None:
			return False
		else:
			return True
if __name__ == '__main__':
	FileCleaner.clean('/root',1.2)
