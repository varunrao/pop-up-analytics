#!/usr/bin/python

import boto3
import traceback
import json
from botocore.exceptions import ClientError
import time

def lambda_handler(event, context):
    fileName = event['filename']
    parameterfile = None
    if 'parameters' in event:
        parameterfile = event['parameters']
    cloudformationconn = boto3.client('cloudformation')

    try:
        print ('Executing CF script : ' + fileName)
        stackexists = False
        templateBodyFile = open(fileName).read()

        params_list = []
        if parameterfile:
            jsonParamFile = open(parameterfile)
            templateParams = json.load(jsonParamFile)
            jsonParamFile.close()
            for paramkey in templateParams['Parameters']:
                params_list.append((
                    {"ParameterKey": paramkey,
                     "ParameterValue": templateParams['Parameters'][paramkey]}
                ))

            stackname = templateParams['StackName']


        try:
            stack = cloudformationconn.describe_stacks(StackName=stackname)
            if len(stack['Stacks']):
                stackexists = True
                # print(
                #     'Stack already exists by the name ' + stackname + '. Delete it before running')
                print(
                    'Template exists. Will try to update ' + stackname + '')
                delete_stack_if_exists(cloudformationconn, stackname)
                stackexists = False
                # cloudformationconn.validate_template(TemplateBody=templateBodyFile)
                # cloudformationconn.update_stack(StackName=stackname,
                #                             TemplateBody=templateBodyFile,
                #                             Parameters=params_list,
                #                             Capabilities=["CAPABILITY_NAMED_IAM"]
                #                         )
        except ClientError as e:
            stackexists = False
            print e
            if e.response['Error']['Code'] == "ValidationError":
                print('Stack not found : ' + stackname)
        if not stackexists:
            cloudformationconn.validate_template(TemplateBody=templateBodyFile)
            cloudformationconn.create_stack(StackName=stackname,
                                            TemplateBody=templateBodyFile,
                                            Parameters=params_list,
                                            DisableRollback=True,
                                            Capabilities=["CAPABILITY_NAMED_IAM"]
                                            )
        print ('Stack ' + stackname + ' setup completed successfully')

    except Exception as e:
        tb = traceback.format_exc()
        print tb
        print ('Deployment not successful: {0}'.format(e.message))

    return "Function ran without errors. Check Logs for details."


# Check stack Status
def check_stack_status(connection, stackname):
    error_state = None
    try:
        stack = connection.describe_stacks(StackName=stackname)
        stackstatus = stack['Stacks'][0]['StackStatus']
        if stackstatus in ['DELETE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
                           'CREATE_IN_PROGRESS', 'ROLLBACK_COMPLETE']:
            loopcontinue = True
            print(
                str("Change in Progress, Stack Status: " + ' - ' + str(stackstatus)))
            time.sleep(10)
            while loopcontinue:
                stack = connection.describe_stacks(StackName=stackname)
                stackstatus = stack['Stacks'][0]['StackStatus']
                if stackstatus in ['UPDATE_COMPLETE', 'CREATE_COMPLETE', 'ROLLBACK_COMPLETE', 'DELETE_COMPLETE',
                                   'CREATE_FAILED']:
                    loopcontinue = False
                    print(str("Stack Update is Completed!" + ' - ' + str(stackstatus)))
                    time.sleep(10)
                else:
                    print(
                        str("Change in Progress, Stack Status: " + ' - ' + str(stackstatus)))
                    time.sleep(10)
        elif error_state == 'No updates are to be performed':
            exit(0)
    except ClientError as e:
        if e.response['Error']['Code'] == "ValidationError":
            print('Stack not found')
    except Exception as e:
        print("Warning " + str(e.message))
        tb = traceback.format_exc()
        print tb
# Deletes a CF stack if it exists
def delete_stack_if_exists(connection, stackname):
    try:
        response = connection.describe_stacks(StackName=stackname)

        if len(response['Stacks']) > 0:
            connection.delete_stack(StackName=stackname)
            check_stack_status(connection, stackname)
    except ClientError as e:
        if e.response['Error']['Code'] == "ValidationError":
            print('Stack not found')
    except Exception as e:
        error_state = e.message
        print("Stack does not exists on delete failed: " + error_state + e)

if __name__ == "__main__":
    event = {}

    event['filename'] = '<path to template>'
    event['parameters'] = '<path to parameters>'

    lambda_handler(event, None)