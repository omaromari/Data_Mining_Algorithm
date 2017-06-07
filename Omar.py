import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import csv
import json
import sys, getopt, pprint
#from pymongo import MongoClient
import re
import requests
from tinydb import TinyDB, where
from tinyrecord import transaction

#1.) Starting with just one PMCID for now

with open('pmcids.txt') as f:
	lines = f.readlines()
#print lines[0]
html_id = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=" + str(lines[0]) #First article
req = requests.get(html_id)
plain_text = req.text

#2.) Use BeautifulSoup module to get article

soup = BeautifulSoup(plain_text, "lxml") #Gets and stores article in variable "soup"

#3.) Search article for total number of figures

figures = soup.find_all("fig")
N = len(figures)
#print N

#4.) Initiate loop to cycle through all figures

ind = 1
count = 0
URL = []
Word = []
Word_data = []
Word_data.append([])
Word_Count = []
Word_Count.append([])
for i in range(1,N+1):
	#print i
	fig = soup.find(id = "fig"+str(i))#figures.find_all(id = "fig"+str(i))
	#print fig
	fig = str(fig)
	Caption = fig.split("<bold>")[1]
	Caption = Caption.split(".</bold>")[0]
	#print Caption
	Caption = Caption.split()
	#print Caption

	Body = fig.split("</bold>")[1]
	#print Body
	Body = Body.split(".</p>")[0]
	Body = Body.split()
	#print Body
	
	HREF = fig.find("xlink:href")
	URL.append( "http://www.w3.org/1999/xlink" + "/xref:href=" + str(HREF))
	#print URL
	#5.) Run Co-occurrence algorithm
	for j in Caption:
		for k in Body:
			if j == k:
				count = count + 1
				Word = j
		Word_data[i-1].append(Word)#[ind] = Word
		Word_Count[i-1].append(count)#[ind] = count
		Word_data.append([])
		Word_Count.append([])		
		count = 0
		ind = ind + 1

#6.)Store data in .CSV and .JSON files using pandas and numpy modules
#Filter-out empty indices in Word_data and Word_Count
Word_data = filter(None, Word_data)
#print (Word_data)
Word_Count = filter(None, Word_Count)
#print (Word_Count)
#print (URL)
dataframe = pd.DataFrame({"URL": URL, "Word": Word_data, "Count": Word_Count})
dataframe.to_csv("Test_1.csv", index = False)

#Store CSV data in JSON file

csvfile = open('Test_1.csv','r')
jsonfile = open('Test_1.json','w')

fieldnames = ("URL","Word","Count")
reader = csv.DictReader(csvfile, fieldnames)
for row in reader:
	json.dump(row, jsonfile)
	jsonfile.write('\n')

#7.) Load data in NOSQL database

#mongo_client = MongoClient()
#db = mongo_client.october_mug_talk
#db.segment_drop()
#header = ["URL","Word","Count"]
#for each in reader:
#	row = {}
#	for field in header:
#		row[field] = each[field]
#	db.segment.insert(row)

table = TinyDB('db.json').table('table')
with transaction(table) as tr:
	tr.insert({"URL": URL, "Word": Word_data, "Count": Word_Count})
    	# delete records
    	tr.remove(where('invalid') == True)
    	# update using a function
    	#tr.update_callable(updater, where(...))
    	# insert many items
    	#tr.insert_multiple(documents)

#8.) Upload data to a webpage

url = 'https://sites.google.com/site/voicerecognitionresult/'#'https://sites.google.com/view/omar-alg-test-1/home/'#'http://test_1.com'
#Use "dataframe" variable from step 6 as input to "data" variable
jsonfile = open('Test_1.json','r')
res = requests.post(url, data=jsonfile)#dataframe)
print(res.text)
