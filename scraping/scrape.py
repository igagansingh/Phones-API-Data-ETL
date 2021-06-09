import urllib2
from urllib2 import HTTPError
from bs4 import BeautifulSoup
import time
import os
import json
import re

flag=True
# Global variables
base_page = "https://www.gsmarena.com/"
all_companies_page = base_page + "makers.php3"


# Convert to camelCase
def convert_to_camel_case(s):
	s=s.strip()
	ans=""
	if ' ' in s:
		arr = s.split(' ')
		for i in range(0, len(arr)):
			if i!=0:	ans = ans + arr[i].capitalize()
			else: ans = ans + arr[i]
		return ans
	return s

# Some keys are like '2g bands', '3g bands'
# To represent them as field in java convert to 'bands2g', 'bands3g'
def bands_fix(s):
	if 'bands' in s:
		return 'bands' + s.replace('bands', '').strip()

# Get list of companies
def load_companies():
	global flag
	flag = False
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
						time.sleep(2)
						# basic information
						phone_info = {"company": company.split(".")[0].capitalize(), "model": phone.split("-")[0], "name": phone.split("-")[0].replace('_',' ').title()}
						
						# images
						phone_info["images"]=[]
						image_url=re.sub("\\d+.php", "pictures-" + re.search("\\d+.php", phone).group(0), phone)
						try:
							page = urllib2.urlopen(base_page + image_url)
							soup = BeautifulSoup(page, 'html.parser')
							images = []
							images_div = soup.find(id="pictures-list").findAll("img")
							for image in images_div:
								if image.has_attr("src"):
									images.append({"info": image["alt"], "src": image["src"]})
							phone_info["images"]=images
						except Exception as inst:
							if type(inst) == HTTPError:
								raise inst
							print("No images found for phone: " + phone_info["model"]+"\n\n")

						# other information
						page = urllib2.urlopen(base_page + phone)
						soup = BeautifulSoup(page, 'html.parser')
						for table in soup.findAll("table"):
							if table.th!=None:
								header = table.th.get_text().lower()
								for row in table.findAll("tr"):
									td = {}
									if(len(row.findAll("td")) > 0) :
										key = row.findAll("td")[0].get_text().lower()
										# Special case
										# 1. If the key is only space
										if len(key.strip())==0:
											td['misc'] = row.findAll("td")[1].get_text()
										# 2. If key contains camera add to a specific 'camera' key
										elif 'camera' in key and len(key.replace('camera', '').strip()) > 0:
											phone['camera'].update({key.replace('camera', '').strip():row.findAll("td")[1].get_text()})
										# 3. If contains xg bands convert to bandsXg
										elif 'bands' in key:
											td[bands_fix(key)] = row.findAll("td")[1].get_text()
										# 4. "3.5mmJack" -> "jack"
										elif '3.5mm' in key:
											dummyKey = convert_to_camel_case(key.replace('3.5mm', ''))
											td[dummyKey] = row.findAll("td")[1].get_text()
										# 5. If space in between convert to camelCase
										else:
											key = convert_to_camel_case(key)
											td[key] = row.findAll("td")[1].get_text()
									try:
										if 'camera' in header:
											dummyKey = header.replace('camera', '').strip()
											if 'camera' not in phone_info:
												phone_info['camera'] = {}

											if dummyKey not in phone_info['camera']:
												phone_info['camera'].update({dummyKey : td})
											else:
												phone_info['camera'][dummyKey].update(td)
										else:
											if header not in phone_info:
												phone_info = {header : {}}
											phone_info[header].update(td)
									except KeyError as e:
										# print type(e)    # the exception instance
										# print e.args     # arguments stored in .args
										# print e
										phone_info[header] = td
										raise e
						print >> open("./phones/"+phone.split("-")[0]+".json", 'a+'), json.dumps(phone_info)
						print "Collected data for phone: ", phone.split("-")[0]
				except Exception as inst:
					if type(inst) == HTTPError:
						raise inst
					print("<>")*50
					print type(inst)    # the exception instance
					print inst.args     # arguments stored in .args
					print inst
					print "Failed phone ", phone, " of company ", company
					print >> open("./failed.txt", 'a+'), base_page + phone

	print "Stored/Fetched all the phones of every company available."

if __name__== "__main__" :
	if not os.path.exists("./company"):
		os.makedirs("./company")
	if not os.path.exists("./phones"):
		os.makedirs("./phones")

	while flag:
		try:
			load_companies()
		except HTTPError as err:
			if err.code == 429:
				flag = True
				print("Experiencing delay, trying after 5 minutes")
				time.sleep(330)
				print("Starting...")
		except Exception as e:
			print("Other exception")
