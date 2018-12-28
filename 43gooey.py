from gooey import Gooey, GooeyParser
import ipaddress
import sys

# Option 43 reference information
'''
https://www.cisco.com/c/en/us/support/docs/wireless-mobility/wireless-lan-wlan/97066-dhcp-option-43-00.html  # noqa
Note: TLV values for the Option 43 suboption: Type + Length + Value. 
Type is always the suboption code 0xf1. Length is the number of controller management IP addresses times 4 in hex.
Value is the IP address of the controller listed sequentially in hex. 
For example, suppose there are two controllers with management interface IP addresses, 192.168.10.5 and 192.168.10.20. 
The type is 0xf1. The length is 2 * 4 = 8 = 0x08. 
The IP addresses translates to c0a80a05 (192.168.10.5) and c0a80a14 (192.168.10.20). 
When the string is assembled, it yields f108c0a80a05c0a80a14. 
The Cisco IOS command that is added to the DHCP scope is option 43 hex f108c0a80a05c0a80a14.
'''


def o43_generator(ip_list):
    wlc_count = len(ip_list)
    # Use list comprehension to convert list of ips in to list of hex values
    # For every ip in the list, break out each octet, convert to hex, and re-join  # noqa
    hex_list = [''.join(['{:02x}'.format(int(i)) for i in ip.split('.')]) for ip in ip_list]  # noqa
    # Type is static
    t = 'f1'
    # Length is calculated as the number of controllers times 4
    l = '{:02x}'.format(wlc_count * 4)  # noqa
    # Converting list to concatenated string
    v = ''.join(hex_list)
    return(t + l + v)


def sanitize(ip_data):
    ip_list = []
    # Split out addresses by comma and strip white space
    for ip in ip_data.split(','):
        ip_list.append(ip.strip(' '))
    # Check some basic validity of the IP address formatting
    # Note: this doesn't check to see if the IP is routeable etc.
    for address in ip_list:
        try:
            ipaddress.ip_address(address)
        except ValueError:
            print('{} does not seem to be a valid IP.'.format(address))
            # raise
            sys.exit(1)
    return(ip_list)


@Gooey()
def main():
    desc = "Option 43 Generator for Cisco WLC"
    g_parser = GooeyParser(description=desc)
    # Create text box for data collection
    g_parser.add_argument('Controllers', help='Enter IPs (comma seperated)') # noqa
    # Gather all args
    args = g_parser.parse_args()
    # Sanitize data and create a list
    ip_list = sanitize(args.Controllers)
    # Create string out of ip list that looks nicer when printed
    pretty_ips = '\n'.join('{}'.format(i) for i in ip_list)
    # Print some output for the user for sanity check
    print('I found {} controller(s).\n\nCreating option 43 hex for:\n{}\n'.format(len(ip_list), pretty_ips))  # noqa
    # Generate option 43 hex value
    o43hex = o43_generator(ip_list)
    # Print final information
    print('Option 43 string: {}'.format(o43hex))


if __name__ == '__main__':
    main()
