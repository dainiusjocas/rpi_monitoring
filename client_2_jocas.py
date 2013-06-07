# Author: Dainius Jocas

# Every 60 seconds queries snmp agent, which knows about DJ-MIB, and sends
#  raw data to the server which is at 192.168.56.102 to port 34567  
# script expects to receive hostname, port number, and timeout through 
#  command line parameters 

import time
import sys
import os
from socket import *

def get_data():
	result = os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piID").read().strip()
	result = result + "\n" + os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piHostname").read().strip()
	result = result + "\n" + os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piIP").read().strip()
	result = result + "\n" + os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piNetmask").read().strip()
	result = result + "\n" + os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piGateway").read().strip()
	result = result + "\n" + os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piDNS").read().strip()
	result = result + "\n" + os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piCluster").read().strip()
	result = result + "\n" + os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piCPULoad").read().strip()
	result = result + "\n" + os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piStorageState").read().strip()
	result = result + "\n" + os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piNetworkLoad").read().strip()
	result = result + "\n" + os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piProcesses").read().strip()
	result = result + "\n" + os.popen("snmpwalk -m DJ-MIB -v 2c -c public localhost piActivity").read().strip()
	return result

# Hostname and port number of the server.
hostname = sys.argv[1]
port_number = int(sys.argv[2])
# Create UDP client socket
clientSocket = socket(AF_INET, SOCK_DGRAM)
while (True):
	# get info about the device
	message = get_data()
	# send to the server
	# Send the UDP packet with the ping message
	clientSocket.sendto(message, (hostname, port_number))
	# timeout in seconds
	time.sleep(sys.argv[3])

# Close the client socket
clientSocket.close()