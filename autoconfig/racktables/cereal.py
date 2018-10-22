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

def from_racktables():
	cereal_ports = "https://racktables.com/racknews"
	cereal = requests.get(cereal_ports,auth=(user,password)).text
	cereal = cereal.replace('null','""')
	cereal = cereal.replace('\\',"")
	cereal = json.loads(cereal)
	return cereal

def parse_cereal(cereal):
	ports_by_cereal_host={}
	for host in cereal:
		hostname = host["name"]
		console = host["Console Port"]
		console = console.split(':')
		if console[0] not in ports_by_cereal_host:
			ports_by_cereal_host[console[0]] = []
		ports_by_cereal_host[console[0]].append([host["name"],console[1],console[2]])
	return ports_by_cereal_host

def output(cereal_dict):
	for cereal_host, key in cereal_dict.items():
		write_to = "../host_vars/" + cereal_host
		if not os.path.exists(write_to):
			os.makedirs(write_to)
		out = open(write_to + "/cereal.yml",'w')
		out.write("cereal:\n")
		for port in key:
			out.write("  - hostname: " + port[0] + "\n")
			out.write("    cereal_port:\n")
			out.write("     - { location: \'" + port[1] + "\', speed: \'" + port[2] + "\' }\n")

cereal = from_racktables()
cereal_ports = parse_cereal(cereal)
output(cereal_ports)
