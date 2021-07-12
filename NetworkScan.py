from PyQt5 import QtCore
import nmap

class NetworkScan(QtCore.QThread):
    write_log_signal = QtCore.pyqtSignal(str)
    write_table_view_signal = QtCore.pyqtSignal(list)
    finished_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None, data=0):
        super(NetworkScan, self).__init__(parent)
        self.data=data

    def run(self):
        self.write_log_signal.emit('Starting thread')
        self.write_log_signal.emit('Scanning network')

        network = self.data["t2_value_1"]

        nmps= nmap.PortScanner()
        nmps.scan(hosts=network, arguments='-sn')

        headers_x=['ip', 'hostname', 'mac', 'state', 'reason']
        l1=[headers_x]

        for ip in nmps.all_hosts():
            hostname = mac = state = reason = ''
            if 'name' in  nmps[ip]['hostnames'][0]:
                hostname = nmps[ip]['hostnames'][0]['name']
            if 'mac' in  nmps[ip]['addresses']:
                mac = nmps[ip]['addresses']['mac']
            if 'state' in  nmps[ip]['status']:
                state = nmps[ip]['status']['state']
            if 'reason' in  nmps[ip]['status']:
                reason = nmps[ip]['status']['reason']

            l2=[ip, hostname, mac, state, reason]
            l1.append(l2)

        self.write_table_view_signal.emit(l1)
        self.finished_signal.emit()

    def stop(self):
        self.write_log_signal.emit('Stopping thread')
        self.finished_signal.emit()
        self.terminate()
