#!/bin/bash

./../inventory/zabbix.py --list >> output.json
./generate.py output.json $1
dot -Tpng graph.dot -o graph.gif
gimp graph.gif
rm output.json
