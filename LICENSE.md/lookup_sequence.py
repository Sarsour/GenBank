#!/usr/bin/python

#Ask for user input to see what accession the user wants the FASTA entry for
userFASTA = input("Enter accession: ")
print("")

data = {}


file = open("e_coli_k12_dh10b.faa", "r")

for line in file:
	if userFASTA in line:
		print(line)
		for line in file:
			if ">" in line:
				break
			print(line)