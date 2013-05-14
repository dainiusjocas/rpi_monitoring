#!/bin/bash

# the ID
uname -n | sed 's/^\s*/id:/'  
# the hostname
hostname | sed 's/^\s*/hostname:/'
# the network configuration (ip, netmask)
ifconfig eth0 | grep "inet addr" | sed 's/\s\+/\n/g' | grep 'addr\|Mask'
# the network configuration (gateway)
route -n | grep 'UG[ \t]' | awk '{print $2}' | sed 's/^\s*/gateway:/'
# the network configuration (dns)
grep nameserver /etc/resolv.conf | sed 's/\s/:/'
# to which cluster the rpi belongs to
# ??
# the system state (cpu load)
top -n 1 | grep Cpu | awk '{print "cpu:"$2+$4+$6+$10+$12+$14+$16}'
# storage state
df -h | grep '\/dev\/' | awk '{print $1":"$4}'
# network load
./net_speed.sh wlan0
# the processes’ list
ps -A | awk '{print $4}' | tr "\\n" ", " | sed 's/\s*/proceses:[/' | sed 's/,$/]\n/'
# what the rpi is doing (you'll have to provide your own definition for that)
# DANGER: to be decided
echo "idle"
