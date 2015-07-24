from subprocess import call
from subprocess import Popen
import logging
import locale
import sys

logger = logging.getLogger(__name__)


class cmd_basic:

    def __init__(self):
        pass

    def call(self, cmd):
        #logger.info("%s", cmd)
        root_logger = logging.getLogger()
        logger.info("logger.handlers:%s", root_logger.handlers)
        logger.info("locale preferredencoding:%s", locale.getpreferredencoding())
        logger.info("sys.getfilesystemencoding:%s", sys.getfilesystemencoding())
        return call(cmd.encode(locale.getpreferredencoding()), shell=True)

    def Popen(self, cmd):
        #logger.info("%s", cmd)
        logger.info("locale preferredencoding:%s", locale.getpreferredencoding())
        logger.info("sys.getfilesystemencoding:%s", sys.getfilesystemencoding())
        return Popen(cmd.encode(locale.getpreferredencoding()), shell=True)


