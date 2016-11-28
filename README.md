# python script examples

This repository contains my python script examples that focuses on use cases for Network Engineers. They are explained
in more detail in the associated Blog posts at the [Coding Networker Blog](https://codingnetworker.com).

The following examples are included in this repository:

* [Parse CLI outputs with TextFSM](https://codingnetworker.com/2015/08/parse-cli-outputs-textfsm/) - This post describes how to parse CLI outputs using TextFSM. Within the an example, I work with multiple "show inventory" commands from a Cisco IOS device in a single text file.
* [Configuration generator with python and Jinja2](https://codingnetworker.com/2015/09/configuration-generator-with-python-and-jinja2/) - This post describes, how to build a simple configuration generator using python and Jinja2. I'll explain it using CSV and JSON based parameter files.
* [Cisco NX-API on Nexus 5500](https://codingnetworker.com/2015/09/cisco-nx-api-nexus-5500/) - This post gives you a short introduction to the Cisco NX-API on Nexus 5500 with NX-OS 7.2
* [Custom filters for a Jinja2 based config generator](https://codingnetworker.com/2015/10/custom-filters-jinja2-config-generator/) - In this post, I'll explain how to include custom filters in Jinja2 and how to use them within the configuration templates
* [Implement HSRP using ciscoconfparse](https://codingnetworker.com/2015/10/implement-hsrp-using-ciscoconfparse/) - This post describes an example to create a configuration for HSRP based on an existing Cisco IOS configuration using the ciscoconfparse module
* **JSON data structure**

    * [python dictionaries and JSON (crash course)](https://codingnetworker.com/2015/10/python-dictionaries-json-crash-course/) - Just a quick crash course about the use of python dictionaries and the JSON data format
    * [Validating JSON data using cerberus](https://codingnetworker.com/2016/03/validate-json-data-using-cerberus/) - In this post, I'll look at a way to verify JSON data using cerberus 

* [HTTP calls using the python requests library](https://codingnetworker.com/2015/10/http-calls-using-python-requests-library/) - How to use the requests library in python based on the example code from the Cisco NX-API post ("interface description cleaner")
* [Reconfigure static ARP entries using ciscoconfparse](https://codingnetworker.com/2015/11/reconfigure-static-arp-entries-ciscoconfparse/) - This post describes how to parse an existing configuration and reconfigure it using the example of static ARP entries (from Cisco VSS to Cisco vPC)
* [Introduction to the python ipaddress module](https://codingnetworker.com/2015/12/introduction-python-ipaddress-module/) - quick introduction to the python ipaddress module
* [Automate SSH connections with netmiko](https://codingnetworker.com/2016/03/automate-ssh-connections-with-netmiko/) - automate SSH connection with netmiko and visualize the results using HTML, CSS and Javascript
* [Parse Cisco IOS configurations with RegEx ](https://codingnetworker.com/2016/05/parse-cisco-ios-configurations-regex/) - some basic examples how to parse Cisco IOS configuration using regular expressions
* [Parse Cisco IOS configuration using ciscoconfparse](https://codingnetworker.com/2016/06/parse-cisco-ios-configuration-ciscoconfparse/) - examples how to parse Cisco IOS configuration using ciscoconfparse (follow up to the last post)
* [Extract CLI commands from Session Logs](https://codingnetworker.com/2016/08/extract-cli-commands-session-logs/) - short script to split multiple CLI commands and outputs from multiple text files (e.g. putty session logs)
* [Pandas DataFrame 101](https://codingnetworker.com/2016/09/pandas-dataframes-101/) - introduction to pandas DataFrames
* [Merge DataFrames in Pandas](https://codingnetworker.com/2016/11/merge-dataframes-pandas/) - how to merge pandas DataFrames based on an example using Excel

In the post [about Vagrant](https://codingnetworker.com/2015/09/use-vagrant-to-run-the-python-examples/), I'll explain how to execute the examples within a virtual machine. This Vagrant VM also contains a pre-configured Jupyter environment, which is described in more detail in the post about [Jupyter: an interactive web-based python shell](https://codingnetworker.com/2015/11/jupyter-interactive-web-based-python-shell/).