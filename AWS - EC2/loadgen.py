"""
Student Name: Chih-Ang Wang
AndrewID: chihangw

Authenticate (You need to do this every time you boot any instance in this project): 
	
	http://<your-instance-dns-name>/username?username=<yourandrewid>
------------------------------------------------------------------------------------
Activate the load generator:

	http://<your-load-generator-instance-dns-name>/part/one/i/want/more?
		dns=ec2-54-165-107-16.compute.amazonaws.com&testId=Pizza
------------------------------------------------------------------------------------
To view average rps "Every Minute": <check every 2 minuts to meet the requirement!!!>

	http://<your-load-generator-instance-dns-name>/view-logs?
		name=result_<yourusername>_<testid>.txt
------------------------------------------------------------------------------------

Goal: all instances in the data center to handle an aggregate of 3600 requests per second.
"""

import urllib
import urllib2
import sys
import re
import time
import boto.ec2

AWSAccessKeyId = "ENTER YOURS!!!"
AWSSecretKey   = "ENTER YOURS!!!"
MACHINE_TYPE   = "m3.medium"
LOAD_GEN_AMI   = "ami-1810b270"
DATA_CEN_AMI   = "ami-324ae85a"
SECURITY_GRP   = "Project2.1"
ACCESS_KEY     = "chihangw"
TESTID         = "iwantplay"

data_center_cnt = 0

def create_DataCenter(): 
	# create a instance for data center
	reservation = conn.run_instances(DATA_CEN_AMI, placement='us-east-1a',\
				  key_name=ACCESS_KEY, instance_type=MACHINE_TYPE,\
				  security_groups=[SECURITY_GRP])
	# update the number of existed data centers
	global data_center_cnt
	data_center_cnt += 1
	# get the data center instance id
	instance = reservation.instances[0]
	instance_id = instance.id
	print "Data Center Instance ID: %s" % instance_id
	# tag the instance after created
	conn.create_tags(instance_id, {"Project": "2.1"}, dry_run=False)
	# retrieve the dns for certain instance
	while True:
		reservs = conn.get_all_instances(instance_ids= [instance_id])
		inst = reservs[0].instances[0]
		dns = inst.public_dns_name
		if dns:
			break
		time.sleep(5)
	print "Data Center[%s] DNS: %s" % (instance_id, dns)
	# authenticate the instance with AndrewID:
	# http://<your-instance-dns-name>/username?username=<yourandrewid>
	data = {'username': 'chihangw'}
	params = urllib.urlencode(data)
	url = "http://" + dns + "/username?" + params
	# print "url: %s" % url
	while True:
		try:
			time.sleep(5)
			req = urllib2.Request(url)
			response = urllib2.urlopen(req)
			print "data center authenticate successfully"
			response.close()
			break
		except urllib2.URLError:
			continue
	return dns

def create_LoadGenerator():
	# create a instance for load generator
	reservation = conn.run_instances(LOAD_GEN_AMI, placement='us-east-1a',\
				  key_name=ACCESS_KEY, instance_type=MACHINE_TYPE,\
				  security_groups=[SECURITY_GRP])
	instance = reservation.instances[0]
	instance_id = instance.id
	print "Load Generator Instance ID: %s" % instance_id
	# tag the instance after created
	conn.create_tags(instance_id, {"Project": "2.1"}, dry_run=False)
	# retrieve the dns for certain instance
	while True:
		reservs = conn.get_all_instances(instance_ids= [instance_id])
		inst = reservs[0].instances[0]
		dns = inst.public_dns_name
		if dns:
			break
		time.sleep(5)
	print "Load Generator[%s] DNS: %s" % (instance_id, dns)
	# authenticate the instance with AndrewID:
	# http://<your-instance-dns-name>/username?username=<yourandrewid>
	data = {'username': 'chihangw'}
	params = urllib.urlencode(data)
	url = "http://" + dns + "/username?" + params
	while True:
		try:
			time.sleep(5)
			req = urllib2.Request(url)
			response = urllib2.urlopen(req)
			print "load generator authenticate successfully"
			response.close()
			break
		except urllib2.URLError:
			continue
	return dns

def activate_LoadGenerator(load_dns, data_dns):
	# activate the data center by sending request to:
	# http://<your-load-generator-instance-dns-name>/part/one/i/want/more?
	# dns=ec2-54-165-107-16.compute.amazonaws.com&testId=Pizza
	url = "http://" + load_dns + "/part/one/i/want/more?" +\
		  "dns=" + data_dns + "&testId=" + TESTID
	req = urllib2.Request(url)
	while True:
		try:
			time.sleep(5)
			response = urllib2.urlopen(req)
			print "activate Data Center DNS[%s] successfully" % data_dns
			response.close()
			break
		except urllib2.URLError:
			continue

def get_rps(load_dns):
	# get Response Per Second (rps) by sending request to:
	# http://<your-load-generator-instance-dns-name>/view-logs?
	# name=result_<yourusername>_<testid>.txt
	url = "http://" + load_dns + "/view-logs?name=result_chihangw_iwantplay.txt" 
	res = urllib2.urlopen(url)
	report_txt = res.read().decode('utf-8')
	print "printing rps report ..........................."
	print report_txt
	rps_records = report_txt.split('\n')
	rps_length  = len(rps_records)

	global data_center_cnt
	print "Data Center #: %d" % data_center_cnt
	aggregate_rps = 0.0
	for i in range(data_center_cnt):
		rps = rps_records[rps_length-3-i]
		print "rps: %s" % rps
		match = re.search("\d*\.\d\d*", rps)
		if match:
			print match.group()
			aggregate_rps += float(match.group())
		else:
			print "no match"
	print "aggregate_rps: %.2f" % aggregate_rps
	return aggregate_rps

# PROGRAM BEGINS HERE 
# ============================================================================
# establish the connection with EC2
conn = boto.ec2.connect_to_region("us-east-1", aws_access_key_id=AWSAccessKeyId,\
								  aws_secret_access_key=AWSSecretKey)
data_dns = create_DataCenter()
load_dns = create_LoadGenerator()
activate_LoadGenerator(load_dns, data_dns)
while True:
	print "sleep........."
	time.sleep(100)
	print "wake.........."
	aggregate_rps = get_rps(load_dns)
	if aggregate_rps < 3600:
		data_dns = create_DataCenter()
		activate_LoadGenerator(load_dns, data_dns)
	else
		break

# RESULT: YOU HAVE REACHED THE GOAL SUCCESSFULLY IN 13 MINUTES. PLEASE ENTER THE FOLLOWING CERTIFICATION CODE TO OLI
# 6a58451ef671



