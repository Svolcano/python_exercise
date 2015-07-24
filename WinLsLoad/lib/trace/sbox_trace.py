import traceback
import logging

logger = logging.getLogger(__name__)

def log_traceback():
    logger.error(get_traceback_string())

def get_traceback_string():
    formatted_lines = traceback.format_exc().splitlines()
    return "\r\n".join(formatted_lines)

if __name__ == '__main__':
    try:
        raise Exception
    except Exception,e:
        print get_traceback_string()
        print log_traceback()
