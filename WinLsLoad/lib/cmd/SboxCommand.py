
import logging
import subprocess

from cmd_basic import cmd_basic

logger = logging.getLogger(__name__)

class SboxCommand():

    def __init__(self):
        self.cmd = cmd_basic()

    def sbox_useradd(self, user, passwd):
        cmd = "sbox_useradd.sh %s '%s'" % (user, passwd)
        self.cmd.call(cmd)

    def sbox_userdel(self, user):
        cmd = "sbox_userdel.sh %s" % user
        self.cmd.call(cmd)

    def sbox_chpass(self, user, passwd):
        cmd = "sbox_chpass.sh %s '%s'" % (user, passwd)
        return self.cmd.call(cmd)

    def sbox_set_fileio(self, user, netname, perm_mask):
        params = "-P %d -n %s %s" % (perm_mask, netname, user)
        cmd = "sbox_set_fileio.sh %s" % params
        self.cmd.call(cmd)

    def sbox_ifconfig(self, prot, interface, address, network, netmask, gateway, dns_type, dns1, dns2, domain_search):
        params_network_dhcp = "-p -i %s " % interface

        if None == gateway or "" == gateway:
            params_network_static = "-i %s -a %s -m %s " % (interface, address, netmask)
        else:
            params_network_static = "-i %s -a %s -m %s -g %s " % (interface, address, netmask, gateway)

        params_dns_auto = "-A"
        params_dns1 = " -1 %s " % dns1
        params_dns2 = " -2 %s " % dns2
        params_dns_man = " -s '%s' " % domain_search

        if "" != dns1:
            params_dns_man = params_dns_man + params_dns1

        if "" != dns2:
            params_dns_man = params_dns_man + params_dns2

        params = "-h"
        if 'dhcp' == prot:
            if 1 == dns_type:
                params = params_network_dhcp + params_dns_auto
            elif 2 == dns_type:
                params = params_network_dhcp + params_dns_man
        elif 'static' == prot:
            if 1 == dns_type:
                params = params_network_static + params_dns_auto
            elif 2 == dns_type:
                params = params_network_static + params_dns_man
        cmd = "sbox_ifconfig.sh %s" % params
        self.cmd.call(cmd)

    def sbox_set_dns(self, dns_type, dns1, dns2):
        params_auto = "-a"
        params_man = "-1 %s -2 %s" % (dns1, dns2)

        params = "-h"
        if '1' == dns_type:
            params = params_auto
        elif '2' == dns_type:
            params = params_man

        cmd = "sbox_set_dns.sh %s" % params
        self.cmd.call(cmd)

    def sbox_ntp_update(self, time_server):
        params = "%s" % time_server
        cmd = "sbox_ntp_update.sh %s" % params
        self.cmd.call(cmd)

    def sbox_upgrade(self, upgrade_file_name, id):
        params = "%s %s" % (upgrade_file_name, id)
        cmd = "sbox_upgrade.sh %s" % params
        self.cmd.Popen(cmd)

    def sbox_recover(self, recover_file_name, id):
        params = "%s %s" % (recover_file_name, id)
        cmd = "sbox_recover.sh %s" % params
        self.cmd.Popen(cmd)

    def sbox_ifinfo(self, interface):
        cmd = "sbox_ifinfo.sh %s" % interface

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, errors = p.communicate()
        return output.strip()
          
    def get_sbox_client_by_port(self, port):
        cmd = "get-sbox-client-by-port.sh %s" % port

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, errors = p.communicate()
        return output.strip()

    def ssoadm_ldap(self, realm_name, domain_name, domain_user, domain_password, domain_host_ip, domain_ou):
        if '' == domain_ou or None == domain_ou:
            cmd = "ssoadm_ldap.sh -r %s -d %s -u %s -p %s %s" % (realm_name, domain_name, domain_user, domain_password, domain_host_ip)
        else:
            cmd = "ssoadm_ldap.sh -r %s -d %s -u %s -p %s -o %s %s" % (realm_name, domain_name, domain_user, domain_password, domain_ou, domain_host_ip)
        return self.cmd.call(cmd)

    def ssoadm_ldap_rm(self, realm_name):
        cmd = "ssoadm_ldap_rm.sh -r %s" % realm_name
        return self.cmd.call(cmd)

    def ssoadm_nis_rm(self, realm_name):
        cmd = "ssoadm_nis_rm.sh -r %s" % realm_name
        return self.cmd.call(cmd)

    def ssoadm_ldapv3(self, realm_name, domain_name, domain_user, domain_password, domain_host_ip, domain_ou):
        if '' != domain_user and None != domain_user and '' != domain_password and None != domain_password:
            if '' != domain_ou and None != domain_ou:
                cmd = "ssoadm_ldapv3.sh -r %s -d %s -u %s -p %s -o %s %s" % (realm_name, domain_name, domain_user, domain_password, domain_ou, domain_host_ip)
            else:
                cmd = "ssoadm_ldapv3.sh -r %s -d %s -u %s -p %s %s" % (realm_name, domain_name, domain_user, domain_password, domain_host_ip)
        else:
            if '' != domain_ou and None != domain_ou:
                cmd = "ssoadm_ldapv3.sh -r %s -d %s -o %s %s" % (realm_name, domain_name, domain_ou, domain_host_ip)
            else:
                cmd = "ssoadm_ldapv3.sh -r %s -d %s %s" % (realm_name, domain_name, domain_host_ip)
        return self.cmd.call(cmd)

    def ssoadm_nis(self, realm_name, domain_name, domain_user, domain_password, domain_host_ip):
        cmd = "ssoadm_nis.sh -r %s -d %s %s" % (realm_name, domain_name, domain_host_ip)
        return self.cmd.call(cmd)

    def openam_backup(self):
        cmd = "openam_backup.sh"
        return self.cmd.call(cmd)

    def openam_useradd(self, number):
        cmd = "openam_useradd.sh -n %s" % number
        return self.cmd.call(cmd)

    def template_modify(self, ip, netname, user_name, password, domain_name):
        cmd = "template_modify.sh -i '%s' -n '%s' -u '%s' -p '%s' -d '%s'" % (ip, netname, user_name, password, domain_name)
        return self.cmd.call(cmd)

    def data_backup(self, filepath):
        cmd = "data_backup.sh '%s'" % filepath
        return self.cmd.call(cmd)

    def data_restore(self, filepath):
        cmd = "data_restore.sh '%s'" % filepath
        return self.cmd.call(cmd)

    def restart_service(self, service_name):
        cmd = "service '%s' restart" % service_name
        return self.cmd.call(cmd)

    def start_cont(self, cont_name):
        cmd = "start-cont.sh '%s'" % cont_name
        return self.cmd.call(cmd)

    def stop_cont(self, cont_name):
        cmd = "stop-cont.sh '%s'" % cont_name
        return self.cmd.call(cmd)

    def restart_sftp_cont(self):
        cmd = "restart_sftp_cont.sh"
        return self.cmd.call(cmd)

    def restart_openam_cont(self):
        cmd = "restart_openam_cont.sh"
        return self.cmd.call(cmd)

    def restart_elk_cont(self):
        cmd = "restart_elk_cont.sh"
        return self.cmd.call(cmd)

    def open_init(self):
        cmd = "open_init.sh"
        return self.cmd.call(cmd)

    def modify_date(self, date):
        cmd = 'date -s "%s"' % date
        return self.cmd.call(cmd)

    def sbox_approval_add_link(self, netname, user_name, ticket_id, path_list):
        param = '%s %s %s' %(netname, user_name, ticket_id)
        for path in path_list:
            quote_path = "'%s'" % path
            param = param + ' ' + quote_path
        cmd = "sbox_approval_add_link.sh %s" % param
        return self.cmd.call(cmd)

    def sbox_approval_del_link(self, netname, user_name, ticket_id):
        param = '%s %s %s' % (netname, user_name, ticket_id)
        cmd   = "sbox_approval_del_link.sh %s" % param
        return self.cmd.call(cmd)

    def sbox_cp_license(self, license_path):
        cmd = "/bin/cp -f '%s' '%s'" % (license_path, '/license/license.txt')
        return self.cmd.call(cmd)

    def sbox_verify(self):
        cmd = "sbox_verify.sh"
        return self.cmd.call(cmd)

    def rdpclient(self,server,domain,user,password,fullscreen,width,height,extra):
        param = ""
        if fullscreen == 1 :
            if ''==domain or None==domain :
                param = "-u %s -p %s %s -f %s" %(user,password,extra,server)
            else :
                param = "-d %s -u %s -p %s %s -f %s" %(domain,user,password,extra,server)
        else :
            if ''==domain or None==domain :
                param = "-u %s -p %s -w %d -h %d %s %s" %(user,password,width,height,extra,server)
            else :
                param = "-d %s -u %s -p %s -w %d -h %d %s %s" %(domain,user,password,width,height,extra,server)
        
        #logger.info("param:%s" %param)

        cmd   = "rdpclient.sh %s" %param
        return self.cmd.call(cmd)
        
    def sbox_whitelist(self, type, operate, ipnetwork):
        if   'add' == operate:
            cmd = "sbox_whitelist.sh -t '%s' -a '%s'" % (type, ipnetwork)
        elif 'del' == operate:
            cmd = "sbox_whitelist.sh -t '%s' -d '%s'" % (type, ipnetwork)
        return self.cmd.call(cmd)

