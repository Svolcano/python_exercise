#coding:utf8


import wx
import time
import datetime
import sys
import os
module_path = os.path.abspath(__file__)
module_path = os.path.dirname(module_path)
module_path = os.path.join(module_path, '..')
sys.path.append(module_path)

from lib.MainFrame import MainFrame

app = wx.App()
win.Show(True)
app.MainLoop()


