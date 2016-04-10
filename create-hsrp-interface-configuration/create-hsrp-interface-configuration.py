import os
import sys
from ipaddress import IPv4Network, IPv4Interface, IPv4Address
from ciscoconfparse import CiscoConfParse
from ciscoconfparse.ccp_util import IPv4Obj


output_directory = "_output"
input_configuration_file = "cisco_ios_vlans.txt"
primary_configuration_file = "primary_config.txt"
secondary_configuration_file = "secondary_config.txt"


if __name__ == "__main__":
    # just make sure that the output directory exists
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    # load the input Cisco IOS configuration file
    print("load Cisco IOS configuration file...")
    try:
        parsed_config = CiscoConfParse(input_configuration_file)

    except Exception as ex:
        print(ex)
        sys.exit()

    # create objects for diff
    print("create primary and secondary configuration object...")
    primary_config = CiscoConfParse([
        "!",
        "! primary switch interface configuration",
        "!",
    ])
    secondary_config = CiscoConfParse([
        "!",
        "! secondary switch interface configuration",
        "!",
    ])

    # read all VLAN SVI's which has an ip address
    vlan_interfaces = parsed_config.find_objects_w_child("^interface Vlan", r"^ ip address.*")

    for vlan_interface in vlan_interfaces:
        # determine current ip address
        ipv4_addr = vlan_interface.re_match_iter_typed(r"ip\saddress\s(\S+\s+\S+)", result_type=IPv4Obj)

        # determine the current interface name and VLAN ID
        vlan_interface_string = vlan_interface.text.lstrip("interface ")
        vlan_id = vlan_interface_string.lstrip("Vlan")

        # the current SVI address is used as a HSRP virtual IP
        virtual_ip = ipv4_addr.ip_object

        # at this point we need to determine the next addresses which are used for the primary and secondary switch
        # we will try, if the next two addresses are part of the network, otherwise we will use the previous two
        # addresses
        ipv4_network = IPv4Network(ipv4_addr.network)
        if (ipv4_addr.ip_object + 1) in ipv4_network.hosts():
            primary_ip = ipv4_addr.ip_object + 1
            secondary_ip = ipv4_addr.ip_object + 2
        else:
            primary_ip = ipv4_addr.ip_object - 1
            secondary_ip = ipv4_addr.ip_object - 2

        # check for secondary IPv4 addresses
        add_ip_addresses = []
        secondary_ipv4_address_lines = vlan_interface.re_search_children(r"^ ip address .* secondary$")
        for sec_ipv4_cmd in secondary_ipv4_address_lines:
            # another way to convert the ip address command
            sec_ipv4_addr = sec_ipv4_cmd.text[len(" ip address "):]
            sec_ipv4_addr = sec_ipv4_addr.rstrip(" secondary")
            sec_ipv4_addr = sec_ipv4_addr.replace(" ", "/")

            # convert it to an IPv4Interface object from the ipaddresss module
            ip_address = IPv4Interface(sec_ipv4_addr)

            # store it for later processing
            add_ip_addresses.append(ip_address)

        # now add the configuration to the change scripts
        primary_config.append_line("interface %s" % vlan_interface_string)
        primary_config.append_line(" description *** VLAN SVI %s" % vlan_id)
        primary_config.append_line(" ip address %s %s" % (primary_ip, ipv4_addr.netmask))
        for ipv4_address in add_ip_addresses:
            # determine primary IP address
            if IPv4Address(ipv4_address.ip + 1) in ipv4_address.network.hosts():
                primary_ip = ipv4_address + 1
            else:
                primary_ip = ipv4_address - 1
            primary_config.append_line(" ip address %s %s secondary" % (primary_ip.ip, ipv4_address.netmask))

        primary_config.append_line(" standby version 2")
        primary_config.append_line(" standby 1 ip %s" % virtual_ip)
        for ipv4_address in add_ip_addresses:
            primary_config.append_line(" standby 1 ip %s secondary" % ipv4_address.ip)

        primary_config.append_line(" standby 1 priority 255")
        primary_config.append_line(" standby 1 authentication md5 key-string vl%s" % vlan_id)
        primary_config.append_line("!")

        secondary_config.append_line("interface %s" % vlan_interface_string)
        secondary_config.append_line(" description *** VLAN SVI %s" % vlan_id)
        secondary_config.append_line(" ip address %s %s" % (secondary_ip, ipv4_addr.netmask))
        for ipv4_address in add_ip_addresses:
            # determine secondary IP address
            if IPv4Address(ipv4_address.ip + 2) in ipv4_address.network.hosts():
                secondary_ip = ipv4_address + 2
            else:
                secondary_ip = ipv4_address - 2
            secondary_config.append_line(" ip address %s %s secondary" % (secondary_ip.ip, ipv4_address.netmask))

        secondary_config.append_line(" standby version 2")
        secondary_config.append_line(" standby 1 ip %s" % virtual_ip)
        for ipv4_address in add_ip_addresses:
            secondary_config.append_line(" standby 1 ip %s secondary" % ipv4_address.ip)

        secondary_config.append_line(" standby 1 priority 254")
        secondary_config.append_line(" standby 1 authentication md5 key-string vl%s" % vlan_id)
        secondary_config.append_line("!")

    # write results
    print("Write results...")
    primary_config.save_as(os.path.join(output_directory, primary_configuration_file))
    secondary_config.save_as(os.path.join(output_directory, secondary_configuration_file))
