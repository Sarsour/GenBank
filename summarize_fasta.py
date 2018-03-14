#!/usr/bin/python

with open("e_coli_k12_dh10b.faa") as file:
    geneList = file.readlines()

#find number of genes and hypothetical count
geneCount = 0
hypotheticalCount = 0

for index in geneList:
	if ">" in index:
		geneCount +=1
	if "hypothetical" in index:
		hypotheticalCount += 1
		
print("Gene Count:", geneCount)
print("Hypothetical Genes:", hypotheticalCount)



#Find min, max, and average protein length
maxLength = 0
currentLength = 0
line = ""
lengthList = []

for elem in geneList:
	if ">" not in elem:
		currentLength = currentLength + len(elem)
	if ">" in elem:
		lengthList.extend([currentLength])
		currentLength = 0
lengthList.extend([currentLength])
del lengthList[0]


print("Maximum Protein Length:", max(lengthList))
print("Minimum Protein Length:", min(lengthList))
print("Average Protein Length:",(sum(lengthList))/len(lengthList))