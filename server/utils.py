import ipaddress


class IpNetworks:
    """
    A Class that contains a list of IPvXNetwork objects.

    Credits to https://www.fomfus.com/articles/how-to-use-ip-ranges-for-django-s-internal_ips-setting/
    """

    networks = []

    def __init__(self, addresses):
        """Create a new IpNetwork object for each address provided."""
        for address in addresses:
            self.networks.append(ipaddress.ip_network(address))

    def __contains__(self, address):
        """Check if the given address is contained in any of our Networks."""
        for network in self.networks:
            if ipaddress.ip_address(address) in network:
                return True
        return False
