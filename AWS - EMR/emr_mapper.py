#!/usr/bin/env python

import sys
import re
import os

file_path = os.environ["mapreduce_map_input_file"]
file_name = os.path.split(file_path)[-1]
date = file_name[17:19]

for line in sys.stdin:

	# exclude matched title in requirement #1
	if line.startswith('en ') == False:
		continue

	title = line.split(' ')[1]
	pview_cnt = line.split(' ')[2]

	# exclude matched title in requirement #3
	if re.match('[a-z]', title):
		continue

	# exclude matched title in requirement #2
	if re.match('(Media|Special|Talk|User|User_talk|Project|Project_talk\
			   |File|File_talk|MediaWiki|MediaWiki_talk|Template):', title):
		continue

	if re.match('(Template_talk|Help|Help_talk|Category|Category_talk\
				 |Portal|Wikipedia|Wikipedia_talk)', title):
		continue

	# exclude matched title in requirement #4
	if re.search('.*\.(jpg|gif|png|JPG|GIF|PNG|txt|ico)$', title):
		continue

	# exclude matched title in requirement #5
	boiler_plate = set(['404_error', 'Main_Page',\
		                'Hypertext_Transfer_Protocol', 'Search'])
	
	if title in boiler_plate:
		continue

	print "%s\t%s%s" % (title, pview_cnt, date)
		