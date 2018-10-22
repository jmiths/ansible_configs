#!/usr/bin/python3
import sys
import json
import pprint
import glob

graph=open("graph.dot",'w')
graph.write("digraph G {\n")
graph.write("ranksep=10;\n")

inventory_file=sys.argv[1]
files=glob.glob('../inventory/*.yml')
graph_list=[]
graph_list_all=[]
rdiff_clients=[]

for filename in files:
        ymlFile=open(filename,'r')
        for line in ymlFile:
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
                        if group=="rdiff_backup_clients":
                                rdiff_clients.append(line)
                        elif len(sys.argv)==2 and line==sys.argv[1]:#if host is equal to user specified host draw red line from host to parent groups
                                if line in rdiff_clients:
                                        graph.write("\t"+line+"[style=filled,color=\".7 .3 1.0\"];\n")
                                        graph.write("\t" + group + " -> " + line +"[color=red];\n")
                                else:
                                        graph.write("\t" + group + " -> " + line +"[color=red];\n")
                        else:
                                if line in rdiff_clients:
                                        graph.write("\t"+line+"[style=filled,color=\".7 .3 1.0\"];\n")
                                else:
                                        graph.write("\t" + group + " -> " + line +";\n")
        graph_list_all.append(graph_list)
        graph_list=[]
        ymlFile.close()
#json parsing below
with open(inventory_file) as data_file:
        data = json.load(data_file)
        
for x in data:
        for i in data[x]:
                for a in data[x][i]:
                        x=x.rstrip()
                        x=x.replace("-","_")
                        a=a.rstrip()
                        a=a.replace("-","_")
                        if x=="group_all":
                                continue
                        if a=="edge":
                                a="\"edge\""
                        if x=="rdiff_backup_clients":
                                rdiff_clients.append(a)
                                #graph.write("\t"+a+"color=red];\n")
                        elif len(sys.argv)==3 and a==sys.argv[2]:
                                if a in rdiff_clients:
                                        graph.write("\t"+a+"[style=filled,color=\".7 .3 1.0\"];\n")     
                                        graph.write("\t"+x+" -> "+a+"[color=red];\n")        
                                else:
                                        graph.write("\t"+x+" -> "+a+"[color=red];\n")
                               # graph_list.append("\t"+x+" -> "+a+"[color=red];\n")
                        else:
                                if a in rdiff_clients:
                                        graph.write("\t"+a+"[style=filled,color=\".7 .3 1.0\"];\n")
                                        graph.write("\t"+x+" -> "+a+";\n")      
                                else:
                                        graph.write("\t"+x+" -> "+a+";\n")
                                #graph_list.append("\t" +x+" -> "+ a +";\n")

        graph_list_all.append(graph_list)
        graph_list=[]

#for x in graph_list_all:
#        print(x)

graph.write("}")
graph.close()

