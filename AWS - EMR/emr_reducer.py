#!/usr/bin/env python

import sys
import re

title = None
# date_cnt = [date1, date2, ... date31, monthly_total]
date_cnt = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

for line in sys.stdin:

	line = line.strip()

	# extract the date of the title
	date = re.search('\d\d$', line).group()
	current_title, pageview = line.split('\t', 1)
	pageview = pageview[:len(pageview)-2]

	try:
		pageview = int(pageview)
		date     = int(date)
	except ValueError:
		print 'ValueError at "%s"\n' % line
		continue

	# NOTICE: Hadoop shuffles and sorts the <key, val> before sent to reducer
	if title == current_title:
		date_cnt[date-1] += pageview
		date_cnt[31]     += pageview
	# If it's the first time processing the title, build a list and update
	else:
		# print out the line if the title change (new title starts)
		if title:
			if int(date_cnt[31]) > 100000:
				print "%s\t%s\tdate1:%s\tdate2:%s\tdate3:%s\tdate4:%s\tdate5:%s\tdate6:%s\tdate7:%s\tdate8:%s\tdate9:%s\tdate10:%s\tdate11:%s\tdate12:%s\tdate13:%s\tdate14:%s\tdate15:%s\tdate16:%s\tdate17:%s\tdate18:%s\tdate19:%s\tdate20:%s\tdate21:%s\tdate22:%s\tdate23:%s\tdate24:%s\tdate25:%s\tdate26:%s\tdate27:%s\tdate28:%s\tdate29:%s\tdate30:%s\tdate31:%s" % (date_cnt[31], title, date_cnt[0], date_cnt[1], date_cnt[2], date_cnt[3], date_cnt[4], date_cnt[5], date_cnt[6], date_cnt[7], date_cnt[8], date_cnt[9], date_cnt[10], date_cnt[11], date_cnt[12], date_cnt[13], date_cnt[14], date_cnt[15], date_cnt[16], date_cnt[17], date_cnt[18], date_cnt[19], date_cnt[20], date_cnt[21], date_cnt[22], date_cnt[23], date_cnt[24], date_cnt[25], date_cnt[26], date_cnt[27], date_cnt[28], date_cnt[29], date_cnt[30])

		title = current_title
		# date_cnt = [date1, date2, ... date31, monthly_total]
		date_cnt = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
					0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
				    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		date_cnt[date-1] = pageview
		date_cnt[31]     = pageview

# print the last title in the input stream
if int(date_cnt[31]) > 100000:
	print "%s\t%s\tdate1:%s\tdate2:%s\tdate3:%s\tdate4:%s\tdate5:%s\tdate6:%s\tdate7:%s\tdate8:%s\tdate9:%s\tdate10:%s\tdate11:%s\tdate12:%s\tdate13:%s\tdate14:%s\tdate15:%s\tdate16:%s\tdate17:%s\tdate18:%s\tdate19:%s\tdate20:%s\tdate21:%s\tdate22:%s\tdate23:%s\tdate24:%s\tdate25:%s\tdate26:%s\tdate27:%s\tdate28:%s\tdate29:%s\tdate30:%s\tdate31:%s" % (date_cnt[31], title, date_cnt[0], date_cnt[1], date_cnt[2], date_cnt[3], date_cnt[4], date_cnt[5], date_cnt[6], date_cnt[7], date_cnt[8], date_cnt[9], date_cnt[10], date_cnt[11], date_cnt[12], date_cnt[13], date_cnt[14], date_cnt[15], date_cnt[16], date_cnt[17], date_cnt[18], date_cnt[19], date_cnt[20], date_cnt[21], date_cnt[22], date_cnt[23], date_cnt[24], date_cnt[25], date_cnt[26], date_cnt[27], date_cnt[28], date_cnt[29], date_cnt[30])

