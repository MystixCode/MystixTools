from PyQt5 import QtCore
import nmap

class PortScan(QtCore.QThread):
    write_log_signal = QtCore.pyqtSignal(str)
    write_table_view_signal = QtCore.pyqtSignal(list)
    write_port_scanner_result_signal = QtCore.pyqtSignal(dict)
    finished_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None, data=0):
        super(PortScan, self).__init__(parent)
        self.data=data

    def run(self):
        self.write_log_signal.emit('Starting thread')
        self.write_log_signal.emit('Scanning ports')

        ip_addr = self.data["t3_value_1"]
        range1 = self.data["t3_value_2"]
        range2 = self.data["t3_value_3"]
        method = self.data["t3_value_4"]

        range = str(range1) + '-' + str(range2)
        nmps = nmap.PortScanner()
        args = ''
        if method==0: #syn scan
            args = '-v -sS'
        if method==1:
            args = '-v -sS -sV -sC -A -O'
        nmps.scan(ip_addr, range, args, sudo=True)

        if ip_addr in nmps.all_hosts():
            if 'tcp' in nmps[ip_addr]:
                state = name = mac = version = lastboot = os = ''
                hostname = nmps[ip_addr].hostname()
                if 'mac' in nmps[ip_addr]['addresses']:
                    mac = nmps[ip_addr]['addresses']['mac']
                if 'osmatch' in nmps[ip_addr]:
                    if 'name' in nmps[ip_addr]['osmatch'][0]:
                        os = nmps[ip_addr]['osmatch'][0]['name']
                if 'uptime' in nmps[ip_addr]:
                    if 'lastboot' in nmps[ip_addr]['uptime']:
                        lastboot = nmps[ip_addr]['uptime']['lastboot']
                        
                lst = {"ip address": ip_addr, "hostname": hostname, "mac address": mac, "os": os, "last boot": lastboot}

                self.write_port_scanner_result_signal.emit(lst)

                headers_x=['port', 'state', 'service', 'version']
                lst1=[headers_x]

                i = 0
                for port in nmps[ip_addr]['tcp'].keys():
                    i += 1
                    if 'state' in nmps[ip_addr]['tcp'][port]:
                        state = nmps[ip_addr]['tcp'][port]['state']
                    if 'name' in nmps[ip_addr]['tcp'][port]:
                        service = nmps[ip_addr]['tcp'][port]['name']
                    if 'version' in nmps[ip_addr]['tcp'][port]:
                        version = nmps[ip_addr]['tcp'][port]['version']
                    lst2=[port, state, service, version]
                    lst1.append(lst2)

                self.write_table_view_signal.emit(lst1)
        self.finished_signal.emit()

    def stop(self):
        self.write_log_signal.emit('Stopping thread')
        self.finished_signal.emit()
        self.terminate()
