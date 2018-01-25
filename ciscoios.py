#!/usr/bin/env python

from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException, SCPConn
import re


class CiscoIOS:

    def __init__(self, device_param):
        if 'hostname' in device_param:
            del(device_param['hostname'])
        self.device_param = device_param
        try:
            self.ssh = ConnectHandler(**device_param)
        except NetMikoAuthenticationException:
            raise NetMikoAuthenticationException
        except NetMikoTimeoutException:
            raise NetMikoTimeoutException

        if not self.ssh.check_enable_mode() and self.device_param['secret']:
            self.ssh.enable()

    def enable_scp(self):
        return self.ssh.send_config_set(['ip scp server enable'])

    def disable_scp(self):
        return self.ssh.send_config_set(['ip scp server enable'])

    def load_file(self, file, dst_file=None):
        if not dst_file:
            dst_file = file
        scp_status = self.ssh.send_command('show running-config | i "ip scp server enable"')
        if not scp_status:
            self.enable_scp()
        scp = SCPConn(self.ssh)
        scp.scp_transfer_file(file, dst_file)
        scp.close()
        if not scp_status:
            self.disable_scp()

    '''
    #show switch
    Switch/Stack Mac Address : e089.9d50.7000
                                               H/W   Current
    Switch#  Role   Mac Address     Priority Version  State 
    ----------------------------------------------------------
    *1       Master e089.9d50.7000     15     1       Ready               
     2       Member 1ce8.5d68.7b00     14     1       Ready               
     3       Member 1ce8.5d68.3980     13     1       Ready               
     4       Member 1ce8.5d8a.cc80     12     1       Ready               
    '''
    def get_switches(self):
        p = re.compile(r"""              
                        (\s|\*)
                        (?P<switch>\d)
                        \s+                          
                        (?P<role>Member|Master)    
                        \s+                       
                        (?P<mac>[a-z0-9]{4}\.[a-z0-9]{4}\.[a-z0-9]{4})                
                        \s+                           
                        (?P<prior>\d{1,2})
                        \s+
                        (?P<version>\d+)
                        \s+
                        (?P<state>Ready|.*?)
                        \s+
                        """, re.VERBOSE)
        ret = self.ssh.send_command('show switch', delay_factor=5)
        for line in ret.splitlines()[3:]:
            switch = {}
            if p.search(line):
                switch['switch'] = p.search(line).group('switch')
                switch['role'] = p.search(line).group('role')
                switch['mac'] = p.search(line).group('mac')
                switch['prior'] = p.search(line).group('prior')
                switch['version'] = p.search(line).group('version')
                switch['state'] = p.search(line).group('state')
                yield switch

    '''
    Flash to flash copy function. Don't use '/' in src, dst path after colon symbol:
    #copy flash:c2960s-universalk9-mz.150-2.SE11.bin flash2:c2960s-universalk9-mz.150-2.SE11.bin
    Destination filename [c2960s-universalk9-mz.150-2.SE11.bin]? 
    Copy in progress...CCCCCCCC
    '''
    def f2f_copy(self, src, dst):
        ret = self.ssh.send_command_timing('copy {0} {1}'.format(src, dst))
        if 'Destination filename [{0}]?'.format(dst[dst.find(':')+1:]) in ret:
            ret += self.ssh.send_command_timing('')
        return ret

    '''
    #show flash3: | i bytes total
    122185728 bytes total (30591488 bytes free)
    '''
    def flash_size(self, flash='flash:'):
        ret = self.ssh.send_command('show {0} | i bytes total'.format(flash))
        return int(ret[:ret.find(' ')])

    def flash_free(self, flash='flash:'):
        ret = self.ssh.send_command('show {0} | i bytes total'.format(flash))
        return int(ret[ret.find('(')+1:ret.rfind(' bytes free')])

    def file_exist(self, file, flash='flash:'):
        if self.ssh.send_command('show {0} | i {1}'.format(flash, file)):
            return True
        return False

    def set_image(self, image):
        return self.ssh.send_config_set(['boot system switch all flash:/{0}'.format(image)])

    def reload(self, save=False):
        if save:
            self.write()
        ret = self.ssh.send_command_timing('reload')
        if 'Proceed with reload? [confirm]' in ret:
            ret += self.ssh.send_command_timing('')
        return ret

    def write(self):
        return self.ssh.send_command('write memory')
