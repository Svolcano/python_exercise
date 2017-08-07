#!/usr/bin/python
#encoding=utf-8

import os
import time
import re
import threading
import sys
import MySQLdb
class FileCleaner():
	def __init__(self):
		self.fileLists=[]
		self.sliceLists=[]
		self.threads = [] 
		self.db = myDB()
		self.db.initDB('192.168.1.103','scw','112233','dirData')
		self.sql = 'insert into delfiles(name,createtime) values'
		

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
					strTime = time.strftime('%Y%m%d%H%M%S')
					sql = '(\'%s\',\'%s\'),'%(f,strTime)
					FileCleaner.self.sql.append(sql)
					print self.sql
					

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

	def cleaner(self,fsplit):
		'delete slice of fileLists '
		for f in fsplit:
			#os.remove(f)
			#print "*"*8 + f
			pass

	def splitFileLists(self):
		'split fileList to 10 slices'
		fllen = len(self.fileLists)
		c = fllen / 10
		for i in range(9):
			self.sliceLists.append(self.fileLists[i*c:(i+1)*c])
		if 9*c < fllen :
			self.sliceLists.append(self.fileLists[9*c:fllen])

	
	def doClean(self):
		print 'clean is starting....',time.ctime()
		self.splitFileLists()
		sliceCounter = len(self.sliceLists)
		for i in range(sliceCounter):
			self.tmpThread = threading.Thread(target=self.cleaner,args=(self.sliceLists[i],))
			self.threads.append(self.tmpThread)

		for i in range(sliceCounter):
			print 'thread %d begin..........'%i
			self.threads[i].setDaemon(True)
			self.threads[i].start()
			print 'thread %d end..........'%i
		print 'all Thread over!',time.ctime()

class myDB():
	def __init__(self):
		pass

	def initDB(self,host,user,pwd,dbname):
		self.conn = MySQLdb.connect(host=host,user=user,passwd=pwd,db=dbname)
		self.cursor = self.conn.cursor()
	
	def myexec(self,sqlStr,param):
		return self.cursor.execute(sqlStr,param)

	def close():
		self.conn.close()

if __name__ == '__main__':
	fh = open('log.txt','w+')
	old = sys.stdout
	sys.stdout = fh
	fc = FileCleaner()
	fc.getFileLists('/root',1.2)
	fc.doClean()
	sys.stdout = old

	#db test

	print 'done'

