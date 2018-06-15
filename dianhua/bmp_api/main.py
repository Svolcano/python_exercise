# -.- coding:utf-8 -.-
import os
import sys
import tornado.httpserver
import tornado.ioloop
import tornado.web
import logging
from logging.handlers import RotatingFileHandler

reload(sys)
sys.setdefaultencoding('utf8')
package_path = os.path.abspath(__file__)
package_path = os.path.dirname(package_path)
package_path = os.path.join(package_path, '..')
sys.path.append(package_path)

from bmp_api.bmp_lib.DailyReportHandler import DailyReportHandler
from bmp_api.bmp_lib.CpReportSummaryHandler import CpReportSummaryHandler
from bmp_api.bmp_lib.CpReportDetailHandler import CpReportDetailHandler
from bmp_api.bmp_lib.BillStaticHandler import BillStaticHandler
from bmp_api.bmp_lib.Constant import ConstantVar, SUtils

logger = logging.getLogger()


if __name__ == "__main__":
    """
    bmp api  main
    """
    formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d]-%(funcName)s- %(levelname)s: %(message)s')
    log_file_handler = RotatingFileHandler(filename="bmp_api_log.log", maxBytes="10485760", backupCount=2, encoding='utf8')
    log_file_handler.setFormatter(formatter)
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    log.addHandler(log_file_handler)
    SUtils.init()
    try:
        app = tornado.web.Application(
            handlers=[
                (r"/api/daily_report", DailyReportHandler),
                (r"/api/complex_report_summary", CpReportSummaryHandler),
                (r"/api/complex_report_detail", CpReportDetailHandler),
                (r"/api/bill_static_report", BillStaticHandler),
            ],
            debug=False
        )
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(ConstantVar.tornado_port)
        tornado.ioloop.IOLoop.instance().start()
    except Exception as e:
        logger.info(e)
    finally:
        logger.info("release socket resource peacefully")
        tornado.ioloop.IOLoop.instance().stop()