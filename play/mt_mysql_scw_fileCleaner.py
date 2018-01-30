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

	def visit(self,arg,dirname,names):
		"callback function: clean files"
		nowTime = time.time()
		try:
			conn = MySQLdb.connect(host='192.168.1.103',user='scw',passwd='112233',db='dirData')
			cursor = conn.cursor()
		except:
			print 'insert conn Error.......'
		tmpList = []
		for f in names:
			f = os.path.join(dirname,f)
			if os.path.isfile(f):
				mtime = os.path.getmtime(f)
				if nowTime - mtime >= arg[1]:
					arg[0].append(f)
					strTime = time.strftime('%Y%m%d%H%M%S')
					tmpList.append((f,strTime))
		try:	
			cursor.executemany('insert into delfiles(name,createtime) values(%s,%s)',tmpList)
		except:
			print 'insert execute error!.......'
		cursor.close()
		conn.close()


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
		os.path.walk(filePath,self.visit,arg)

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
		try:
			conn = MySQLdb.connect(host='192.168.1.103',user='scw',passwd='112233',db='dirData')
			cursor = conn.cursor()
		except:
			print "conn Error!........"
		for f in fsplit:
			#os.remove(f)
			try:
				print	cursor.execute('delete from delfiles where name=\'%s\'' % f)
			except:
				print "excute error!......."
		cursor.close()
		conn.close()

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
			self.threads[i].setDaemon(False)
			self.threads[i].start()
			#self.threads[i].join()
			print 'thread %d end..........'%i

		print 'all Thread over!',time.ctime()

if __name__ == '__main__':
	fh = open('log.txt','w+')
	old = sys.stdout
	sys.stdout = fh
	fc = FileCleaner()
	fc.getFileLists('/root/workspace/',1.2)
	fc.doClean()
	sys.stdout = old
