#!/usr/bin/env python

import ciscoios
import parseconf
import getpass
import os


def load_ios(host, ios_image):
    hostname = host['hostname']
    try:
        cisco = ciscoios.CiscoIOS(host)
    except ciscoios.NetMikoAuthenticationException:
        print('{0} - bad password'.format(hostname))
        return
    except ciscoios.NetMikoTimeoutException:
        print('{0} - timeout'.format(hostname))
        return
    except Exception as err:
        print('{0} - error: {1}'.format(hostname, err))
        return

    def free_check(flash='flash:'):
        if cisco.flash_free(flash) - os.path.getsize(ios_image) < cisco.flash_size(flash) / 20:
            print('need more free space on {0}!'.format(flash))
            return False
        return True

    if cisco.file_exist(file=ios_image):
        return

    if not free_check():
        return

    ret = cisco.load_file(file=ios_image, dst_file='flash:{0}'.format(ios_image))
    for switch in cisco.get_switches():
        if switch['role'] is "Member":
            sw_num = switch['switch']
            if free_check('flash{0}:'.format(sw_num)) and \
                    not cisco.file_exist(file=ios_image, flash='flash{}:'.format(sw_num)):
                ret += cisco.f2f_copy(src='flash:{0}'.format(ios_image),
                                      dst='flash{0}:{1}'.format(sw_num, ios_image))
    return ret


conf = parseconf.ParseConf()
conf.set_pass(getpass.getpass())
load_ios(conf.get_host_by_name('acc-sw-5.2'), ios_image='c2960s-universalk9-mz.150-2.SE11.bin')
