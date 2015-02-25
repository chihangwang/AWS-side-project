#!/usr/bin/python
import boto
from boto.ec2.cloudwatch import CloudWatchConnection
import mysql.connector
import datetime
import time

AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''

def return_mysql_metrics():
    metrics = {}
    cnx = mysql.connector.connect(user='sysbench', password='project3')
    cursor = cnx.cursor()

    query1  = ("show status like 'Queries'")
    query2  = ("show status like 'Uptime'")

    cursor.execute(query1)
    for (Variable_name, Value) in cursor:
        metrics['query'] = int(Value)

    cursor.execute(query2)
    for (Variable_name, Value) in cursor:
        metrics['time'] = int(Value)

    cursor.close()
    cnx.close()
    return metrics

def enable_cloud_watch():
    instance_id = boto.utils.get_instance_metadata()['instance-id']
    conn = CloudWatchConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)

    while (1):
        time.sleep(55)
        timestamp = datetime.datetime.now()
        metric1 = return_mysql_metrics()
        time.sleep(5)
        metric2 = return_mysql_metrics()

        mysql_tps = (float(abs(metric1['query'] - metric2['query'])) / float(metric2['time'] - metric1['time'])) / float(16)
        tps_percent = float(mysql_tps / 130) * 100
        conn.put_metric_data('TPS_namespace', 'TPS_utilization', tps_percent, timestamp, 'Percent', {'InstanceID': instance_id})

if __name__ == '__main__':
    enable_cloud_watch()