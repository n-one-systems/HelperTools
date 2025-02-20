import ipaddress

def smallest_network(ips):
    """
    Given a list of IP addresses (as strings), determine the smallest network 
    that contains all of them.
    """
    # Convert string IP addresses to IPv4Address objects
    ips = [ipaddress.IPv4Address(ip) for ip in ips]
    
    # Find the lowest and highest IP addresses
    ip_min = min(ips)
    ip_max = max(ips)
    
    # Determine the common prefix length by XOR-ing the integer representations
    diff = int(ip_min) ^ int(ip_max)
    prefix = 32
    while diff:
        diff >>= 1
        prefix -= 1

    # Create the network using the lower IP and calculated prefix length.
    network = ipaddress.IPv4Network((int(ip_min), prefix), strict=False)
    return str(network)

class FilterModule(object):
    def filters(self):
        return {
            'smallest_network': smallest_network
        }

