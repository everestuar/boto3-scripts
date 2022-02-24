## Creation of CloudWatch Alarms
## Each method can be executed separately
import os
import boto3

# Create BOTO3 clients
cloudwatch = boto3.client('cloudwatch')
ec2_client = boto3.client('ec2')
rds_client = boto3.client('rds')

## SNS TOPIC TO SEND ALARMS
sns_arn = os.getenv("SNS_ARN")

def get_ec2_info():
    
    contador = 0
    i_intances = {}

    response = ec2_client.describe_instances(
        # Filters = [
        #     {
        #         'Name': 'instance-id',
        #         'Values': [
        #             'i-04d79cd137166acc7',
        #         ]
        #     },
        # ],
        MaxResults=100,
    )

    for r in response['Reservations']:
        for i in r['Instances']:
            contador = contador + 1
            for x in i['Tags']:
                temp = {}
                temp['InstanceId'] = i['InstanceId']
                temp['InstanceType'] = i['InstanceType']
                temp['Nombre'] = str(x['Value']).replace('⚡','').strip()
                i_intances[contador] = temp

    return i_intances

def get_ec2_name(instance_id):

    name = ''
    response = ec2_client.describe_instances(
        Filters = [
            {
                'Name': 'instance-id',
                'Values': [
                    instance_id,
                ]
            },
        ],
        MaxResults=100,
    )

    for r in response['Reservations']:
        for i in r['Instances']:
            for x in i['Tags']:
                if (x['Key'] == 'Name'):
                    name = str(x['Value']).replace('⚡','').strip()
        
    if not name:
        name = instance_id

    return name

def get_path_name(path):
    path_name = ''

    if path == '/':
        path_name = 'root'
    else: 
        path_name = path.replace('/', '', 1)

    return path_name

def get_rds_info():

    contador = 0
    i_databases = {}    

    response = rds_client.describe_db_instances(
        MaxRecords=100,
    )

    for r in response['DBInstances']:
        contador = contador + 1
        temp = {}
        temp['DBInstanceIdentifier'] = r['DBInstanceIdentifier']        
        i_databases[contador] = temp

    return i_databases

def get_ec2_cwagent():
    
    contador = 0

    response = cloudwatch.list_metrics(
        Namespace='CWAgent',
        MetricName='disk_used_percent',
        Dimensions=[
            {
                'Name': 'fstype',
                'Value': 'ext4'
            },
        ]
    )

    for m in response['Metrics']:
        temp = {}
        for d in m['Dimensions']:
            if d['Name'] == 'path': 
                temp['path'] = d['Value']
            
            if d['Name'] == 'InstanceId': 
                temp['InstanceId'] = d['Value']

            if d['Name'] == 'ImageId': 
                temp['ImageId'] = d['Value']
            
            if d['Name'] == 'InstanceType': 
                temp['InstanceType'] = d['Value']

            if d['Name'] == 'device': 
                temp['device'] = d['Value']
            
        create_ec2_disk_alarms(get_ec2_name(temp['InstanceId']), temp['InstanceId'], temp['ImageId'], temp['InstanceType'], get_path_name(temp['path']), temp['path'], temp['device'])

    print('right or wrong everything is done! :)')

def main():
    print("main")
    # print(get_ec2_name('i-025f0d821ceb5a8f2'))
    # get_ec2_cwagent()
    create_alarms()

def create_alarms():

    instances = get_ec2_info()
    rds = get_rds_info()

    for i_id, i_info in instances.items():
        print("\nEC2 ID:", i_id)        
        # create_ec2_ram_alarms(i_info['Nombre'], i_info['InstanceId'], i_info['InstanceType'])
        # create_ec2_cpu_alarms(i_info['Nombre'], i_info['InstanceId'])
        create_ec2_status_alarms(i_info['Nombre'], i_info['InstanceId'])
        # create_ec2_disk_alarms(i_info['nombre'], i_info['id'], i_info['type'])
        print(i_info['Nombre'] + ' ' + i_info['InstanceId'])

    # for i_id, i_info in rds.items():
    #     print("\nRDS ID:", i_id)
    #     create_rds_cpu_alarms(i_info['DBInstanceIdentifier'])
    #     create_rds_connections_alarms(i_info['DBInstanceIdentifier'])
    #     create_rds_storage_alarms(i_info['DBInstanceIdentifier'])
    #     print(i_info['DBInstanceIdentifier'])

def create_ec2_ram_alarms(nombre, id, type):
    cloudwatch.put_metric_alarm(
        AlarmName='ram-utilization-'+nombre,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=2,
        MetricName='mem_used_percent',
        Namespace='CWAgent',
        Period=300,
        Statistic='Average',
        Threshold=70.0,
        TreatMissingData='missing',
        OKActions=[sns_arn],
        AlarmActions=[sns_arn],
        InsufficientDataActions=[],
        AlarmDescription='Alarm when server ' + nombre + ' RAM exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': id
            },
            {
                'Name': 'ImageId',
                'Value': 'ami-09e67e426f25ce0d7',
            },
            {
                'Name': 'InstanceType',
                'Value': type,
            },
        ],
    )

def create_ec2_cpu_alarms(nombre, id):
    cloudwatch.put_metric_alarm(
        AlarmName='cpu-utilization-'+nombre,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=2,
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Period=300,
        Statistic='Average',
        Threshold=70.0,
        TreatMissingData='missing',
        OKActions=[sns_arn],
        AlarmActions=[sns_arn],
        InsufficientDataActions=[],
        AlarmDescription='Alarm when server ' + nombre + ' CPU exceeds 70%',
        Dimensions=[
            {
            'Name': 'InstanceId',
            'Value': id
            },
        ],
    )

def create_ec2_status_alarms(nombre, id):
    cloudwatch.put_metric_alarm(
        AlarmName='status-check-'+nombre,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='StatusCheckFailed',
        Namespace='AWS/EC2',
        Period=180,
        Statistic='Average',
        Threshold=1,
        TreatMissingData='breaching',
        OKActions=[sns_arn],
        AlarmActions=[sns_arn],
        InsufficientDataActions=[],
        AlarmDescription='Alarm when server ' + nombre + ' status check fails',
        Dimensions=[
            {
            'Name': 'InstanceId',
            'Value': id
            },
        ],
    )

def create_ec2_disk_alarms(nombre, instance_id, imageid, instance_type, path_name, path, device):
    cloudwatch.put_metric_alarm(
        AlarmName='disk-utilization-'+path_name+'-'+nombre,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=2,
        MetricName='disk_used_percent',
        Namespace='CWAgent',
        Period=300,
        Statistic='Average',
        Threshold=85.0,
        TreatMissingData='missing',
        OKActions=[sns_arn],
        AlarmActions=[sns_arn],
        InsufficientDataActions=[],
        AlarmDescription='Alarm when server ' + nombre + ' filesystem ' + path + ' usage exceeds 85%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
            {
                'Name': 'ImageId',
                'Value': imageid,
            },
            {
                'Name': 'InstanceType',
                'Value': instance_type,
            },
            {
                'Name': 'path',
                'Value': path,
            },
            {
                'Name': 'device',
                'Value': device,
            },
            {
                'Name': 'fstype',
                'Value': 'ext4',
            },
        ],
    )

def create_rds_cpu_alarms(nombre):
    cloudwatch.put_metric_alarm(
        AlarmName='rds-cpu-utilization-'+nombre,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=2,
        MetricName='CPUUtilization',
        Namespace='AWS/RDS',
        Period=300,
        Statistic='Average',
        Threshold=70.0,
        TreatMissingData='missing',
        OKActions=[sns_arn],
        AlarmActions=[sns_arn],
        InsufficientDataActions=[],
        AlarmDescription='Alarm when RDS ' + nombre + ' CPU exceeds 70%',
        Dimensions=[
            {
            'Name': 'DBInstanceIdentifier',
            'Value': nombre
            },            
        ],
    )

def create_rds_connections_alarms(nombre):
    cloudwatch.put_metric_alarm(
        AlarmName='rds-db-connections-'+nombre,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        EvaluationPeriods=2,
        MetricName='DatabaseConnections',
        Namespace='AWS/RDS',
        Period=300,
        Statistic='Average',
        Threshold=15,
        TreatMissingData='missing',
        OKActions=[sns_arn],
        AlarmActions=[sns_arn],
        InsufficientDataActions=[],
        AlarmDescription='Alarm when RDS ' + nombre + ' exceeds 15 database connections',
        Dimensions=[
            {
            'Name': 'DBInstanceIdentifier',
            'Value': nombre
            },            
        ],
    )

def create_rds_storage_alarms(nombre):
    cloudwatch.put_metric_alarm(
        AlarmName='rds-free-storage-space-'+nombre,
        ComparisonOperator='LessThanOrEqualToThreshold',
        EvaluationPeriods=2,
        MetricName='FreeStorageSpace',
        Namespace='AWS/RDS',
        Period=300,
        Statistic='Average',
        Threshold=12,
        TreatMissingData='missing',
        OKActions=[sns_arn],
        AlarmActions=[sns_arn],
        InsufficientDataActions=[],
        AlarmDescription='Alarm when RDS ' + nombre + ' has 12 GB or less of free storage space',
        Dimensions=[
            {
            'Name': 'DBInstanceIdentifier',
            'Value': nombre
            },
        ],
    )

main()