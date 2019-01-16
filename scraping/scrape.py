import urllib2
from bs4 import BeautifulSoup
import time
import os
import json

if not os.path.exists("./company"):
	os.makedirs("./company")
if not os.path.exists("./phones"):
	os.makedirs("./phones")

base_page = "https://www.gsmarena.com/"
all_companies_page = base_page + "makers.php3"

# Phone companies
companies_link = []
with open('company_links.txt', 'a+') as f:
	# I already have file open at this point.. now what?
	f.seek(0) #ensure you're at the start of the file..
	first_char = f.read(1) #get the first character
	print "Checking if file is empty..." + os.path.basename(f.name)
	if not first_char:
		print "file is empty" #first character is the empty string..	
		print "-"*35
		print "Getting the companies link from the web..."
		page = urllib2.urlopen(all_companies_page) #use file now
		soup = BeautifulSoup(page, 'html.parser')
		companies_div = soup.find('div', attrs={'class': 'st-text'})
		companies_anchor_tags = companies_div.findAll('a') 
		for a in companies_anchor_tags:
			companies_link.append(a['href'])
		print ""
		for item in companies_link:
			print >> f, item
	else:
		f.seek(0)
		print "Getting the links from the file..."
		companies_link = f.read().splitlines()
		print "Total companies: ", len(companies_link)

total_phones=0
for company_link in companies_link:
	current_company_name = company_link.split("-")[0]
	print "Company: " +  current_company_name
	with open("./company/"+current_company_name+".txt", 'a+') as f:
		phones_link=[]
		# I already have file open at this point.. now what?
		f.seek(0) #ensure you're at the start of the file..
		first_char = f.read(1) #get the first character
		print "Checking if file is empty..." + os.path.basename(f.name)
		if not first_char:
			print "file is empty" #first character is the empty string..	
			print "-"*35
			print "Getting the phones link from the web..."
			page = urllib2.urlopen(base_page + company_link)
			soup = BeautifulSoup(page, 'html.parser')
			phones_div = soup.find('div', attrs={'class': 'makers'})
			phones_anchor_tag = phones_div.findAll('a')
			for a in phones_anchor_tag:
				phones_link.append(a['href'])
			print "-"*35
			for item in phones_link:
				print >> f, item
			time.sleep(10)
		else:
			f.seek(0)
			print "Getting the phones from the file..."
			print ""
			phones_link = f.read().splitlines()
			total_phones += len(phones_link)
print "Got the list of phones of every comapny. Total number of phones to get data for: ", total_phones

companies_with_phones_link = []
all_the_txt_files = os.listdir(os.getcwd()+"/company")

for file in all_the_txt_files:
	if( file.endswith(".txt") and (file != "company_links.txt")):
		companies_with_phones_link.append(file)

i=0
for company in companies_with_phones_link:
	with open("./company/" + company, 'a+') as f:
		phones_link=[]
		# I already have file open at this point.. now what?
		f.seek(0) #ensure you're at the start of the file..
		phones_link = f.read().splitlines()
		for phone in phones_link:
			try:
				if os.path.isfile("./phones/"+phone.split("-")[0]+".json"):
					print "Data already exists for phone: ", phone.split("-")[0]
				else:
					phone_info={}
					if(i%4 == 0):
						time.sleep(10)
						i=0
					i = i+1	
					phone_info = {"Company": company.split(".")[0], "Model": phone.split("-")[0], "Name": phone.split("-")[0].replace('_',' ').title()}
					page = urllib2.urlopen(base_page + phone)
					soup = BeautifulSoup(page, 'html.parser')
					for table in soup.findAll("table"):
						header = table.th.get_text()
						for row in table.findAll("tr"):
							td = {}
							out_row = [ header ]
							if(len(row.findAll("td")) > 0) :
								td[row.findAll("td")[0].get_text()] = row.findAll("td")[1].get_text()
							try:
								temp = phone_info[header]
								temp.update(td)
								phone_info[header] = temp
							except KeyError:
								phone_info[header] = td
					print >> open("./phones/"+phone.split("-")[0]+".json", 'a+'), json.dumps(phone_info)
					print "Collected data for phone: , ", phone.split("-")[0]
			except Exception as inst:
				print("@")*50
				print type(inst)    # the exception instance
				print inst.args     # arguments stored in .args
				print inst   
				print "Failed phone ", phone, " of company ", company
print "Stored/Fetched all the phones of every company available."