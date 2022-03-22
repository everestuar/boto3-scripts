import os
from urllib import response
import boto3

ec2_client = boto3.client('ec2')

def main():
    print("main")
    # print(get_ec2_name('i-025f0d821ceb5a8f2'))
    associate_ec2_role()

def associate_ec2_role():
    dict_1 = get_all_ec2s()
    dict_3 = {}

    for i_id, i_info in dict_1.items():
        if (not bool(is_ec2_with_role(i_info['InstanceId']))):
            print("adding: ", i_info)
            associate_iam_instance_profile(i_info['InstanceId'])
        else:
            print("already: ", i_info)
            print("Instance already has an IAM Profile")


def associate_iam_instance_profile(id):    
    response = ec2_client.associate_iam_instance_profile(
        IamInstanceProfile={
            'Arn': 'arn:aws:iam::342433597948:instance-profile/monitor-ec2-ssm',
            'Name': 'monitor-ec2-ssm'
        },
        InstanceId=id
    )

    print("associate_ec2_role response: ", response)


def get_all_ec2s():
    
    contador = 0
    i_intances = {}

    response = ec2_client.describe_instances(
        # Filters = [
        #     {
        #         'Name': 'iam-instance-profile.arn',
        #         'Values': [
        #             'arn:aws:iam::342433597948:instance-profile/monitor-ec2-ssm',
        #         ]
        #     },
        # ],
        MaxResults=200,
    )

    # print("response: ", response)

    for r in response['Reservations']:
        # print("instances: ", r['Instances'])
        for i in r['Instances']:
            contador = contador + 1
            temp = {}
            temp['InstanceId'] = i['InstanceId']
            temp['InstanceType'] = i['InstanceType']   
            for x in i['Tags']:                             
                if x['Key'] == 'Name':
                    # print("Nombre: ", str(x['Value']).strip())                    
                    temp['Nombre'] = str(x['Value']).strip()
            i_intances[contador] = temp

    print("\n")                
    # print("instancias: ", i_intances)
    return i_intances

def is_ec2_with_role(id):
    
    contador = 0
    i_intances = {}

    response = ec2_client.describe_instances(
        Filters = [
            {
                'Name': 'iam-instance-profile.arn',
                'Values': [
                    'arn:aws:iam::342433597948:instance-profile/monitor-ec2-ssm',
                ]
            },
        ],
        InstanceIds=[
            id,
        ],
    )

    print("is_ec2_with_role response: ", response)

    for r in response['Reservations']:
        # print("instances: ", r['Instances'])
        for i in r['Instances']:
            contador = contador + 1
            temp = {}
            temp['InstanceId'] = i['InstanceId']
            temp['InstanceType'] = i['InstanceType']   
            for x in i['Tags']:                             
                if x['Key'] == 'Name':
                    # print("Nombre: ", str(x['Value']).strip())                    
                    temp['Nombre'] = str(x['Value']).strip()
            i_intances[contador] = temp

    print("is_ec2_with_role instancias: ", i_intances)
    print("\n")
    return i_intances  

main()

