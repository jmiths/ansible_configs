#!/usr/bin/python3
#to generate graph:
#	run this script (adding a host name parameter causes the program to draw a red line from the host to its parent groups
#	generate graph with "dot -Tpng -o graph.gif graph.dot"
import sys
invent = open("inventory",'r')
graph = open("graph.dot",'w')
graph.write("digraph G {\n")
graph.write("ranksep=3;\n")#sets spacing between nodes to 3" 
for line in invent:
	line = line.rstrip()
	line = line.replace("-","_")
	if "[" in line:
		if "children" in line:
			groupIndex = line.find(":")
			group = line[1:groupIndex]
		else:
			group = line[1:-1]
			
	elif line == "":
		continue
	else:
		if line=="edge":
			line="\"edge\""
		if len(sys.argv)==2 and line==sys.argv[1]:#if host is equal to user specified host draw red line from host to parent groups
			graph.write("\t" + group + " -> " + line +"[color=red];\n")
		else:		
			graph.write("\t" + group + " -> " + line +";\n")
		
graph.write("}")
graph.close()
invent.close()
