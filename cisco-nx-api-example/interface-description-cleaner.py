"""
interface description cleaner
-----------------------------

This script will utilize the Cisco NX-API to update the interface descriptions on a Cisco Nexus switches
based on CDP information.

"""
import json
import requests
import re

# todo update the device information when testing the script
# get CDP information from the following clients and update there configuration
hosts = [
    "10.1.1.1",
    "10.1.1.2"
]

# credentials to use on the Cisco NX-API
dev_username = "setup"
dev_password = "setup"

# HTTPs server port, which is used on every Switch to connect to the Cisco NX-API
HTTPS_SERVER_PORT = "8181"

"""
------------------------------------------------------------------------------------------------------------------------
some helper functions to work with the Cisco NX-API
"""
# suppress the unverified request messages (when using self-signed certificates)
requests.packages.urllib3.disable_warnings()

def nxapi_cli_conf(commands, hostname, username, password):
    """
    executes configure commands on the given host using Cisco NX-API

    :param username: username for authentication
    :param password: password for authentication
    :param hostname: the hostname, where the Cisco NX-API call must be executed
    :param commands: the configuration commands that should be executed on the switch using Cisco NX-API
    """
    # convert the given configuration commands to a format which can be used within the Cisco NX-API and verify
    # that the configuration script does not end with the termination sign (lead to an error in the last command)
    commands = commands.replace("\n"," ; ")
    if commands.endswith(" ; "):
        commands = commands[:-3]

    payload = {
        "ins_api": {
            "version": "1.2",
            "type": "cli_conf",
            "chunk": "0",               # do not chunk results
            "sid": "1",
            "input": commands,
            "output_format": "json"
        }
    }
    return nxapi_call(hostname, payload, username, password, "json")

def nxapi_cli_show(show_command, hostname, username, password):
    """
    execute show command on the given host using Cisco NX-API

    :param username: username for authentication
    :param password: password for authentication
    :param hostname: the hostname, where the Cisco NX-API call must be executed
    :param show_command: the show command, that should be executed on the switch
    """
    payload = [
        {
            "jsonrpc": "2.0",
            "method": "cli",
            "params": {
                "cmd": show_command,
                "version": 1.2
            },
            "id": 1
        }
    ]
    return nxapi_call(hostname, payload, username, password, "json-rpc")

def nxapi_call(hostname, payload, username, password, content_type="json"):
    """
    common NX-API call which includes some basic verification of the response

    :param hostname: the hostname, where the Cisco NX-API call must be executed
    :param payload: the payload for the NX-API call
    :param username: username for authentication
    :param password: password for authentication
    :param content_type: the content type of the payload, defaults to "JSON"
    """
    headers={'content-type':'application/%s' % content_type}
    response = requests.post("https://%s:%s/ins" % (hostname, HTTPS_SERVER_PORT),
                             auth=(username, password),
                             headers=headers,
                             data=json.dumps(payload),
                             verify=False,                      # disable SSH certificate verification
                             timeout=4)
    if response.status_code == 200:
        # verify result if a cli_conf operation was performed
        if "ins_api" in payload:
            if "type" in payload['ins_api'].keys():
                if "cli_conf" in payload['ins_api']['type']:
                    for result in response.json()['ins_api']['outputs']['output']:
                        if result['code'] != "200":
                            print("--> partial configuration failed, please verify your configuration!")
                            break
        return response.json()
    else:
        msg = "call to %s failed, status code %d (%s)" % (target_host,
                                                          response.status_code,
                                                          response.content.decode("utf-8"))
        print(msg)
        raise Exception(msg)

def interface_shortener(interface_name):
    """
    makes Cisco interface names shorter (e.g. 'Ethernet' to 'Eth')

    :param interface_name:
    """
    interface_short_string_map = [
        { "from": "Ethernet", "to": "Eth"},
        { "from": "GigabitEthernet", "to": "Gi"},
        { "from": "FastEthernet", "to": "Fa"},
        { "from": "TenGigabitEthernet", "to": "Te"},
    ]
    result = interface_name
    for s in interface_short_string_map:
        if re.match(r"^%s" % s['from'], result) is not None:
            result = result.replace(s['from'], s['to'])
            break
    return result

"""
------------------------------------------------------------------------------------------------------------------------
the interface description cleaner script
"""

if __name__ == "__main__":
    print("----------------------------------------")
    print("start the interface description cleaner ")
    print("----------------------------------------")
    host_results = dict()
    for target_host in hosts:
        print("request CDP information for switch: %s" % target_host)
        result = nxapi_cli_show("show cdp neighbor detail", target_host, dev_username, dev_password)

        # dump neighbors
        neighbor_statements = result['result']['body']['TABLE_cdp_neighbor_detail_info']['ROW_cdp_neighbor_detail_info']

        host_neighbors = list()

        if type(neighbor_statements) is not list:
            # convert to a list if only a single entry in a dictionary is received from the device
            neighbor_statements = [neighbor_statements]

        for neighbor in neighbor_statements:
            # remove SN and/or DNS prefix from hostname
            remote_host = neighbor['device_id'].split("(")[0]
            if "." in remote_host:
                remote_host = remote_host.split(".")[0]

            # descriptions should not be that long...
            local_interface = interface_shortener(neighbor['intf_id'])
            remote_interface = interface_shortener(neighbor['port_id'])

            entry = {
                "local_interface": local_interface,
                "remote_host": remote_host,
                "remote_interface": remote_interface,
                "remote_mgmt_ip": neighbor['v4mgmtaddr']
            }
            host_neighbors.append(entry)

        host_results[target_host] = host_neighbors

    # generate change script per device and push to it
    for host in host_results.keys():
        # create change script
        change_script = ""
        for entry in host_results[host]:
            change_script += "interface %s\n description *** %s, %s (%s)\n" % (entry['local_interface'],
                                                                               entry['remote_interface'],
                                                                               entry['remote_host'],
                                                                               entry['remote_mgmt_ip'])
        # verify that  the output is correct
        print("apply change script: %s" % host)
        response = nxapi_cli_conf(change_script, host, dev_username, dev_password)

    print("finished successful")
