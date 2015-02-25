"""
    Name: Chih-Ang Wang
    AndrewID: chihangw
    Project 2.3
"""
import urllib
import urllib2
import time
import boto.ec2
import boto.ec2.elb
import boto.ec2.cloudwatch
import boto.ec2.autoscale
from boto.ec2.elb import HealthCheck
from boto.ec2.elb import ELBConnection
from boto.ec2.autoscale  import LaunchConfiguration
from boto.ec2.autoscale  import AutoScalingGroup
from boto.ec2.autoscale  import AutoScaleConnection
from boto.ec2.cloudwatch import CloudWatchConnection
from boto.ec2.cloudwatch import MetricAlarm
from boto.ec2.autoscale  import ScalingPolicy
from boto.ec2.autoscale  import Tag

AWSAccessKeyId = ""
AWSSecretKey   = ""
MACHINE_TYPE   = "m3.medium"
LOAD_GEN_AMI   = "ami-7aba0c12"
DATA_CEN_AMI   = "ami-3c8f3a54"
SECURITY_GRP   = "HTTP_ENABLED"
ACCESS_KEY     = "chihangw"
TESTID         = "iwantplay"
ARN_topic      = "arn:aws:sns:us-east-1:900670946900:PROJECT2-3"
MAX_SIZE       = 4
MIN_SIZE       = 3

ag = None
lc = None
elb = None

def create_LoadBalancer():
    print "Creating ELB..."
    elb_conn = ELBConnection(AWSAccessKeyId, AWSSecretKey)
    zones = ['us-east-1a']
    ports = [(80, 80, 'http')]
    hc = HealthCheck(
        interval=10,
        timeout = 7,
        healthy_threshold=2,
        unhealthy_threshold=3,
        target='HTTP:80/heartbeat?username=chihangw'
    )
    global elb
    elb = elb_conn.create_load_balancer(name='myELB',
                                        zones=zones,
                                        listeners=ports)
    elb.configure_health_check(hc)
    ELB_DNS = elb.dns_name
    print "ELB created successfully"
    print "ELB DNS: %s" % ELB_DNS
    return ELB_DNS

def create_AutoScaling():
    print "Creating AutoScaling..."
    # establish connection
    as_conn = AutoScaleConnection(AWSAccessKeyId, AWSSecretKey)
    # create launch configuration
    global lc
    lc = LaunchConfiguration(name='lc', image_id=DATA_CEN_AMI,
                             key_name=ACCESS_KEY, instance_monitoring=True,
                             security_groups=[SECURITY_GRP],
                             instance_type=MACHINE_TYPE)
    as_conn.create_launch_configuration(lc)

    # create tag for autoscaling group
    as_tag = Tag(key="Project",
                 value="2.3",
                 propagate_at_launch=True,
                 resource_id='my_group')

    # create aotoscaling group
    global ag
    ag = AutoScalingGroup(group_name='my_group', load_balancers=['myELB'],
                          availability_zones=['us-east-1a'],
                          launch_config=lc, min_size=MIN_SIZE,
                          max_size=MAX_SIZE, connection=as_conn, tags=[as_tag])
    # associate the autoscaling group with launch configuration
    as_conn.create_auto_scaling_group(ag)

    # build the scale policy
    scale_up_policy = ScalingPolicy(
            name='scale_up', adjustment_type='ChangeInCapacity',
            as_name='my_group', scaling_adjustment=1, cooldown=60)
    scale_down_policy = ScalingPolicy(
            name='scale_down', adjustment_type='ChangeInCapacity',
            as_name='my_group', scaling_adjustment=-1, cooldown=60)

    # register the scale policy
    as_conn.create_scaling_policy(scale_up_policy)
    as_conn.create_scaling_policy(scale_down_policy)

    # refresh the scale policy for extra information
    scale_up_policy = as_conn.get_all_policies(
            as_group='my_group', policy_names=['scale_up'])[0]
    scale_down_policy = as_conn.get_all_policies(
            as_group='my_group', policy_names=['scale_down'])[0]

    # create cloudwatch alarm
    cloudwatch = CloudWatchConnection(
            aws_access_key_id=AWSAccessKeyId,
            aws_secret_access_key=AWSSecretKey,
            is_secure=True)

    # assocate cloudwatch with alarm
    alarm_dimensions = {"AutoScalingGroupName": 'my_group'}

    # create scale up alarm
    scale_up_alarm = MetricAlarm(
            name='scale_up_on_cpu', namespace='AWS/EC2',
            metric='CPUUtilization', statistic='Average',
            comparison='>', threshold='80',
            period='60', evaluation_periods=1,
            alarm_actions=[scale_up_policy.policy_arn],
            dimensions=alarm_dimensions)
    cloudwatch.create_alarm(scale_up_alarm)

    # create scale down alarm
    scale_down_alarm = MetricAlarm(
            name='scale_down_on_cpu', namespace='AWS/EC2',
            metric='CPUUtilization', statistic='Average',
            comparison='<', threshold='55',
            period='60', evaluation_periods=2,
            alarm_actions=[scale_down_policy.policy_arn],
            dimensions=alarm_dimensions)
    cloudwatch.create_alarm(scale_down_alarm)

    # configure autoscaling group with Simple Notification Service(SNS)
    as_conn.put_notification_configuration(ag, ARN_topic,
        ['autoscaling:EC2_INSTANCE_LAUNCH',
         'autoscaling:EC2_INSTANCE_LAUNCH_ERROR',
         'autoscaling:EC2_INSTANCE_TERMINATE',
         'autoscaling:EC2_INSTANCE_TERMINATE_ERROR'
        ])

    print "AutoScaling created successfully"

def create_LoadGenerator():
    # create a instance for load generator
    print "Creating Load Generator..."
    conn = boto.ec2.connect_to_region("us-east-1",
        aws_access_key_id=AWSAccessKeyId, aws_secret_access_key=AWSSecretKey)

    reservation = conn.run_instances(LOAD_GEN_AMI, placement='us-east-1a',
                  key_name=ACCESS_KEY, instance_type=MACHINE_TYPE,
                  security_groups=[SECURITY_GRP])
    instance = reservation.instances[0]
    instance_id = instance.id
    print "Load Generator Instance ID: %s" % instance_id
    # tag the instance after created
    conn.create_tags(instance_id, {"Project": "2.3"}, dry_run=False)
    # retrieve the dns for certain instance
    while True:
        reservs = conn.get_all_instances(instance_ids=[instance_id])
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
            print "Load Generator authenticated successfully"
            response.close()
            break
        except urllib2.URLError:
            continue
    return dns

def activate_LoadGenerator(load_dns, elb_dns):
    url = "http://" + load_dns + "/begin-phase-3?" +\
          "dns=" + elb_dns + "&testId=" + TESTID
    req = urllib2.Request(url)
    while True:
        try:
            time.sleep(5)
            response = urllib2.urlopen(req)
            print "activate Load Generator DNS[%s] successfully" % load_dns
            response.close()
            break
        except urllib2.URLError:
            continue

def start_Warmup(load_dns, elb_dns):
    url = "http://" + load_dns + "/warmup?" +\
          "dns=" + elb_dns + "&testId=" + TESTID
    req = urllib2.Request(url)
    while True:
        try:
            time.sleep(3)
            response = urllib2.urlopen(req)
            print "start warming up the ELB..."
            print "waiting for at least 5 mins"
            response.close()
            time.sleep(6*60)
            print "finish warming up the ELB"
            break
        except urllib2.URLError:
            continue

def main():
    elb_dns  = create_LoadBalancer()
    load_dns = create_LoadGenerator()
    create_AutoScaling()
    print "While waiting for 'InService', go tag your ELB now."
    time.sleep(4*60) # wait for "InService" for instances in ELB
    for i in range(2):
        start_Warmup(load_dns, elb_dns)
    activate_LoadGenerator(load_dns, elb_dns)
    print "View Log at:"
    print "http://" + load_dns + "/view-logs?name=result_chihangw_iwantplay.txt"
    print "Good Luck!!!"
    time.sleep(60*110)
    # delete all the configuration and ELB
    ag.shutdown_instances()
    ag.delete()
    lc.delete()
    elb.delete()

if __name__ == '__main__':
    main()