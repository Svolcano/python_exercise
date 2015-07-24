#!/usr/bin/python
# _*_ coding: utf-8 _*_

import ConfigParser
import os

def get_mysql_host():
    cf = ConfigParser.RawConfigParser()
    if not os.path.exists("load_check.conf"):
        cf.add_section("database")

        cf.set("database", "host", "localhost")

        with open('load_check.conf', 'wb') as configfile:
            cf.write(configfile)

    cf.read("load_check.conf")
    return cf.get("database", "host")
 
if __name__ == '__main__':
    a = get_mysql_host()
    print type(a)
    print a
    print '------'
     

