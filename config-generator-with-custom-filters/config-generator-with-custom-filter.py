"""
config generator with custom filter
-----------------------------------

This script will generate an interface configuration for a Cisco IOS and Juniper JUNOS device based on a common set of
parameters to demonstrate the use of custom filters with the Jinja2 template engine.

"""
import jinja2
import json
import os
from ipaddress import IPv4Network
from slugify import slugify

parameter_file = "parameters.json"
template_file = "ip-interface-config.jinja2"
output_directory = "_output"


def dotted_decimal(prefix_length):
    """
    converts the given prefix to a IPv4 dotted decimal representation
    :param prefix_length:
    :return:
    """
    try:
        ip = IPv4Network("0.0.0.0/" + str(prefix_length))
        return ip.netmask
    except Exception:
        return "[INVALID VALUE(" + str(prefix_length) + ")]"


def slugify_string(text):
    """
    convert the given string to a slug
    :param text:
    :return:
    """
    return slugify(text)


if __name__ == "__main__":
    # create Jinja2 template environment with the link to the current directory
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="."),
                             trim_blocks=True,
                             lstrip_blocks=True)

    # register custom filters on the jinja2 environment
    env.filters["dotted_decimal"] = dotted_decimal
    env.filters["slugify_string"] = slugify_string

    # load template file
    template = env.get_template(template_file)

    # just make sure that the output directory exists
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    print("Load common parameter set and define vendors...")
    vendors = ["Cisco_IOS", "Juniper"]
    interface_parameter_json = json.load(open(parameter_file))

    # create the templates for all vendors
    print("Create templates for all vendors...")
    for vendor in vendors:
        parameter = {
            "vendor": vendor,
            "feature_string": ["Infrastructure ACLs"],
        }
        parameter.update(interface_parameter_json.copy())
        result = template.render(parameter)
        f = open(os.path.join(output_directory, vendor + "-ip_interfaces.config"), "w")
        f.write(result)
        f.close()
        print("Configuration '%s' created for %s" % (vendor + "-ip_interfaces.config", vendor))

    print("DONE")
