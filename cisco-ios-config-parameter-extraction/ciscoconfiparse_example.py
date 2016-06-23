"""
example script how to extract parameters from a Cisco IOS configuration using ciscoconfparse
"""
import json
from ciscoconfparse import CiscoConfParse
from ciscoconfparse.ccp_util import IPv4Obj

if __name__ == "__main__":
    # the result dictionary
    result = {
        "features": [],
        "interfaces": {}
    }

    # create CiscoConfParse object using a configuration file stored in the
    # same directory as the script
    confparse = CiscoConfParse("example_config.txt")

    # check if OSPF is used as the routing protocol
    # the following regex_pattern matches only the "router ospf <process-id>" command (no VRFs)
    ospf_regex_pattern = r"^router ospf \d+$"

    # in this case, we will simply check that the ospf router command is part of the config
    is_ospf_in_use = confparse.has_line_with(ospf_regex_pattern)

    if is_ospf_in_use:
        print("==> OSPF is used in this configuration")
        result["features"].append("ospf")
    else:
        print("==> OSPF is not used in this configuration")

    # extract the interface name and description
    # first, we get all interface commands from the configuration
    interface_cmds = confparse.find_objects(r"^interface ")

    # iterate over the resulting IOSCfgLine objects
    for interface_cmd in interface_cmds:
        # get the interface name (remove the interface command from the configuration line)
        intf_name = interface_cmd.text[len("interface "):]
        result["interfaces"][intf_name] = {}

        # search for the description command, if not set use "not set" as value
        result["interfaces"][intf_name]["description"] = "not set"
        for cmd in interface_cmd.re_search_children(r"^ description "):
            result["interfaces"][intf_name]["description"] = cmd.text.strip()[len("description "):]

        # extract IP addresses if defined
        IPv4_REGEX = r"ip\saddress\s(\S+\s+\S+)"
        for cmd in interface_cmd.re_search_children(IPv4_REGEX):
            # ciscoconfparse provides a helper function for this task
            ipv4_addr = interface_cmd.re_match_iter_typed(IPv4_REGEX, result_type=IPv4Obj)

            result["interfaces"][intf_name].update({
                "ipv4": {
                    "address": ipv4_addr.ip.exploded,
                    "netmask": ipv4_addr.netmask.exploded
                }
            })

    print("\nEXTRACTED PARAMETERS\n")
    print(json.dumps(result, indent=4))