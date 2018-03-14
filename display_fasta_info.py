#!/usr/bin/python

import jinja2
import re

templateLoader = jinja2.FileSystemLoader( searchpath="./templates")

env = jinja2.Environment(loader=templateLoader)
template = env.get_template('display_fasta_info.html')

cols = list()
idList = list()
lengthList = list()
restOfHeaderList = list()

#Find ID and rest of header
for line in open("e_coli_k12_dh10b.faa"):
	if " " in line:
		cols = line.split(" ",1)
		idList.append(cols[0])
		restOfHeaderList.append(cols[1])


#Find protein lengths
currentLength = 0
line = ""

for line in open("e_coli_k12_dh10b.faa"):
	if ">" not in line:
		currentLength = (currentLength + len(line))
	if ">" in line:
		lengthList.extend([currentLength-1])
		currentLength = 0
lengthList.extend([currentLength-1])

#Delete first index (gene information)
del idList[0]
del lengthList[0]
del restOfHeaderList[0]

print("Content_Type: text/html\n\n")
print(template.render(ids=idList, lengths=lengthList,rest=restOfHeaderList))



