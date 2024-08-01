from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

# Network general options
net.setLogLevel('info')
net.enableArpTables()

# Network definition
net.addHost('h1')
net.addHost('h2')

net.addP4Switch('s1', cli_input='s1-commands.txt')
net.setP4Source('s1','./p4src/rule_cache.p4')
net.addP4Switch('s2', cli_input='s2-commands.txt')
net.setP4Source('s2','./p4src/rule_cache.p4')
net.addP4Switch('s3', cli_input='s3-commands.txt')
net.setP4Source('s3','./p4src/rule_cache.p4')
net.addP4Switch('s4', cli_input='s4-commands.txt')
net.setP4Source('s4','./p4src/rule_cache.p4')

net.addLink('h1', 's1')
net.addLink('h2', 's2')
net.addLink('s1', 's2')
net.addLink('s1', 's3')
net.addLink('s2', 's3')

net.addLink('s1', 's4')
net.addLink('s2', 's4')
net.addLink('s3', 's4')

# Assignment strategy
net.l2()

# Nodes general options
net.disablePcapDumpAll()
net.enableLogAll()
net.disableCpuPortAll()
net.enableCli()

# Start network
net.startNetwork()
