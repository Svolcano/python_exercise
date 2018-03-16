import logging
import random
def xx():
    print("from a")


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logging.info('1232')


for i in range(10):
    print(random.randint(0, 2))