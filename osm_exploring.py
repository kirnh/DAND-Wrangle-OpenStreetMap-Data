import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict


bengaluru = "bengaluru_india.osm"
bengaluru_sample = "bengaluru_india_sample.osm"

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)

expected_street = ["Road", "Avenue", "Cross", "Post", "Street", "Nagar", "Veedhi", "Stage", "Phase", "Main", "Circle"]

def audit(street_names, expected_street):
	unexpected = defaultdict(set)
	for i in street_names:
		m = street_type_re.search(i)
		if m:
			street_type = m.group()
			if street_type not in expected_street:
				unexpected[street_type].add(i)
	return unexpected

def pretty_print_default_dict(d):
	d = dict(d)
	keys = d.keys()
	keys = sorted(keys, key = lambda s: s.lower())
	for k in keys:
		v = d[k]
		print "%s: %d" %(k, v)


def get_street_name_list(filename, name = "all"):
	if name == "all":
		street_name_list = defaultdict(int)
		for event, element in ET.iterparse(filename, events = ("start",)):
			if element.tag in ["node"]:
				for tag in element.iter("tag"):
					if tag.attrib["k"] == "addr:street":
						m = street_type_re.search(tag.attrib["v"])
						if m:
							street_name_type = m.group()
							street_name_list[street_name_type] += 1
		return street_name_list
	else:
		street_name_list = []
		for event, element in ET.iterparse(filename, events = ("start",)):
			if element.tag == "node":
				for tag in element.iter("tag"):
					if tag.attrib["k"] == "addr:street" and tag.attrib["v"].endswith(name):
						street_name_list.append(tag.attrib["v"])
		return street_name_list

def print_street_name_type_details(filename, street_name_type):
	street_name_type_details = get_street_name_list(filename, name = street_name_type)
	for i in street_name_type_details:
		print i

def print_street_name_type_list(filename):
	street_name_type_list = get_street_name_list(filename, name = "all")
	for k, v in street_name_type_list.items():
		print k, v

#street_list = get_street_name_list(bengaluru)
#print (audit(street_list, expected_street))
#print "\n"
#pretty_print_default_dict(street_list)
#print "\n"
#print_street_name_type_details(bengaluru, "Road)")
#print "\n"
#print_street_name_type_details(bengaluru, "Malleshwaram")

def get_elements_by_k_and_v(filename, k, v = "", only_tag_element = False):
	element_list = []
	for event, element in ET.iterparse(filename, events = ("start",)):
		if element.tag in ["node", "way"]:
			elem = []
			for tag in element.iter():
				elem.append(tag.attrib)
			for i in elem:
				try:
					if i["k"] == k and i["v"].endswith(v):
						if only_tag_element:
							element_list.append(i["v"])
						else:
							element_list.append(elem)
				except KeyError:
					pass
	return element_list

#street_names = get_elements_by_k_and_v(bengaluru, "addr:street", v = "", only_tag_element = False)
#pprint.pprint(street_names)
#print len(street_names) 

def group_by_k(filename, k):
	elements_list = (get_elements_by_k_and_v(bengaluru, k, v = "", only_tag_element = True))
	grouped = defaultdict(int)
	for k in elements_list:
		if grouped[k]:
			grouped[k] += 1
		else:
			grouped[k] = 1
	return grouped

#grouped_by_opening_hours = group_by_k(bengaluru, "opening_hours")
#pretty_print_default_dict(grouped_by_opening_hours)


def get_unique_users(filename):
	users = set()
	for event, element in ET.iterparse(filename, events = ("start",)):
		if element.tag in ["way", "node", "relation"]:
			users.add(element.get("uid"))
	return users


def count_all_k_tags(filename):
	k_count = {}
	for event, element in ET.iterparse(filename, events = ("start",)):
		if element.tag in ["way", "node", "relation"]:
			for tag in element.iter("tag"):
				k = tag.attrib["k"]
				if k in k_count:
					k_count[k] += 1
				else:
					k_count[k] = 1
	return k_count

#pprint.pprint(count_all_k_tags(bengaluru))

def count_all_document_by_type(filename, doc_type):
	count = 0
	for _, element in ET.iterparse(filename, events = ("start",)):
		if element.tag in doc_type:
			count += 1
	print count

#count_all_document_by_type(bengaluru, ["way"])






