import pygtk
pygtk.require("2.0")
import gtk
import os
import logging

logger = logging.getLogger(__name__)


class ServerWidget(gtk.VBox):    
    
    APP_PATH = os.path.abspath(os.path.dirname(__name__))
    IMAGE_DIR = os.path.join(APP_PATH,"img")
    
    IMAGE_LIST = (os.path.join(IMAGE_DIR,"logo_green.png"),
                                os.path.join(IMAGE_DIR,"logo_yellow.png"),
                                os.path.join(IMAGE_DIR,"logo_red.png"))  
    IMAGE_WIDTH = 128
    IMAGE_HEIGHT = 128
    
    LABEL_WIDTH = IMAGE_WIDTH
    LABEL_HEIGHT = 40
    

        
    def __new__(cls,server_ip,run_status):
        if not server_ip  or run_status < 0 or run_status > 3:
            logger.info("ServerWidget 's parameter are wrong :%s,%s " % server_ip,str(run_status))
            return None
        cls.server_ip = server_ip
        cls.run_status = run_status
        return gtk.VBox.__new__(cls,False,0)
          
    def display(self):    
        self.label = gtk.Label(self.server_ip)
        self.label.set_size_request(self.LABEL_WIDTH,self.LABEL_HEIGHT)
        self.label.show()
        
        self.button = gtk.Button()
        self.button.connect("clicked",self.button_click,self.server_ip)
        image = gtk.Image()            
        image.set_from_file(self.IMAGE_LIST[self.run_status])
        image.set_size_request(self.IMAGE_WIDTH,self.IMAGE_HEIGHT)
        image.show()
        self.button.add(image)       
        self.button.show()
                        
        self.pack_start(self.button,True,True,2)
        self.pack_end(self.label,False,False,2)
        self.set_homogeneous(False)
        
        self.show()   
    
    def button_click(self,widget,data=None):
        ''' callback function of button clicked '''
        if not data: 
            return  
        self.status_bar = None
        fixed_layout  = self.get_parent();     #get win
        if fixed_layout:
            vbox = fixed_layout.get_parent()
            children = vbox.get_children()
            for child in children:
                if isinstance(child,gtk.Statusbar):
                    self.status_bar = child
                    break 
        if  self.status_bar:
            self.context_id =self.status_bar.get_context_id("lsLoad")
            self.status_bar.pop(self.context_id)
            self.status_bar.push(self.context_id,"connectted to: %s" % data)
            
        os.system('gnome-terminal -x ssh %s ' %  data)
        




if __name__ == "__main__":
    
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    
    '''
    hbox = gtk.HBox(True,20)
    win.set_size_request(800,600)
    win.set_resizable(False)
    
    sw = ServerWidget('192.168.1.103',1)
    sw.display()
    
    hbox.add(sw)
    hbox.set_resize_mode()
    hbox.show()
    
    win.add(hbox)
    '''
    fixed = gtk.Fixed()
    sw = ServerWidget('192.168.1.70',1)
    sw.display()
    fixed.put(sw,0,0)
    
    sw = ServerWidget('192.168.1.18',2)
    sw.display()
    fixed.put(sw,sw.IMAGE_WIDTH,0)

    fixed.show()
    win.add(fixed)
    win.set_size_request(800,600)
    win.show()
    
    gtk.main()
    