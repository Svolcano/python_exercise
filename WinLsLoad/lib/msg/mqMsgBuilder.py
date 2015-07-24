
class MsgBuilder():

    def __init__(self):
        pass

    def build_request_add_user(self, user, password, id):
        msg = {}
        msg['request']  = 'add_user'
        msg['user']     = user
        msg['passwd']   = password
        msg['id']       = id
        return msg

    def build_request_del_user(self, user, id):
        msg = {}
        msg['request']  = 'del_user'
        msg['user']     = user
        msg['id']       = id
        return msg

    def build_request_change_passwd(self, user, passwd, id):
        msg = {}
        msg['request']  = 'change_passwd'
        msg['user']     = user
        msg['passwd']   = passwd
        msg['id']       = id
        return msg

    def build_request_user_zone_security_change(self, user_id, zone_id, security_item, id):
        msg = {}
        msg['request']       = 'user_zone_security_change'
        msg['user_id']       = user_id
        msg['zone_id']       = zone_id
        msg['security_item'] = security_item
        msg['id']            = id
        return msg

    def build_request_user_zone_audit_change(self, user_id, zone_id, audit_item, id):
        msg = {}
        msg['request']       = 'user_zone_audit_change'
        msg['user_id']       = user_id
        msg['zone_id']       = zone_id
        msg['audit_item']    = audit_item
        msg['id']            = id
        return msg

    def build_request_stop_container(self, user, zone, id):
        msg = {}
        msg['request']       = 'stop_container'
        msg['user']          = user
        msg['zone']          = zone
        msg['id']            = id
        return msg

    def build_request_zone_disable(self, zone_id, id):
        msg = {}
        msg['request']       = 'zone_disable'
        msg['zone_id']       = zone_id
        msg['id']            = id
        return msg

    def build_request_user_disable(self, user_id, id):
        msg = {}
        msg['request']       = 'user_disable'
        msg['user_id']       = user_id
        msg['id']            = id
        return msg

    def build_request_user_zone_stop_login(self, user_id, zone_id, id):
        msg = {}
        msg['request']       = 'user_zone_stop_login'
        msg['user_id']       = user_id
        msg['zone_id']       = zone_id
        msg['id']            = id
        return msg

    def build_request_network_change(self, network_id, id):
        msg = {}
        msg['request']       = 'network_change'
        msg['network_id']    = network_id
        msg['id']            = id
        return msg

    def build_request_time_zone_change(self, time_zone, id):
        msg = {}
        msg['request']      = 'time_zone_change'
        msg['time_zone']    = time_zone
        msg['id']           = id
        return msg

    def build_request_time_server_change(self, time_server, id):
        msg = {}
        msg['request']      = 'time_server_change'
        msg['time_server']  = time_server
        msg['id']           = id
        return msg

    def build_request_hostname_change(self, hostname, id):
        msg = {}
        msg['request']      = 'hostname_change'
        msg['hostname']     = hostname
        msg['id']           = id
        return msg

    def build_request_system_recover(self, update_id, id):
        msg = {}
        msg['request']      = 'system_recover'
        msg['update_id']    = update_id
        msg['id']           = id
        return msg

    def build_request_system_upgrade(self, update_id, upgrade_file_name, id):
        msg = {}
        msg['request']           = 'system_upgrade'
        msg['update_id']         = update_id
        msg['upgrade_file_name'] = upgrade_file_name
        msg['id']                = id
        return msg

    def build_request_zone_name_change(self, zone_id, old_zone_name, id):
        msg = {}
        msg['request']           = 'zone_name_change'
        msg['zone_id']           = zone_id
        msg['old_zone_name']     = old_zone_name
        msg['id']                = id
        return msg

    def build_request_shutdown(self, id):
        msg = {}
        msg['request']           = 'shutdown'
        msg['id']                = id
        return msg

    def build_request_reboot(self, id):
        msg = {}
        msg['request']           = 'reboot'
        msg['id']                = id
        return msg

    def build_request_cpu_usage(self, id):
        msg = {}
        msg['request']           = 'cpu_usage'
        msg['id']                = id
        return msg

    def build_request_memory_usage(self, id):
        msg = {}
        msg['request']           = 'memory_usage'
        msg['id']                = id
        return msg

    def build_request_date_time_zone(self, id):
        msg = {}
        msg['request']           = 'date_time_zone'
        msg['id']                = id
        return msg

    def build_request_interface_info(self, interface, id):
        msg = {}
        msg['request']           = 'interface_info'
        msg['interface']         = interface
        msg['id']                = id
        return msg

    def build_request_reboot_webserver(self, id):
        msg = {}
        msg['request']           = 'reboot_webserver'
        msg['id']                = id
        return msg

    def build_request_reboot_mysqlserver(self, id):
        msg = {}
        msg['request']           = 'reboot_mysqlserver'
        msg['id']                = id
        return msg

    def build_request_add_ad(self, domain_id, id):
        msg = {}
        msg['request']           = 'add_ad'
        msg['domain_id']         = domain_id
        msg['id']                = id
        return msg

    def build_request_del_ad(self, realm_name, id):
        msg = {}
        msg['request']           = 'del_ad'
        msg['realm_name']        = realm_name
        msg['id']                = id
        return msg

    def build_request_sync_ad_to_db(self, id):
        msg = {}
        msg['request']           = 'sync_ad_to_db'
        msg['id']                = id
        return msg

    def build_request_backup_ad(self, id):
        msg = {}
        msg['request']           = 'backup_ad'
        msg['id']                = id
        return msg

    def build_request_openam_useradd(self, number, id):
        msg = {}
        msg['request']           = 'openam_useradd'
        msg['number']            = number
        msg['id']                = id
        return msg

    def build_request_data_backup(self, path, id):
        msg = {}
        msg['request']           = 'data_backup'
        msg['path']              = path
        msg['id']                = id
        return msg

    def build_request_data_restore(self, path, id):
        msg = {}
        msg['request']           = 'data_restore'
        msg['path']              = path
        msg['id']                = id
        return msg

    def build_request_restart_service(self, name, id):
        msg = {}
        msg['request']           = 'restart_service'
        msg['name']              = name
        msg['id']                = id
        return msg

    def build_request_restart_container(self, name, id):
        msg = {}
        msg['request']           = 'restart_container'
        msg['name']              = name
        msg['id']                = id
        return msg

    def build_request_open_init(self, number, id):
        msg = {}
        msg['request']           = 'open_init'
        msg['number']            = number
        msg['id']                = id
        return msg

    def build_request_restart_system(self, name, id):
        msg = {}
        msg['request']           = 'restart_system'
        msg['name']              = name
        msg['id']                = id
        return msg

    def build_request_vsftp_passwd(self, new_passwd, id):
        msg = {}
        msg['request']           = 'vsftp_passwd'
        msg['new_passwd']        = new_passwd
        msg['id']                = id
        return msg

    def build_request_man_modify_date(self, date, id):
        msg = {}
        msg['request']           = 'man_modify_date'
        msg['date']              = date
        msg['id']                = id
        return msg

    def build_request_upload_license(self, path, id):
        msg = {}
        msg['request']           = 'upload_license'
        msg['path']              = path
        msg['id']                = id
        return msg

    def build_request_manage_license(self, type, id):
        msg = {}
        msg['request']           = 'manage_license'
        msg['type']              = type
        msg['id']                = id
        return msg

    def build_request_smtp_server_verify(self, server, user, password, sender, id):
        msg = {}
        msg['request']           = 'smtp_server_verify'
        msg['server']            = server
        msg['user']              = user
        msg['password']          = password
        msg['sender']            = sender
        msg['id']                = id
        return msg

    def build_request_send_mail(self, server, user, password, sender, receiver, title, message, id):
        msg = {}
        msg['request']           = 'send_mail'
        msg['server']            = server
        msg['user']              = user
        msg['password']          = password
        msg['sender']            = sender
        msg['receiver']          = receiver
        msg['title']             = title
        msg['message']           = message
        msg['id']                = id
        return msg

    def build_request_set_fire_wall(self, type, operate, ipnetwork, id):
        msg = {}
        msg['request']           = 'set_fire_wall'
        msg['type']              = type
        msg['operate']           = operate
        msg['ipnetwork']         = ipnetwork
        msg['id']                = id
        return msg

    def build_response(self, response_name, return_value, id):
        msg = {}
        msg['response']          = response_name
        msg['return']            = return_value
        msg['id']                = id
        return msg

    def build_response_cpu_usage(self, response_name, return_value, cpu_usage, id):
        msg = {}
        msg['response']          = response_name
        msg['return']            = return_value
        msg['cpu_usage']         = cpu_usage
        msg['id']                = id
        return msg

    def build_response_memory_usage(self, response_name, return_value, memory_usage, id):
        msg = {}
        msg['response']          = response_name
        msg['return']            = return_value
        msg['memory_usage']      = memory_usage
        msg['id']                = id
        return msg

    def build_response_date_time_zone(self, response_name, return_value, date, time_zone,  id):
        msg = {}
        msg['response']          = response_name
        msg['return']            = return_value
        msg['date']              = date
        msg['time_zone']         = time_zone
        msg['id']                = id
        return msg

    def build_response_interface_info(self, response_name, return_value, interface, link, duplex, speed, mac, ip, mask, gateway, id):
        msg = {}
        msg['response']          = response_name
        msg['return']            = return_value
        msg['interface']         = interface
        msg['link']              = link
        msg['duplex']            = duplex
        msg['speed']             = speed
        msg['mac']               = mac
        msg['ip']                = ip
        msg['mask']              = mask
        msg['gateway']           = gateway
        msg['id']                = id
        return msg

    def build_response_disable_processing(self, response_name, remain_container, remain_time,  id):
        msg = {}
        msg['response']          = response_name
        msg['return']            = 'processing'
        msg['remain_container']  = remain_container
        msg['remain_time']       = remain_time
        msg['id']                = id
        return msg

if __name__ == '__main__':
    bder = MsgBuilder()
    # 1

