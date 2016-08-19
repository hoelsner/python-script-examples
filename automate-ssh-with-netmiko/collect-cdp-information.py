"""
This script collects the CDP information from a Cisco device using SSH. These information are converted to a JSON data
structure that is used within a HTML page to create a simple network diagram.

It uses netmiko, TextFSM and vis.js.
"""
import json
import os
import webbrowser
import sys
import textfsm
from netmiko import ConnectHandler


def get_cdp_neighbor_details(ip, username, password, enable_secret):
    """
    get the CDP neighbor detail from the device using SSH

    :param ip: IP address of the device
    :param username: username used for the authentication
    :param password: password used for the authentication
    :param enable_secret: enable secret
    :return:
    """
    # establish a connection to the device
    ssh_connection = ConnectHandler(
        device_type='cisco_ios',
        ip=ip,
        username=username,
        password=password,
        secret=enable_secret
    )

    # enter enable mode
    ssh_connection.enable()

    # prepend the command prompt to the result (used to identify the local device)
    result = ssh_connection.find_prompt() + "\n"

    # execute the show cdp neighbor detail command
    # we increase the delay_factor for this command, because it take some time if many devices are seen by CDP
    result += ssh_connection.send_command("show cdp neighbor detail", delay_factor=2)

    # close SSH connection
    ssh_connection.disconnect()

    return result


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("\nplease provide the following arguments:")
        print("\tcollect-cdp-information.py <ip> <username> <password> <enable secret>\n\n")
        sys.exit(0)

    target_ip = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    secret = sys.argv[4]

    try:
        print("collect CDP information from device %s..." % target_ip)
        cdp_det_result = get_cdp_neighbor_details(
            ip=target_ip,
            username=username,
            password=password,
            enable_secret=secret
        )

        found_hosts = []
        nodes = []
        edges = []

        # parse the show cdp details command using TextFSM
        print("parse results...")
        re_table = textfsm.TextFSM(open("show_cdp_neighbor_detail.textfsm"))
        fsm_results = re_table.ParseText(cdp_det_result)
        local_hostname = "not discovered"

        counter = 1
        for e in fsm_results:
            if len(nodes) == 0:
                # add local node (always ID 1)
                node = {
                    "id": counter,
                    "label": e[0],
                    "group": "root_device"
                }

                counter += 1
                nodes.append(node)

            # add new node
            remote_node = e[1]
            if remote_node not in found_hosts:
                # add new node
                node = {
                    "id": counter,
                    "label": remote_node,
                    "title": "<strong>Mgmt-IP:</strong><br>%s<br><br><strong>Platform</strong>:<br> "
                             "%s<br><br><strong>Version:</strong><br> %s" % (e[2], e[3], e[6]),
                    "group": "attached_device"
                }
                nodes.append(node)

                # add new connection
                edge = {
                    "from": 1,
                    "to": counter,
                    "title": "from: %s<br>to: %s" % (e[5], e[4]),
                    "label": "",
                    "value": 0,
                    "font": {
                        "align": "top"
                    }
                }
                edges.append(edge)
                found_hosts.append(remote_node)
                counter += 1

            else:
                # only add connection of existing device
                current_node = None
                for n in nodes:
                    if remote_node in n["label"]:
                        current_node = n
                        break

                if current_node:
                    # search existing connection and increase the value of the link
                    for edge in edges:
                        if edge["to"] == current_node["id"]:
                            edge["value"] += 10
                            edge["title"] += "<hr>from: %s<br>to: %s" % (e[4], e[5])

                else:
                    # not found
                    print("host %s should exist, but was not found in the dictionary." % remote_node)

        data = {
            "nodes": nodes,
            "edges": edges
        }
        print("write results to data.js...")
        datajs = "var data = " + json.dumps(data, indent=4)
        if os.path.exists("data.js"):
            os.remove("data.js")

        f = open("data.js", "w")
        f.write(datajs)
        f.close()

        print("open browser with results....")
        webbrowser.open_new_tab(os.path.abspath("data.js"))
        print("done")

    except Exception as ex:
        print("Exception occurred: %s" % ex)
