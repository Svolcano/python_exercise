import subprocess
import hashlib
import logging

logger = logging.getLogger(__name__)

def verify_license_valid():

    sbox_verify_file_hash_expected="2bddc9bc4740d1a0f8349f55257773fb9b4375b3"

    sha1 = hashlib.sha1()
    try:
        f = open('/usr/local/bin/sbox_verify.sh','rb')
    except Exception,e:
        logger.info(e)
        return False

    try:
        sha1.update(f.read())
    except Exception,e:
        logger.info(e)
        f.close()
        return False

    #logger.info("hash value:%s",sha1.hexdigest())

    if sbox_verify_file_hash_expected != sha1.hexdigest() :
        return False

    logger.info("pre sbox_verify.sh")

    cmd = "/usr/local/bin/sbox_verify.sh "
    ret = subprocess.call(cmd, shell=True)

    logger.info("post ret = %s",ret)

    if 1 == ret:
        return False

    if 0 == ret:
        return True

    return False


if __name__ == '__main__':

    print verify_license_valid()
