from PyQt5 import QtCore
import scapy.all as scapy
from scapy.layers import http

class Sniffer(QtCore.QThread):
    write_log_signal = QtCore.pyqtSignal(str)
    finished_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None, data=0):
        super(Sniffer, self).__init__(parent)
        self.data=data
        
    def sniff(self, interface):

        test = scapy.sniff(count=20, iface=interface, store=False, prn=self.sniff_filter)
            
    
    def sniff_filter(self, pkt):
        if pkt.haslayer(http.HTTPRequest):
            print('http pkt-----------------------------')
            #a = pkt.show(dump=True)
            #print(a)

            mac_src = pkt.src
            mac_dst = pkt.dst
            ip_src = pkt['IP'].src
            ip_dst = pkt['IP'].dst
            host=pkt.Host.decode() 
            path=pkt.Path.decode()
            method=pkt.Method.decode()
            version=pkt.Http_Version.decode()
      
            #auth=pkt.Authorization.decode()
            #print('auth: ' + auth )
            
            url = str(host + path)

            ##print('Method: ' + str(pkt[http.HTTPRequest].Method))
            ##print('Version: ' + str(pkt[http.HTTPRequest].Http_Version))
            ##print('Authorization: ' + str(pkt[http.HTTPRequest].Authorization))
            ##print('Origin: ' + str(pkt[http.HTTPRequest].Origin))
            ##print('Authorization: ' + str(pkt[http.HTTPRequest].Authorization))
      
            #keywords = ['pass', 'password', 'usr', 'username', 'user', 'pwd']
            #if pkt.haslayer(scapy.Raw): # username and password appears in raw field
                #for keyword in keywords: # check if each keyword exists
                    #if keyword in str(pkt[scapy.Raw]): # in the raw field
                        #print(unquote(str(pkt[scapy.Raw]))) # if exists, print out the content once.
                        #break
                
            ##print(packets.show())
            return mac_src, mac_dst, ip_src, ip_dst, host, path, method, version
        #TODO: write this live data via signal to gui thread in a nice minimal format

    def run(self):
        self.write_log_signal.emit('Starting thread')
        self.write_log_signal.emit('Sniffing')
        
        interface = self.data["t4_value_1"]
        
        self.write_log_signal.emit('Interface: ' + interface)
        
        result = self.sniff(interface)
        print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
        print(result)
        print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')

        self.finished_signal.emit()

    def stop(self):
        self.write_log_signal.emit('Stopping thread')
        self.finished_signal.emit()
        self.terminate()
