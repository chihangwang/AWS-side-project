"""
	AndrewID: chihangw
	Command:  Put this script and pagecounts dataset in the same folder.
			  Enter 'python sequential_analysis.py [arg1]' to run the script.
			  The final result will be in the file 'filter_f' ! 
"""

import re
import sys

def predicate(output):
	match = re.search('\d*$', output)
	pview_cnt = int(match.group())
	return pview_cnt

def main():

	pagecnt_f = open(sys.argv[1], "rU")
	filter_f = open("filter_f", "w")

	output_list = []

	for line in pagecnt_f:

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

		output = "%s\t%s\n" % (title, pview_cnt)
		output_list.append(output)
		
	sorted_list = sorted(output_list, key=predicate)

	for out in sorted_list:
		filter_f.write(out)

	pagecnt_f.close()
	filter_f.close()

if __name__ == '__main__':
	main()