# -*- coding: utf-8 -*-
from os import listdir
from os.path import isfile, join
import shlex, subprocess,sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time as t
import csv
import sys

filetype=sys.argv[1]
args_str = "moss -l "+filetype

filepath=sys.argv[2]
files = [f for f in listdir(filepath+"/basecode") if isfile(join(filepath+"/basecode", f))]
for file in files:
    args_str=args_str+" -b "+filepath+"/basecode/"+file

files = [f for f in listdir(filepath) if isfile(join(filepath, f))]
for file in files:
    if(".java" in file):
		args_str=args_str+" "+filepath+"/"+file

args = shlex.split(args_str)
p = subprocess.Popen(args, stdout=subprocess.PIPE)
output=p.stdout.read()

print(output)
lines=output.split("\n")
r=requests.get(lines[-2])
content=r.content
content=content.replace("</A>","</a></td>")
content=content.replace("<TR>","</td></tr><tr>")

soup = BeautifulSoup(content, 'html.parser')

reports = []

for row in soup.find_all("tr"):
	report = []
	for cell in row.find_all("td"):
		text = str(cell.text)
		text = text.rstrip()
		newtext=text.split("/")
		text=newtext[len(newtext)-1]
		report.append(text)

	if len(report) != 0:
		reports.append(report)
	
row = soup.find_all("tr")
i=1
while i<len(row):
	req=requests.get(row[i].find("a").get("href").replace(".html","-top.html"))
	newcontent=req.content
	newcontent=newcontent.replace("<TR><TD>","</TR><TR><TD>")
	newcontent=newcontent.replace("</A>","</A></TD>")
	newcontent=newcontent.replace("</TABLE>","</TR></TABLE>")
	newSoup=BeautifulSoup(newcontent,'html.parser')
	links=newSoup.find_all("a")
	reports[i-1].append(str(links[0].text))
	reports[i-1].append(str(links[2].text))
	i=i+1

curr=datetime.now()
curr="./output/"+str(curr)+".csv"
print("Saving Results To "+curr)
with open(curr,'wb') as out:
	csv_out = csv.writer(out)
	csv_out.writerow(['File 1','File 2','# of Lines Matched','Lines in File 1 Matched','Lines in File 2 Matched'])
	for report in reports:
		csv_out.writerow(report)

print("Done")
