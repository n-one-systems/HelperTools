
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import ipaddress
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError


DOCUMENTATION = """
lookup: nsys.HelperTools:sn_math
author: AI Working Group
version_added: "2.0"
short_description: Calculate new IP addresses from a CIDR and summands.
description:
  - This lookup plugin calculates a set of IP addresses by taking an input IP address in CIDR notation and a list of summands.
  - It splits the input into a base IP and a prefix, calculates the network step (for IPv4, computed as 2^(32 - prefix)),
    and for each summand multiplies the summand by the step and adds it to the base IP.
  - The result is then returned as a list of CIDR-formatted IP addresses (using the original prefix).
options:
  _terms:
    description:
      - A list of terms.
      - The first term must be a CIDR string (e.g., "192.168.100.253/24").
      - The second term must be a list of summands (e.g., [1, 10, 12, -10]).
    required: True
notes:
  - This plugin currently supports only IPv4 addresses.
requirements: []
"""

EXAMPLES = """
- name: Calculate new IP addresses
  debug:
    msg: "{{ lookup('nsys.HelperTools.sn_math', '192.168.100.253/24', [1, 10, 12, -10]) }}"
"""

RETURN = """
_raw:
    description: The list of calculated IP addresses in CIDR notation.
    returned: always
    type: list
    sample: [
      "192.168.101.253/24",
      "192.168.110.253/24",
      "192.168.112.253/24",
      "192.168.90.253/24"
    ]
"""

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        # Expect two arguments: 
        #   1. input_ip_cidr: a string like "192.168.100.253/24"
        #   2. summands: a list of integers (or strings convertible to int)
        if len(terms) < 2:
            raise AnsibleError("Usage: lookup('sn_math', input_ip_cidr, summands)")

        input_ip_cidr = terms[0]
        summands = terms[1]

        try:
            # Use ip_interface to parse both the IP and prefix
            interface = ipaddress.ip_interface(input_ip_cidr)
        except Exception as e:
            raise AnsibleError("Invalid CIDR '%s': %s" % (input_ip_cidr, e))

        base_ip = interface.ip            # e.g. IPv4Address('192.168.100.253')
        prefix = interface.network.prefixlen  # e.g. 24 (as an int)
        # For IPv4, number of addresses per network = 2^(32 - prefix)
        step = 2 ** (32 - prefix)

        results = []
        for summand in summands:
            try:
                offset = int(summand) * step
            except Exception as e:
                raise AnsibleError("Invalid summand '%s': %s" % (summand, e))
            new_ip_int = int(base_ip) + offset
            try:
                new_ip = ipaddress.IPv4Address(new_ip_int)
            except Exception as e:
                raise AnsibleError("Resulting IP (%s) out of bounds: %s" % (new_ip_int, e))
            # Format as CIDR string using the original prefix
            results.append("{}/{}".format(new_ip, prefix))
        return results

