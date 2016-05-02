"""
example script how to extract parameters from a Cisco IOS configuration using regular expressions
"""
import sys
import re
import json

if __name__ == "__main__":
    config_file_name = "example_config.txt"

    # the result dictionary
    result = {
        "features": [],
        "interfaces": {}
    }

    # read the example configuration
    try:
        file = open(config_file_name)
        sample_config = file.read()
        file.close()

    except Exception as ex:
        print("Cannot read configuration (%s), terminate script")
        sys.exit(1)

    # check if OSPF is used as the routing protocol
    # the following regex_pattern matches only the "router ospf <process-id>" command (no VRFs)
    ospf_regex_pattern = r"^router ospf \d+$"

    # we will use the re.search() function, because the re.match() function ignores the MULTILINE flag
    # if the command is not found, the return value is None
    is_ospf_in_use = True if re.search(ospf_regex_pattern, sample_config, re.MULTILINE) else False

    if is_ospf_in_use:
        print("==> OSPF is used in this configuration")
        result["features"].append("ospf")
    else:
        print("==> OSPF is not used in this configuration")

    # extract the interface name and description
    interface_descriptions = re.finditer(r"^(interface (?P<intf_name>\S+))\n"
                                         r"( .*\n)*"
                                         r"( description (?P<description>.*))\n",
                                         sample_config,
                                         re.MULTILINE)

    for intf_part in interface_descriptions:
        print("==> found interface '%s' with description '%s'" % (intf_part.group("intf_name"),
                                                                  intf_part.group("description")))
        result["interfaces"][intf_part.group("intf_name")] = {
            "description": intf_part.group("description") if intf_part.group("description") else "not set"
        }

    # extract the IPv4 address of the interfaces
    interface_ips = re.finditer(r"^(interface (?P<intf_name>.*)\n)"
                                r"( .*\n)*"
                                r"( ip address (?P<ipv4_address>\S+) (?P<subnet_mask>\S+))\n",
                                sample_config,
                                re.MULTILINE)

    for intf_ip in interface_ips:
        print("==> found interface '%s' with ip '%s/%s'" % (intf_ip.group("intf_name"),
                                                           intf_ip.group("ipv4_address"),
                                                           intf_ip.group("subnet_mask")))
        # create interface name if not already exist
        if intf_ip.group("intf_name") not in result["interfaces"].keys():
            result["interfaces"][intf_ip.group("intf_name")] = {}

        result["interfaces"][intf_ip.group("intf_name")].update({
            "ipv4": {
                "address": intf_ip.group("ipv4_address"),
                "netmask": intf_ip.group("subnet_mask")
            }
        })

    print("\nEXTRACTED PARAMETERS\n")
    print(json.dumps(result, indent=4))
