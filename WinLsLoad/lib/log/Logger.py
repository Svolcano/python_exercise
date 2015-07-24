import logging
import os
import sys
import platform
from logging.handlers import RotatingFileHandler

from GetScriptDir import current_file_directory

class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger    = logger
      self.log_level = log_level
      self.linebuf   = ''
 
   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())

def logging_init(logger_name, logger_directory, level=logging.DEBUG, screen=False):
    formatter = logging.Formatter('%(asctime)s-%(name)s-[TID:%(thread)d][%(filename)s](%(funcName)s)[line:%(lineno)d]%(levelname)s:%(message)s')
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.propagate = 0

    if 'Windows' == platform.system() :#windows platform
        logger_dir=current_file_directory()
        logger_path = logger_dir + os.sep +logger_name+'.log'
        rh = RotatingFileHandler(logger_path, maxBytes=10*1024*1024, backupCount=5)
        rh.setLevel(level)
        rh.setFormatter(formatter)
        logger.addHandler(rh)
    else :  #linux platform
        if True == screen:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        logger_path = logger_directory + os.sep + logger_name + '.log'
        rh = RotatingFileHandler(logger_path, maxBytes=10*1024*1024, backupCount=5)
        rh.setLevel(level)
        rh.setFormatter(formatter)
        logger.addHandler(rh)

    #stdout_logger = logging.getLogger('STDOUT')
    #sl_stdout     = StreamToLogger(stdout_logger, logging.INFO)
    #sys.stdout    = sl_stdout
 
    #stderr_logger = logging.getLogger('STDERR')
    #sl_stderr     = StreamToLogger(stderr_logger, logging.ERROR)
    #sys.stderr    = sl_stderr

