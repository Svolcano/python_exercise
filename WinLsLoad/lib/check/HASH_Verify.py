import subprocess
import logging

logger = logging.getLogger(__name__)

def verify_passwd(user, password):
    cmd = "grep %s /etc/shadow | awk -F : '/%s/ {if ($1 == \"%s\"){print $2}}'" % (user, user, user)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output, errors = p.communicate()
    shadow_password = output.strip()

    logger.info("user:%s,password:%s,shadow_password:%s", user, password, shadow_password)

    if "" == shadow_password:
        return -1

    if shadow_password != password:
        return -1

    return 0

