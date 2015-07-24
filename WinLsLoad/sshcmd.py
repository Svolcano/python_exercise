#!/usr/bin/env python 
#_*_ coding:utf-8 _*_

import pygtk
pygtk.require("2.0")
import gtk
import os


class ServerWidget(gtk.Button,gtk.Label):
    
    
    APP_PATH = os.path.abspath(os.path.dirname(__name__))
    IMAGE_DIR = os.path.join(APP_PATH,"img")
    
    def __init__(self,server_ip,run_status): 
        gtk.Button.__init__(self)
        gtk.Label.__init__(self)       
        self.label = gtk.Label(server_ip)
        self.label.show()
        
        self.button = gtk.Button()
        logo_file = os.path.abspath(os.path.join(ServerWidget.IMAGE_DIR,"logo.png"))
        logo = gtk.gdk.pixbuf_new_from_file(logo_file) 
             
        self.button.set_image(logo)
        self.button.show()
        
        self.vbox = gtk.VBox(True,0)
        self.vbox.pack_start(self.button,True,True,0)
        self.vbox.pack_start(self.label,True,True,0)
        
    def show(self):
        self.vbox.show()


if __name__ == "__main__":
    sw = ServerWidget("192.168.1.103",1)
    sw.show()
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.add(sw)
    win.show()
    gtk.main()