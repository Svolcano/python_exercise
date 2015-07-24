#!/usr/bin/env python
#_*_ coding:utf-8 _*_

import gtk
import pygtk
pygtk.require('2.0')
import os
import logging
from ServerWidget import ServerWidget

from lib.db.tab_load_server import tab_load_server
from lib.db.tab_load_info import tab_load_info
from SvrConfig import get_mysql_host

from lib.log.Logger import logging_init

logger = logging.getLogger(__name__)

class MainWindow(object):   
    
    WIN_WIDTH = 800
    WIN_HEIGHT = 600
    
    def __init__(self):
        '''  do some init works '''
        #init sql
        mysql_host = get_mysql_host()
        self.servers_db = tab_load_server(mysql_host, 'sboxweb', 'Sbox123456xZ', 'sbox_db')
        self.load_info_db = tab_load_info(mysql_host, 'sboxweb', 'Sbox123456xZ', 'sbox_db')     
        self.msg_id = -1
        self.context_id = -1
    def create_window(self):
        ''' create window '''
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.connect("destroy",self.quit,'bye')
        self.win.set_title("LsLoad-Window")
        self.win.set_size_request(self.WIN_WIDTH,self.WIN_HEIGHT)     #w & h      
     
    def create_menu_bar(self):
        '''  create window menu   '''  
        
        refresh_menu = gtk.MenuItem("ReFresh")
        refresh_menu.connect("activate",self.refresh)
        refresh_menu.show()       
        
        self.menu_bar = gtk.MenuBar()
        self.menu_bar.append(refresh_menu)
        self.menu_bar.show()           
    
    def create_status_bar(self):
        ''' create status bar  '''
        self.status_bar = gtk.Statusbar()
        self.context_id = self.status_bar.get_context_id("lsLoad")        
    
    def show_statusbar_msg(self,msg):
            self.status_bar.pop(self.context_id)
            self.msg_id = self.status_bar.push(self.context_id,msg)      
    
    def get_servers(self): 
        logger.info("Function :get_servers")        
        rtn, servers = self.servers_db.get_servers()
        if rtn:
           self.show_statusbar_msg("server info loads compete!")
        else:
            self.show_statusbar_msg("something wrong with db query!")        
        return (rtn, servers)
    
    def refresh(self,widget,data=None):
        ''' call back function  of refresh menu'''
        self.del_server_from_win()
        self.add_server_to_win()
        self.show_statusbar_msg("refresh done!")
    
    def quit(self,widget,data=None):
        gtk.main_quit()   
     
    def get_run_status(self,server_ip):
        '''  get server's status '''
        run_status = 1         
        return run_status
    
    def del_server_from_win(self):
        ''' clear all server displayed '''
        vbox = self.win.get_child()
        children = vbox.get_children()
        for child in children:
            if isinstance(child,gtk.Fixed):
                fixed_layout = child
                break        
        vbox.remove(fixed_layout)
            
    def add_server_to_win(self):
        ''' add all server to windows '''
        rtn,server_list = self.get_servers()        
        if not rtn:
            return 
        fixed_layout = gtk.Fixed()
        fixed_layout.show()     
        x = 0
        y = 0
        step_width = ServerWidget.IMAGE_WIDTH+20
        step_height = ServerWidget.IMAGE_HEIGHT+20
        for server in server_list:
            ip = server[0]
            run_status =  self.get_run_status(ip)
            sw = ServerWidget(ip,run_status)
            sw.display()                        
            if x+step_width > self.WIN_WIDTH :
                x = 0
                y += step_height
            fixed_layout.put(sw,x,y)
            x+=step_width
        vbox =self.win.get_child()
        vbox.pack_start(fixed_layout,True,True,0)
           
    def display(self):
        ''' show all window'''
        self.create_window()
        self.create_menu_bar()
        self.create_status_bar()
        
        vbox = gtk.VBox(False,10)
        vbox.pack_start(self.menu_bar,False,False,0)
        vbox.pack_end(self.status_bar,False,False,0)                    
        self.win.add(vbox) 
           
        self.add_server_to_win()
                   
        self.win.show_all()
        self.show_statusbar_msg("welcome to lsLoad windows!")   
        
    def main(self):
        gtk.main()


if __name__ == "__main__":
    win = MainWindow()
    win.display()
    win.main()
    