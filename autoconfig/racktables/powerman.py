#!/usr/bin/python3

import getpass
import requests
import json
import sys
import os

if len(sys.argv) > 2:
    password = sys.argv[2]
    user = sys.argv[1]
else:
    user = getpass.getuser()
    password = getpass.getpass("Enter your Password: \n")

def location_of_wps():
    location = {}
# This URL gets only WPS and those who have console ports
    locate_wps = "https://racktables.com/racknews"
    locate = requests.get(locate_wps,auth=(user,password)).text
    locate = locate.replace('null','""')
    locate = locate.replace('\\',"")
    locate = json.loads(locate)

    for wps in locate: # Record comes {name: wps-name , Port: wps-host:dev:speed
        console = wps["Console Port"]
        console = console.split(":")
        location[console[0]] = [wps["name"],console[1],console[2]]
    return location


def parse_powerman():
# This URL gets the all servers that have at least one powerman port and of those it takes the three powerman ports (assuming we don't have four plug servers yet
    url = "https://racktables.com/racknews"
    r = requests.get(url,auth=(user,password)).text
    r = r.replace('null','""')
    powerman = json.loads(r)
    ports_by_host = []
    for host in powerman: # For every host
        hostname = host["name"]
        ports = []
        all_web = True # Have I seen a wps that needs cereal?
        needs_host = None # If I have seen a wps that needs to be all on one host, who?
        for i in range(1,4): # There are only powerman ports 1-3 atm
            port = host["powerman port " + str(i)]
            if "host" in port: # There may be a character in the field, but typing host is an attempt to break it, limited error check
                port = port.replace('&quot;','"') # Trust me, wait to here to parse hand built dict
                port = json.loads(port)
                temp = [] # We need to keep ports in memory should they all require same host
                wps_host = port["host"] # Which wps are we talking about
                if wps_host != "web":   # If you are not a web wps, then this machine needs all one stargate to take care
                    all_web = False       # Flip bool, could be done with one value, but this reads better
                    needs_host = wps_host # Save the host that ruined everything
                temp.append(wps_host)
                temp.append(hostname)
                temp.append(port["wps"]) # Format: [ wps_host, hostname affected, wps, port, label ]
                temp.append(port["port"])
                temp.append(port["label"])
                ports.append(temp)
        if all_web == False:  # If you need a certain host, then all ports on hostname must take it
            for port in ports:
                port[0] = needs_host
        for port in ports:  # Finally flatten list for easy steps
            ports_by_host.append(port)
    return ports_by_host


def build_dicts(ports_by_host):
    wps_hosts = {}
    aliases = {}
    for ports in ports_by_host: # Go through each port, no longer by host
        wps_host = ports[0]
        hostname = ports[1]
        wps = ports[2]
        port = ports[3]
        label = ports[4]
        if wps_host not in wps_hosts: # If I haven't seen the wps host [web,sgs] make it known to aliases and wps_host
            wps_hosts[wps_host] = {}
            aliases[wps_host] = {}
        if label.strip() == "": # If I don't have a label, I am the only port on this machine
            if hostname not in wps_hosts[wps_host]:
                wps_hosts[wps_host][hostname] = {}
            wps_hosts[wps_host][hostname]["wps"] = wps
            wps_hosts[wps_host][hostname]["port"] = port
        else: # I need to worry about aliases and port labels
            temp = hostname + "-" + label
            wps_hosts[wps_host][temp] = {}
            wps_hosts[wps_host][temp]["wps"] = wps
            wps_hosts[wps_host][temp]["port"] = port
            if hostname not in aliases[wps_host]: # If aliases doesn't know about HN
                aliases[wps_host][hostname] = []
            aliases[wps_host][hostname].append(temp) # At hostname, but an alias
    return wps_hosts, aliases


def output_vars(wps_hosts,aliases):
    for wps_host, key in wps_hosts.items():  # Time to print by sg1,sg2,web...
        if wps_host != "web":
            write_to = "../host_vars/" + wps_host
            if not os.path.exists(write_to):
                os.makedirs(write_to)
            out = open(write_to + "/powerman.yml" ,'w')
            out.write("power:\n")  # SGs get variable power to use
        else:
            if not os.path.exists("../roles/powerman-server/defaults"):
                os.makedirs("../roles/powerman-server/defaults")
            write_to = "../roles/powerman-server/defaults/main.yml" # Web kept in defaults
            out = open(write_to,'w')
            out.write("web_power:\n")   # Everyone gets web power
        hostnames = sorted(list(key.keys()))
        for hostname in hostnames:  # Ansible variable parsing
            keys = key[hostname]
            '''
        Output looks like this:
            power:
               - hostname: curve
                 port:
                  -  { wps: 'wps-08', port: 19 }
               - hostname: network2-l
                 port:
                 -  { wps: 'wps-08', port: 6 }
               - hostname: pegasus-b
                 port:
                 -  { wps: 'wps-08', port: 18 }
            '''
            out.write("   - hostname: " + hostname + "\n")
            out.write("     port:\n")
            out.write("      -  { wps: \'" + keys["wps"] + "\', port: " + keys["port"] + " }\n")
        if wps_host != "web": # Once again web have special aliases that are not contained within a host var
            if aliases[wps_host]: # If I actually have aliases to output
                out.write("aliases:\n")
            else:
                out.write("aliases: False\n")
        else:
            out.write("web_aliases:\n")
        for host, key in aliases[wps_host].items(): # Reference SG1,SG2.. web for aliases
            out.write("    - hostname: " + host + "\n")
            out.write("      alias:\n")
            for alias in key:
                out.write("       - " + alias + "\n")
        if wps_host != "web":
            console = location[wps_host]  # Finally output where WPS is attached
            out.write("wps:\n")
            out.write("  name: " + console[0] + "\n")
            out.write("  dev: " + console[1] + "\n")
            out.write("  speed: " + console[2] + "\n")

ports_by_hosts = parse_powerman()
location = location_of_wps()
wps_hosts, aliases = build_dicts(ports_by_hosts)
output_vars(wps_hosts,aliases)
