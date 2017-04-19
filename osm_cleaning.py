import re
import xml.etree.cElementTree as ET
import pprint
import codecs
import json


bengaluru_sample = "bengaluru_india_sample.osm"
bengaluru = "bengaluru_india.osm"

#################################################################

## S T R E E T  ## D A T A ## C L E A N E D ##

street_name_mapping = {" Rd": " Road",
			" Raod": " Road",
			" road": " Road",
			" Nagara": " Nagar",
			" cross": " Cross",
			" Belandur,": " Bellandur",
			" belandur,": " Bellandur",
			" block": " Block",
			" Jayanagara": " Jayanagar",
			" layout": " Layout",
			" Mahadevapura": " Mahadevpura",
			" main": " Main",
			" Sadashivnagara": " Sadashivnagar",
			" street": " Street",
			",,": ",",
			"\"": "",
			"Banerghatta": "Bannerghatta",
			"feet": "Feet",
			"Pilla": "Pillar",
			"( S K Karim": " (Karim",
			"(S K Karim": " (Karim",
			";": " or ",
			"ft": " Feet",
			"  ": " "
			}

def is_street_name(tag_element):
	return (tag_element.attrib["k"] == "addr:street")

def update_street_name(street_name, street_name_mapping):
	for key in street_name_mapping:
		if key in street_name:
			street_name = street_name.replace(key, street_name_mapping[key])
	street_name = street_name.rstrip(",")
	if type(street_name) != type("string"):
		street_name = street_name.encode("utf8")
	return street_name

def test_street_name_update():
	new_street_name_list = [] 
	for event, element in ET.iterparse(bengaluru, events = ("start",)):
		if element.tag in ["way", "node", "relation"]:
			for tag_element in element.iter("tag"):
				if is_street_name(tag_element):
					street_name = tag_element.attrib["v"]
					better_street_name = update_street_name(street_name, street_name_mapping)
					new_street_name_list.append(better_street_name)
	#pprint.pprint(new_street_name_list)
	print len(new_street_name_list)

#test_street_name_update()

#######################################################################

## L E V E L ## D A T A ## C L E A N E D ##

def is_level(tag_element):
	return (tag_element.attrib["k"] == "level")

def update_level(level):
	if "," in level:
		level = level[0] + ";" + level[-1]
	return level

def test_update_level():
	updated_level_list = []
	for event, element in ET.iterparse(bengaluru, events = ("start",)):
		if element.tag in ["way", "node"]:
			for tag_element in element.iter("tag"):
				if is_level(tag_element):
					level = tag_element.attrib["v"]
					better_level = update_level(level)
					updated_level_list.append(better_level)
	#pprint.pprint(updated_level_list)
	print len(updated_level_list)

#test_update_level()

##################################################################

## N A M E ## D A T A ## C L E A N E D ##

def is_name(tag_element):
	return (tag_element.attrib["k"] == "name")

name_mapping = {"Wolrd Of Titan": "World of Titan",
                "Titan Eye +": "Titan Eye+",
                "Sweet Chariot": "Sweet Chariot Cafe",
                "State ATM": "State Bank ATM",
                "State Bank Of India": "State Bank of India",
                "State Bank of India, Yemalur": "State Bank of India",
                "Shell Petrol Bank": "Shell Petrol Bunk",
                "Shell Petrol Pump": "Shell Petrol Bunk",
                "uco Bank": "UCO Bank"}

def update_name(name, name_mapping):
	if name in name_mapping:
		name = name_mapping[name]
	if type(name) != type("string"):
		name = name.encode("utf8")
	return name

def test_update_name():
	new_name_list = []
	for event, element in ET.iterparse(bengaluru, events = ("start",)):
		if element.tag in ["way", "node"]:
			for tag_element in element.iter("tag"):
				if is_name(tag_element):
					name = tag_element.attrib["v"]
					better_name = update_name(name, name_mapping)
					new_name_list.append(better_name)
	#pprint.pprint(new_name_list)
	print len(new_name_list)

#test_update_name()

###################################################################

## S H A P E ## E L E M E N T ##

CREATED = ["version", "changeset", "uid", "timestamp", "user"]

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def shape_element(element):
	new_element = {}
	if element.tag in ["way", "node"]:
		new_element["created"] = {}
		for k , v in element.attrib.items():    #top level attributes
			if k in CREATED:
				new_element["created"][k] = v
			elif k in ["lat", "lon"]:
				if "pos" not in new_element:
					new_element["pos"] = []
				new_element["pos"].append(float(v))
				if k == "lat" and len(new_element["pos"]) == 2:
					pos = new_element["pos"]
					new_element["pos"] = []
					for i in [1, 0]:
						new_element["pos"].append(pos[i])
			else:
				new_element[k] = v
			for tag_element in element.iter("tag"):    #tag element attributes
				if "k" in tag_element.attrib.keys():
					k = tag_element.attrib["k"]
					v = tag_element.attrib["v"]
					if problemchars.search(k):
						pass
					elif k.startswith("addr:"):
						stripped = k.lstrip("addr:")
						if ":" not in stripped:
							if "address" not in new_element or type(new_element["address"] != type({})):
								new_element["address"] = {}
							if is_street_name(tag_element):      #cleaning street names
								v = update_street_name(v, street_name_mapping)
							new_element["address"][stripped] = v
						else:
							pass
					elif k.find("addr:") != 0 and ":" in k:
						left_part = k.split(":")[0]
						right_part = k.split(":")[1]
						if left_part not in new_element:
							new_element[left_part] = {}																
							new_element[left_part][right_part] = tag_element.attrib["v"]
					else:
						if is_name(tag_element):     #cleaning name fields
							v = update_name(v, name_mapping)
						elif is_level(tag_element):  #cleaning level field
							v = update_level(v)
						new_element[k] = v
			if element.tag == "way":
				new_element["type"] = "way"
				for nd_element in element.iter("nd"):
					if "ref" in nd_element.attrib.keys():
						if "node_refs" not in new_element:
							new_element["node_refs"] = []
						new_element["node_refs"].append(nd_element.attrib["ref"])
			elif element.tag == "node":
				new_element["type"] = "node"
	return new_element

def test_shape_element(filename):
	element_list = []
	for event, element in ET.iterparse(filename, events = ("start",)):
		if element.tag in ["way", "node"]:
			new_element = shape_element(element)
			element_list.append(new_element)
	return element_list

#bengaluru_list = test_shape_element(bengaluru_sample)
#print len(bengaluru_list)

###########################################################################################
 
 ## P R O C E S S I N G ## M A P ## & ##
 ## W R I T I N G ## J S O N ## F I L E ##

def process_map(file_in, pretty = False):
	file_out = "{0}.json".format(file_in)
	data = []
	with codecs.open(file_out, "w") as fo:
		for _, element in ET.iterparse(file_in):
			if element.tag in ["way", "node"]:
				el = shape_element(element)
				if el:
					data.append(el)
					if pretty:
						fo.write(json.dumps(el, indent = 2) + "\n")
					else:
						fo.write(json.dumps(el) + "\n")
	return data

#process_map(bengaluru, False)

