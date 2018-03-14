#!/usr/local/bin/python3
import jinja2
import re
import cgi
import os

#Jinja and html setup
templateLoader = jinja2.FileSystemLoader( searchpath="./templates")

env = jinja2.Environment(loader=templateLoader)
template = env.get_template('compare.html')

#Read predicted proteins
predicted_proteins = 0
predicted_gene_start_position_list = []
predicted_gene_end_position_list = []
predicted_protein_ids = []

with open('predictedproteins.faa') as predictedfile:
	for line in predictedfile:
		if '>' in line:
			predicted_proteins += 1
			temp_list = line.split(' ')
			predicted_protein_ids.append(temp_list[0])
			predicted_gene_start_position_list.append(int(temp_list[2]))
			predicted_gene_end_position_list.append(int(temp_list[4]))
predictedfile.close()

#Read actual proteins
actual_proteins = 0
actual_gene_start_position_list = []
actual_gene_end_position_list = []
actual_protein_ids = []

with open('actualproteins.txt') as actualfile:
	for line in actualfile:
		if '>' in line:
			actual_proteins += 1
			temp_list = line.split('..')
			actual_gene_start_position_list.append(temp_list[0])
			actual_gene_end_position_list.append(temp_list[1])
		if 'prot_' in line:
			temp_list = line.split('prot_')
			actual_protein_ids.append(temp_list[1])
actualfile.close()

#Clean up the position lists (extract the coordinates)
for i in range(len(actual_gene_end_position_list)):
	for j in actual_gene_end_position_list[i]:
		if not j.isdigit():
			actual_gene_end_position_list[i] = actual_gene_end_position_list[i].replace(j, '')

for i in range(len(actual_gene_start_position_list)):
	actual_gene_start_position_list[i] = actual_gene_start_position_list[i][actual_gene_start_position_list[i].rfind('='):]
for i in range(len(actual_gene_start_position_list)):
	for j in actual_gene_start_position_list[i]:
		if not j.isdigit():
			actual_gene_start_position_list[i] = actual_gene_start_position_list[i].replace(j, '')

#Find first coordinates since it's formatted differently
with open('actualproteins.txt') as actualfile:
	first_line = actualfile.readline()
	first_line_comps = first_line.split('1..')
	actual_gene_start_position_list[0] = 1
	actual_gene_end_position_list[0] = first_line_comps[1]
actualfile.close()	
for i in actual_gene_end_position_list[0]:
	if not i.isdigit():
		actual_gene_end_position_list[0] = actual_gene_end_position_list[0].replace(i, '')

#Make sure coordinates in list are numbers, not strings
predicted_gene_start_position_list = list(map(int, predicted_gene_start_position_list))
predicted_gene_end_position_list = list(map(int, predicted_gene_end_position_list))
actual_gene_start_position_list = list(map(int, actual_gene_start_position_list))
actual_gene_end_position_list = list(map(int, actual_gene_end_position_list))

#Clean up actual_protein_ids and predicted_protein_ids to isolate the ids
for i in range(len(actual_protein_ids)):
	actual_protein_ids[i] = actual_protein_ids[i][:10]
for i in range(len(predicted_protein_ids)):
	predicted_protein_ids[i] = predicted_protein_ids[i][1:]
	
#Compare coordinates
compare_start_coordinates = []
compare_end_coordinates = []
agreement_list = []	

for i in range(len(actual_gene_start_position_list)):
	if actual_gene_start_position_list[i] == predicted_gene_start_position_list[i]:
		compare_start_coordinates.append('agrees')
	else:
		compare_start_coordinates.append('disagrees')
		
for i in range(len(actual_gene_end_position_list)):
	if actual_gene_end_position_list[i] == predicted_gene_end_position_list[i]:
		compare_end_coordinates.append('agrees')
	else:
		compare_end_coordinates.append('disagrees')

for i in range(len(actual_gene_start_position_list)):
	if compare_start_coordinates[i] == 'agrees' and compare_end_coordinates[i] == 'agrees':
		agreement_list.append('EXACT')
	elif compare_start_coordinates[i] == 'agrees':
		agreement_list.append("5' MATCH")
	elif compare_end_coordinates[i] == 'agrees':
		agreement_list.append("3' MATCH")
	else:
		agreement_list.append('NONE')
		
#Find number of matches for each strand
exact_matches = agreement_list.count('EXACT')
start_matches = agreement_list.count("5' MATCH")
end_matches = agreement_list.count("3' MATCH")
no_matches = agreement_list.count("NONE")

#Make all lists the same length as the longer list (for table purposes)
difference = len(predicted_protein_ids) - len(actual_protein_ids)
for i in range(difference):
	actual_protein_ids.append('N/A')
	actual_gene_start_position_list.append(0)
	actual_gene_end_position_list.append(0)
	compare_start_coordinates.append('N/A')
	compare_end_coordinates.append('N/A')
	agreement_list.append('N/A')

#Testing below
print('Actual Proteins:', actual_proteins)
print('Predicted Proteins:', predicted_proteins)
print('Exact Coordinate Matches:', exact_matches)
print("5' Only Matches:", start_matches)
print("3' Only Matches:", end_matches)
print("No Matches:", no_matches)

for i in range(len(actual_protein_ids)):
	print(actual_protein_ids[i], '-----', actual_gene_start_position_list[i], '-----', actual_gene_end_position_list[i], '-----', predicted_protein_ids[i], '-----', predicted_gene_start_position_list[i], '-----', 
	predicted_gene_end_position_list[i], '-----', compare_start_coordinates[i], '-----', compare_end_coordinates[i], '-----', agreement_list[i])

#Create objects to pass
class Entry(object):
	ap_ids = ""
	ags_pos = ""
	age_pos = ""
	pp_ids = ""
	pgs_pos = ""
	pge_pos = ""
	agree = ""

def make_entry(ap_ids, ags_pos, age_pos, pp_ids, pgs_pos, pge_pos, agree):
	entry = Entry()
	entry.ap_ids = ap_ids
	entry.ags_pos = ags_pos
	entry.age_pos = age_pos
	entry.pp_ids = pp_ids
	entry.pgs_pos = pgs_pos
	entry.pge_pos = pge_pos
	entry.agree = agree
	
	return entry

#Create list of entries
my_entries = []
i = 0

while i < len(actual_protein_ids):
	my_entries.append(make_entry(actual_protein_ids[i], actual_gene_start_position_list[i], actual_gene_end_position_list[i]
	, predicted_protein_ids[i], predicted_gene_start_position_list[i], predicted_gene_end_position_list[i], agreement_list[i]))
	i += 1
	
print("Content-Type: text/html\n\n")
print(template.render(ents = my_entries)

"""
							Variables being passes to database and html template:
Variables:
actual_proteins							- Number of actual proteins
predicted_proteins						- number of predicted proteins form Prodigal
exact_matches							- Count of exact coordinate matches
start_matches							- Count of 5' only matches
end_matches								- Count of 3' only matches
no_matches								- Count of no coordinate matches

Lists:
actual_protein_ids						- Actual protein ids from GenBank
actual_gene_start_position_list			- 5' gene start positions for GenBank actual genes
actual_gene_end_position_list			- 3' gene end positions for GenBank actual genes
predicted_protein_ids					- Predicted protein ids from Prodigal
predicted_gene_start_position_list		- 5' gene start positions for Prodigal predicted genes
predicted_gene_end_position_list		- 3' gene end positions for Prodigal predicted genes
compare_start_coordinates				- Do the start positions of each respective gene match?
compare_end_coordinates					- Do the end positoins of each respective gene match?
agreement_list							- How well do the coordinates match?  What strand if not both?
"""