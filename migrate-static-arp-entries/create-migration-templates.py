import sys
import os
from ipaddress import IPv4Address, IPv4Network
from ciscoconfparse import CiscoConfParse
from ciscoconfparse.ccp_util import IPv4Obj

# existing configuration file and output dir
existing_configuration = "cisco_static_arp_configuration.txt"
output_dir = "_output"


def get_vlan_svi_records_from_existing_configuration(cisco_conf_parse_obj):
    """
    parse VLAN SVI interfaces with IP address
    :param cisco_conf_parse_obj: Instance of CiscoConfParse
    :return: list with dictionaries that contain the VLAN ID, IP address and subnet mask
    """
    # read all VLAN SVI's which has an ip address
    vlan_interfaces = cisco_conf_parse_obj.find_objects_w_child("^interface Vlan", r'^ ip address.*')
    vlan_svi_records = list()

    for vlan_interface in vlan_interfaces:
        vlan_svi_record = dict()

        # determine current ip address
        ipv4_addr = vlan_interface.re_match_iter_typed(r"ip\saddress\s(\S+\s+\S+)", result_type=IPv4Obj)

        # determine the current interface name and VLAN ID
        vlan_interface_string = vlan_interface.text.lstrip("interface ")
        vlan_id = vlan_interface_string.lstrip("Vlan")

        vlan_svi_record['ipv4_addr'] = str(ipv4_addr.ip)
        vlan_svi_record['ipv4_netmask'] = str(ipv4_addr.netmask)
        vlan_svi_record['vlan_id'] = vlan_id
        vlan_svi_records.append(vlan_svi_record)

    return vlan_svi_records


if __name__ == "__main__":
    # verify that output directory exists
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    print("Load confguration file...")
    try:
        parsed_config = CiscoConfParse(existing_configuration)

    except Exception as ex:
        print("FAILED")
        print(">>> loading of configuration failed, script execution terminated")
        print(ex)
        sys.exit()

    print("Load VLAN SVIs from configuration...")
    vlan_svis = get_vlan_svi_records_from_existing_configuration(parsed_config)

    print("Load static ARP entries from configuration...")
    # get the static ARP entries
    static_arp_entries = parsed_config.find_objects("^arp\s(\S+\s+\S+)")

    for static_arp_entry in static_arp_entries:
        arp_record = dict()

        # split the arp command and get the required infos
        # result looks like: ['arp', '10.0.100.115', '0100.5e7f.9271', 'ARPA']
        arr_obj = static_arp_entry.text.split()
        ipv4 = arr_obj[1]
        mac = arr_obj[2]

        # now we create an IP address object from the ARP entry
        arp_ipv4_addr = IPv4Address(ipv4)

        # assign static arp entry to the VLAN SVI interface
        for vlan_svi in vlan_svis:
            svi_ipv4_network = IPv4Network(vlan_svi['ipv4_addr'] + "/" + vlan_svi['ipv4_netmask'], strict=False)
            if arp_ipv4_addr in svi_ipv4_network.hosts():
                # extend the model if the correct IP network is found
                if "static_arps" not in vlan_svi.keys():
                    vlan_svi['static_arps'] = list()
                record = {
                    'ipv4_host': ipv4,
                    'mac': mac
                }
                vlan_svi['static_arps'].append(record)

                # a static ARP is only defined on a single interface
                break

    print("Write results to file...")
    cisco_nxos_template = CiscoConfParse(['!'])

    for vlan_svi in vlan_svis:
        cisco_nxos_template.append_line("interface Vlan%s" % vlan_svi['vlan_id'])
        for static_arp in vlan_svi['static_arps']:
            cisco_nxos_template.append_line(" ip arp %s %s" % (static_arp['ipv4_host'], static_arp['mac']))
        cisco_nxos_template.append_line('!')

    cisco_nxos_template.save_as(os.path.join(output_dir, "cisco_nxos_config.txt"))
