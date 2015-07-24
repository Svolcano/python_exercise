# _*_ coding: utf-8 _*_
import os
import logging
from subprocess import call

def join_dir_path(split_list,n):
    '''
    the function of combined directory
    '''
    #lens = len(split_list)
    path = '/'
    for i in range(2,n):
        path = path + split_list[i]
        if i != (lens-2):
            path = path + '/'

    logger.debug(path)
    return path

def join_path(split_list,n):
    '''
    the function of combined path
    '''
    lens = len(split_list)
    path = '/'
    for i in range(2,n):
        path = path + split_list[i]
        if i != (lens-1):
            path = path + '/'

    logger.debug(path)
    return path

def split_path(path):
    '''
    split the path string with '/'.
    Args:
        path:the path which the monitor gets.
    Return:
        return path list.
    '''
    ret = []
    while path != '/':
        a = os.path.split(path)
        ret.append(a[1])
        path = a[0]

    ret.reverse()
    return ret

if __name__ == '__main__':
    print get_netname('/BGsftp/br1.ext/user1/import/a.txt') 
    print get_username('/BGsftp/br1.ext/user1/import/a.txt') 
    print get_port('/BGsftp/br1.ext/user1/import/a.txt') 
    print get_netname('/BGsftp/br1.ext/user1/export/a.txt') 
    print get_username('/BGsftp/br1.ext/user1/export/a.txt') 
    print get_port('/BGsftp/br1.ext/user1/export/a.txt') 
