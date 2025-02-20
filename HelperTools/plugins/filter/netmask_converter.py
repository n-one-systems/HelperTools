#!/usr/bin/python

class FilterModule(object):
    def filters(self):
        return {
            'convert_netmask': self.convert_netmask
        }

    def convert_netmask(self, netmask, desired_format=None):
        """
        Convert netmask between dotted decimal and CIDR notation
        
        Args:
            netmask (str): Input netmask in either format (e.g. "255.255.255.0" or "/24" or "24")
            desired_format (str): Optional - specify 'dotted' or 'cidr' for single format output
            
        Returns:
            dict: Both formats or single format if specified
        """
        # Clean input
        netmask = str(netmask).strip()
        
        # Remove leading slash if present
        if netmask.startswith('/'):
            netmask = netmask[1:]
            
        # Convert to binary for processing
        if '.' in netmask:  # Input is dotted decimal
            binary = self._dotted_to_binary(netmask)
        else:  # Input is CIDR
            try:
                prefix_len = int(netmask)
                if not 0 <= prefix_len <= 32:
                    raise ValueError("CIDR prefix must be between 0 and 32")
                binary = '1' * prefix_len + '0' * (32 - prefix_len)
            except ValueError as e:
                raise ValueError(f"Invalid netmask format: {netmask}")
                
        # Generate both formats
        dotted = self._binary_to_dotted(binary)
        cidr = f"/{binary.count('1')}"
        
        # Return requested format or both
        if desired_format == 'dotted':
            return dotted
        elif desired_format == 'cidr':
            return cidr
        else:
            return {
                'dotted': dotted,
                'cidr': cidr
            }
            
    def _dotted_to_binary(self, dotted):
        """Convert dotted decimal to binary string"""
        try:
            # Split into octets and validate
            octets = [int(x) for x in dotted.split('.')]
            if len(octets) != 4:
                raise ValueError("Must have exactly 4 octets")
                
            # Convert to binary
            binary = ''
            for octet in octets:
                if not 0 <= octet <= 255:
                    raise ValueError("Each octet must be between 0 and 255")
                binary += format(octet, '08b')
                
            # Validate netmask format (must be continuous 1s followed by 0s)
            if '01' in binary:
                raise ValueError("Invalid netmask format - must be continuous 1s followed by 0s")
                
            return binary
            
        except Exception as e:
            raise ValueError(f"Invalid dotted decimal format: {dotted}")
            
    def _binary_to_dotted(self, binary):
        """Convert binary string to dotted decimal"""
        try:
            octets = []
            for i in range(0, 32, 8):
                octet = binary[i:i+8]
                octets.append(str(int(octet, 2)))
            return '.'.join(octets)
        except Exception as e:
            raise ValueError(f"Error converting binary to dotted decimal: {binary}")
