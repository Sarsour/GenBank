#!/usr/local/bin/python3

from Bio import Entrez
import sys
from pathlib import Path
import os
import glob
import jinja2
import re
import cgi
import mysql.connector

#File1 AB011549.2
#File2 NG_008929.1
#File3 NIIM01000017.1
#File4 AF184072.1
#File5 NZ_CP013436.1 (predicted gene)

templateLoader = jinja2.FileSystemLoader( searchpath="./templates")
env = jinja2.Environment(loader=templateLoader)
template = env.get_template('search_gb.html')

first_accession = 'None'
second_accession = 'None'

form = cgi.FieldStorage()
if not form.getfirst('acc1') is None :
	first_accession = form.getfirst('acc1')
if not form.getfirst('acc2') is None:
	second_accession = form.getfirst('acc2')
#first_accession = 'NG_008929.1'
#second_accession = 'AB011549.2'

table_pure_accession_list = []
table_accession_list = []
table_organism_list = []
table_gene_number_list = []
table_basepair_number_list = []
table_gene_list = []
table_all_accessions_list = []

conn = mysql.connector.connect(user='nsarsou1', password='password', host='localhost', database='nsarsou1')
cursor = conn.cursor()

qry="""SELECT Pure_Accession, Accession, Organism, Gene_Number, Basepair_Number FROM Accessions WHERE Pure_Accession in (%s,%s)"""
cursor.execute(qry, (first_accession, second_accession ))

for (table_pure_accession, table_accession, table_organism, table_gene_number, table_basepair_number) in cursor:
	table_pure_accession_list.append(table_pure_accession)
	table_accession_list.append(table_accession)
	table_organism_list.append(table_organism)
	table_gene_number_list.append(table_gene_number)
	table_basepair_number_list.append(table_basepair_number)



# Main method
def main():

	# Check database to search for accession.  If it's there, file will be extracted from GenBank and parsed.
	if check_accession(first_accession) == False:
		first_gb_file = get_gb_files_from_GenBank(first_accession)
		parse_gb_files(first_gb_file, first_accession)

	if check_accession(second_accession) == False:
		second_gb_file = get_gb_files_from_GenBank(second_accession)
		parse_gb_files(second_gb_file, second_accession)

	# Call method to delete mined gb files
	delete_temp_files()	

	#display_data(first_accession, second_accession)

	''' NEXT:
		Take user input from html for accessions instead of from terminal
		Take out data from database and display on html template
	'''


# Check accession in database before extracting and parsing
def check_accession(accession):

	accession_woversion, version = accession.split('.')
	
	conn = mysql.connector.connect(user='nsarsou1', password='password', host='localhost', database='nsarsou1')
	cursor = conn.cursor()

	qry = """ SELECT Accession FROM Accessions WHERE Accession = %s"""

	cursor.execute(qry, (accession_woversion, ))

	result  = ''
	for a in cursor:
		result = a	

	if result  == '':
		return False
	else:
		return True

	cursor.close()
	conn.close()


# Mine the gb files of the requested accessions from the user.  Return the gb file names
def get_gb_files_from_GenBank(accession):

	Entrez.email = 'example@mail.com'
	files_made = False
	gb_file_name = ''

	# Create files to store genomes
	gb_file_name = accession + ".gb"

	try:
		# Fetch accession
		handle = Entrez.efetch(db='nucleotide', id=accession, rettype='gb')
		gb_file = open(gb_file_name, 'w')
		gb_file.write(handle.read())
		handle.close()
			
	except:
		#print('One or both of your files are wrong')
		sys.exit()
	
	return(gb_file_name)


# Parses the gb files that the user requested to extract the genome information
def parse_gb_files(gb_file, pure_accession):

	gb_file_list = []

	organism = ''
	accession = ''
	predicted_gene_count = 1
	number_of_genes = 0
	number_of_basepairs = 0
	gene_list = []
	iso_gene_list = []

	# Put files lines into list
	with open(gb_file) as f:
		for line in f:
			line = line.strip()
			gb_file_list.append(line)

	# Isolate variables and data from file
	for item in gb_file_list:
		if 'ORGANISM' in item:	# Organism
			organism = item[10:]
			
		if 'ACCESSION   ' in item:	# Accession
			accession = item[12:]
		
		if 'LOCUS' in item:	# Basepairs
			temp_substring = (item[30:item.find(' bp ')])
			for c in temp_substring:
				if c.isdigit():
					number_of_basepairs = int(temp_substring[temp_substring.index(c):])
					break
		
		if '/gene="' in item:	# List of genes and number of genes
			gene_list.append(item[item.index('/gene=')+7:len(item)-1])
		elif 'gene prediction' in item:
			gene_list.append('predicted gene ' + str(predicted_gene_count))
			predicted_gene_count += 1
			
	for i in gene_list:	# Take only 1 instance of each gene in gene_list
		if i not in iso_gene_list:
			iso_gene_list.append(i)
	number_of_genes = len(iso_gene_list)
						
	add_to_database(pure_accession, accession, organism, number_of_genes, number_of_basepairs, iso_gene_list)


# Add to database
def add_to_database(pure_accession, accession, organism, number_of_genes, number_of_basepairs, iso_gene_list):
	conn = mysql.connector.connect(user='nsarsou1', password='password', host='localhost', database='nsarsou1')
	cursor = conn.cursor()

	qry = """ INSERT INTO Accessions (Pure_Accession, Accession, Organism, Gene_Number, Basepair_Number)
		VALUES (%s,%s,%s,%s,%s) """	

	cursor.execute(qry, (pure_accession, accession, organism, number_of_genes, number_of_basepairs))

	for gene in iso_gene_list:
		qry = """INSERT INTO Genes VALUES (%s, %s) """
		cursor.execute(qry, (accession, gene))


	cursor.close()
	conn.close()


# Delete .gb files from directory
def delete_temp_files():
	filelist = glob.glob("*.gb")
	for f in filelist:
		os.remove(f)


def display_data(first_accession, second_accession):
	templateLoader = jinja2.FileSystemLoader( searchpath="./templates")
	env = jinja2.Environment(loader=templateLoader)
	template = env.get_template('search_gb.html')

	conn = mysql.connector.connect(user='nsarsou1', password='password', host='localhost', database='nsarsou1')
	cursor = conn.cursor()

	qry="""SELECT Accession, Organism, Gene_Number, Basepair_Number FROM Accessions"""
	cursor.execute(qry)
          
	for (table_accession, table_organism, table_gene_number, table_basepair_number) in cursor:
		table_accession_list.append(table_accession)
		table_organism_list.append(table_organism)
		table_gene_number_list.append(table_gene_number)	
		table_basepair_number_list.append(table_basepair_number)

	conn.close()

class Entry(object):
	pacc = ""
	acc = ""
	org = ""
	gn = ""
	bpn = ""

def make_entry(pacc, acc, org, gn, bpn):
	entry = Entry()
	entry.pacc = pacc
	entry.acc = acc
	entry.org = org
	entry.bpn = bpn
	entry.gn = gn

	return entry


my_entries = []
i = 0
length = len(table_accession_list)

while i < length:
	my_entries.append(make_entry(table_pure_accession_list[i], table_accession_list[i], table_organism_list[i], table_gene_number_list[i], table_basepair_number_list[i]))
	i += 1

# Second Table
qry = """ SELECT * FROM Genes ORDER BY Accession"""
cursor.execute(qry)

for (table_all_accessions, table_gene) in cursor:
	table_gene_list.append(table_gene)
	table_all_accessions_list.append(table_all_accessions)

conn.close()  


class Entry2(object):
	tg = ""
	taa = ""


def make_entry2(tg, taa):
	entry2 = Entry2()
	entry2.tg = tg
	entry2.taa = taa

	return entry2


my_entries2 = []
i = 0
length2 = len(table_all_accessions_list)

while i < length2:
        my_entries2.append(make_entry2(table_gene_list[i], table_all_accessions_list[i]))
        i += 1


print("Content-Type: text/html\n\n")
print(template.render(acc1 = first_accession, acc2 = second_accession, ents = my_entries, ents2 = my_entries2))


# Main method
if __name__ == "__main__":
	
	main()
