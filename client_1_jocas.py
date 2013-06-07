from pysnmp.entity import engine, config
from pysnmp import debug
from pysnmp.entity.rfc3413 import cmdrsp, context, ntforg
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.smi import builder

import threading
import collections
import time
import os

#can be useful
#debug.setLogger(debug.Debug('all'))

MibObject = collections.namedtuple('MibObject', ['mibName',
                                   'objectType', 'valueFunc'])

class Mib(object):
    """Stores the data we want to serve. 
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._test_count = 0

    def getTestDescription(self):
        return "My Description Dainius Jocas"

    def getTestCount(self):
        with self._lock:
            return self._test_count

    def setTestCount(self, value):
        with self._lock:
            self._test_count = value
            
            
    def getpiActivity(self):
        return "TODO: getpiActivity"
        
    def getpiProcesses(self):
        return str(os.popen("ps -A | awk '{print $4}'").read().strip().split('\n'))
        
    def getpiNetworkLoad(self):
        return "TODO: getpiNetworkLoad"
        
    def getpiStorageState(self):
        return os.popen("df -h | grep '\/dev\/' | awk '{print $4}'").read().strip()
    
    def getpiCPULoad(self):
	return os.popen("top -n 1 | grep Cpu | awk '{print $2+$4+$6+$10+$12+$14+$16}'").read().strip()
    
    def getpiCluster(self):
        return "TODO: getpiCluster"
    
    def getpiDNS(self):
        return os.popen("grep nameserver /etc/resolv.conf").read().strip().split('\n')[0].split(' ')[1]
    
    def getpiGateway(self):
        return os.popen("route -n | grep 'UG[ \t] | awk '{print $2}'").read().strip()
    
    def getpiNetmask(self):
        output = os.popen("ifconfig eth0 | grep 'inet addr'").read().strip()
        return output.split(' ')[5].split(':')[1]
    
    def getpiIP(self):
        output = os.popen("ifconfig eth0 | grep 'inet addr'").read().strip()
	return output.split(' ')[1].split(':')[1]
    
    def getpiHostname(self):
        return os.popen("hostname").read().strip()
    
    def getpiID(self):
        return os.popen("uname -n").read().strip()
    


def createVariable(SuperClass, getValue, *args):
    """This is going to create a instance variable that we can export. 
    getValue is a function to call to retreive the value of the scalar
    """
    class Var(SuperClass):
        def readGet(self, name, *args):
            return name, self.syntax.clone(getValue())
    return Var(*args)


class SNMPAgent(object):
    """Implements an Agent that serves the custom MIB and
    can send a trap.
    """

    def __init__(self, mibObjects):
        """
        mibObjects - a list of MibObject tuples that this agent
        will serve
        """

        #each SNMP-based application has an engine
        self._snmpEngine = engine.SnmpEngine()

        #open a UDP socket to listen for snmp requests
        config.addSocketTransport(self._snmpEngine, udp.domainName,
                                  udp.UdpTransport().openServerMode(('', 161)))

        #add a v2 user with the community string public
        config.addV1System(self._snmpEngine, "agent", "public")
        #let anyone accessing 'public' read anything in the subtree below,
        #which is the enterprises subtree that we defined our MIB to be in
        config.addVacmUser(self._snmpEngine, 2, "agent", "noAuthNoPriv",
                           readSubTree=(1,3,6,1,4,1))

        #each app has one or more contexts
        self._snmpContext = context.SnmpContext(self._snmpEngine)

        #the builder is used to load mibs. tell it to look in the
        #current directory for our new MIB. We'll also use it to
        #export our symbols later
        mibBuilder = self._snmpContext.getMibInstrum().getMibBuilder()
        mibSources = mibBuilder.getMibSources() + (builder.DirMibSource('.'),)
        mibBuilder.setMibSources(*mibSources)

        #our variables will subclass this since we only have scalar types
        #can't load this type directly, need to import it
        MibScalarInstance, = mibBuilder.importSymbols('SNMPv2-SMI',
                                                      'MibScalarInstance')
        #export our custom mib
        for mibObject in mibObjects:
            nextVar, = mibBuilder.importSymbols(mibObject.mibName,
                                                mibObject.objectType)
            instance = createVariable(MibScalarInstance,
                                      mibObject.valueFunc,
                                      nextVar.name, (0,),
                                      nextVar.syntax)
            #need to export as <var name>Instance
            instanceDict = {str(nextVar.name)+"Instance":instance}
            mibBuilder.exportSymbols(mibObject.mibName,
                                     **instanceDict)

        # tell pysnmp to respotd to get, getnext, and getbulk
        cmdrsp.GetCommandResponder(self._snmpEngine, self._snmpContext)
        cmdrsp.NextCommandResponder(self._snmpEngine, self._snmpContext)
        cmdrsp.BulkCommandResponder(self._snmpEngine, self._snmpContext)


    def setTrapReceiver(self, host, community):
        """Send traps to the host using community string community
        """
        config.addV1System(self._snmpEngine, 'nms-area', community)
        config.addVacmUser(self._snmpEngine, 2, 'nms-area', 'noAuthNoPriv',
                           notifySubTree=(1,3,6,1,4,1))
        config.addTargetParams(self._snmpEngine,
                               'nms-creds', 'nms-area', 'noAuthNoPriv', 1)
        config.addTargetAddr(self._snmpEngine, 'my-nms', udp.domainName,
                             (host, 162), 'nms-creds',
                             tagList='all-my-managers')
        #set last parameter to 'notification' to have it send
        #informs rather than unacknowledged traps
        config.addNotificationTarget(
            self._snmpEngine, 'test-notification', 'my-filter',
            'all-my-managers', 'trap')


    def sendTrap(self):
        print "Sending trap"
        ntfOrg = ntforg.NotificationOriginator(self._snmpContext)
        errorIndication = ntfOrg.sendNotification(
            self._snmpEngine,
            'test-notification',
            ('DJ-MIB', 'testTrap'),
            ())


    def serve_forever(self):
        print "Starting agent"
        self._snmpEngine.transportDispatcher.jobStarted(1)
        try:
           self._snmpEngine.transportDispatcher.runDispatcher()
        except:
            self._snmpEngine.transportDispatcher.closeDispatcher()
            raise

class Worker(threading.Thread):
    """Just to demonstrate updating the MIB
    and sending traps
    """

    def __init__(self, agent, mib):
        threading.Thread.__init__(self)
        self._agent = agent
        self._mib = mib
        self.setDaemon(True)

    def run(self):
        while True:
            time.sleep(3)
            mib.setTestCount(mib.getTestCount()+1)
            agent.sendTrap()

if __name__ == '__main__':
    mib = Mib()
    objects = [MibObject('DJ-MIB', 'testDescription', mib.getTestDescription),
               MibObject('DJ-MIB', 'testCount', mib.getTestCount),
               MibObject('DJ-MIB', 'piID', mib.getpiID),
               MibObject('DJ-MIB', 'piHostname', mib.getpiHostname),
               MibObject('DJ-MIB', 'piIP', mib.getpiIP),
               MibObject('DJ-MIB', 'piNetmask', mib.getpiNetmask),
               MibObject('DJ-MIB', 'piGateway', mib.getpiGateway),
               MibObject('DJ-MIB', 'piDNS', mib.getpiDNS),
               MibObject('DJ-MIB', 'piCluster', mib.getpiCluster),
               MibObject('DJ-MIB', 'piCPULoad', mib.getpiCPULoad),
               MibObject('DJ-MIB', 'piStorageState', mib.getpiStorageState),
               MibObject('DJ-MIB', 'piNetworkLoad', mib.getpiNetworkLoad),
               MibObject('DJ-MIB', 'piProcesses', mib.getpiProcesses),
               MibObject('DJ-MIB', 'piActivity', mib.getpiActivity)]
    agent = SNMPAgent(objects)
    agent.setTrapReceiver('192.168.56.101', 'traps')
    Worker(agent, mib).start()
    try:
        agent.serve_forever()
    except KeyboardInterrupt:
        print "Shutting down"


