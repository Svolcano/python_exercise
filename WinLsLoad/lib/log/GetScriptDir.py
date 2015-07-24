import os,sys

def get_log_and_db_directory():
    dir = os.environ['HOME'] + os.sep + '.log'
    try :
        os.mkdir(dir)
    except Exception,e:
        return dir
    return dir

def current_file_directory():
    '''Get the file LoginRecord.py path
    
    Args:
    Returns:
    The file LoginRecord.py path,eg:/home/xinyao/login_record.db
    '''
    import platform,os
    if 'Windows' == platform.system():
        str_path = os.environ['AppData']
        str_path = str_path + os.sep + 'bitguard'
        str_path_flag = os.path.exists(str_path)
        if False == str_path_flag :
            os.mkdir(str_path)
        return str_path
    else :
        import sys, inspect
        path = os.path.realpath(sys.path[0])        # interpreter starter's path
        if os.path.isfile(path):                    # starter is excutable file
            path = os.path.dirname(path)
            return os.path.abspath(path)            # return excutable file's directory  
        else:                                       # starter is python script
            caller_file = inspect.stack()[1][1]     # function caller's filename
            return os.path.abspath(os.path.dirname(caller_file))# return function caller's file's directory

def join_upper_level_path(split_list,lens):
    '''
    the function of combined directory
    '''
    path = ''
    for i in range(0,(lens-1)):
        path = path + split_list[i]
        if i != (lens-2):
            path = path + os.sep
    return path

def get_filename_path(filename):
    path = os.path.realpath(__file__)
    path_split = []
    path_split = path.split(os.sep)
    len_split = len(path_split)
    len2 = len_split
    while len2>1 :
        dir = join_upper_level_path(path_split,len2)
        path_filename = dir + os.sep + filename
        path_exist = os.path.exists(path_filename)
        if True == path_exist :
            return path_filename
        len2 = len2-1
    return ''

if __name__ == '__main__':
    print current_file_directory()
    print get_filename_path('screen.png')
