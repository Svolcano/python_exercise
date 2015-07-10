#!/usr/bin/python
#encoding=utf-8

import os
import time
import re
import threading
import sys
class FileCleaner():
	def __init__(self):
		self.fileLists=[]
		self.sliceLists=[]
		self.threads = [] 

	@staticmethod
	def __visit(arg,dirname,names):
		"callback function: clean files"
		nowTime = time.time()
		for f in names:
			f = os.path.join(dirname,f)
			if os.path.isfile(f):
				mtime = os.path.getmtime(f)
				if nowTime - mtime >= arg[1]:
					arg[0].append(f)
	def getFileLists(self,filePath,cleanTime):
		"filePath is the one you want to clean;clearTime's unit is day"
		if not os.path.exists(filePath):
			print 'filePath does\'t exists!'
			return
		if not FileCleaner.isNum(cleanTime):
			print 'Time is wrong !'
			return 
		cleanSeconds = cleanTime * 3600 * 24
		arg = (self.fileLists,cleanSeconds)
		os.path.walk(filePath,FileCleaner.__visit,arg)

	@staticmethod
	def isNum(number):
		number = str(number)
		m1 = re.match('\d+[\.\d]?\d*',number);
		if m1 == None:
			return False
		else:
			return True
	def cleaner(self,arg):
		'delete slice of fileLists '

		for f in arg:
			#os.remove(f)
			print "*"*8 + f
			pass
	def splitFileLists(self):
		'split fileList to slices'
		fllen = len(self.fileLists)
		for i in range(0,fllen,10):
			self.sliceLists.append(self.fileLists[i:i+10])

	def doClean(self):
		print 'clean is starting....',time.ctime()
		self.splitFileLists()
		sliceCounter = len(self.sliceLists)
		for i in range(sliceCounter):
			self.tmpThread = threading.Thread(target=self.cleaner,args=(self.sliceLists[i],))
			self.threads.append(self.tmpThread)

		for i in range(sliceCounter):
			self.threads[i].setDaemon(True)
			self.threads[i].start()
		print 'all Thread over!',time.ctime()
		
if __name__ == '__main__':
	fh = open('log.txt','w+')
	old = sys.stdout
	sys.stdout = fh
	fc = FileCleaner()
	fc.getFileLists('G:/',1.2)
	fc.doClean()
	sys.stdout = old
	print 'done'

