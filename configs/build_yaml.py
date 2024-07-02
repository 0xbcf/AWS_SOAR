import os
import sys
import importlib.util
from troposphere import Base64, Select, FindInMap, GetAtt
from troposphere import GetAZs, Join, Output, If, And, Not
from troposphere import Or, Equals, Condition
from troposphere import Parameter, Ref, Tags, Template, Export
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution
from troposphere.cloudfront import DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.serverless import Function, FunctionGlobals
from troposphere.serverless import LayerVersion
from troposphere.logs import LogGroup
from troposphere.iam import ManagedPolicy
from troposphere.awslambda import Environment, VPCConfig, LoggingConfig, EventInvokeConfig

aws_account_id = "xxxxxxxxxxxx"
vpc_subnet_id = "vpc-xxxxxxxxxxxx"
security_group_id = "sg-xxxxxxxxxxxx"

def generate_secret(secret_identities):
    # Generate a policy that allows access to secrets in secrets manager
    secret_permission = {"Effect": "Allow",
     "Action": ["secretsmanager:GetSecretValue"],
     "Resource": []
     }
    for item in secret_identities:
        secret_permission["Resource"].append(
            "arn:aws:secretsmanager:us-east-1:{}:secret:prod/{}-*".format(aws_account_id, item))
        secret_permission["Resource"].append(
            "arn:aws:secretsmanager:us-east-1:{}:secret:test/{}-*".format(aws_account_id, item))
    return [secret_permission]
t = Template()
t.set_version("2010-09-09")
t.set_transform("AWS::Serverless-2016-10-31")
t.set_description("This is a SOAR application with multiple playbooks")
environment = t.add_parameter(Parameter(
    "environment",
    Type="String",
    Default="test",
    AllowedValues=["test", "production"],
))
t.add_condition("isProd", Equals(Ref(environment), "production"))
t.add_condition("isTest", Equals(Ref(environment), "test"))

TestFunction = t.add_resource(Function(
    "TestFunction",
    Handler="playbook.playbook_start",
    Runtime="python3.11",
    CodeUri="monitoring/TestFunction/",
    Policies=[Ref("PlaybookCommonPolicy"), {"Statement": [
        {"Effect": "Allow", "Action": ["secretsmanager:GetSecretValue"],
         "Resource": ["arn:aws:secretsmanager:us-east-1:{}:secret:test/panorama-*".format(aws_account_id)]}]}],
))

SOARProdMonitor = t.add_resource(Function(
    "SOARProdMonitor",
    Handler="playbook.playbook_start",
    Runtime="python3.11",
    CodeUri="monitoring/SOAR-prod-monitor/",
    Policies=[Ref("PlaybookCommonPolicy"), {"Statement": [
        {"Effect": "Allow", "Action": ["logs:StartQuery", "logs:GetQueryResults"],
         "Resource": ["arn:aws:logs:us-east-1:{}:log-group:*".format(aws_account_id)]}]}],
    Condition="isProd",
))

SOARTestMonitor = t.add_resource(Function(
    "SOARTestMonitor",
    Handler="playbook.playbook_start",
    Runtime="python3.11",
    CodeUri="monitoring/SOAR-test-monitor/",
    Policies=[Ref("PlaybookCommonPolicy"), {"Statement": [
        {"Effect": "Allow", "Action": ["logs:StartQuery", "logs:GetQueryResults"],
         "Resource": ["arn:aws:logs:us-east-1:{}:log-group:*".format(aws_account_id)]}]}],
    Condition="isTest",
))
CustomLibrary = t.add_resource(LayerVersion(
    "CustomLibrary",
    ContentUri="libraries/custom/",
    LayerName=If("isProd", "CustomLibrary", "CustomLibraryTest"),
    RetentionPolicy="Retain",
    Description="Shared code for playbooks",
    CompatibleRuntimes=["python3.11"],
))

CustomDependency = t.add_resource(LayerVersion(
    "CustomDependency",
    ContentUri="libraries/dependencies1/",
    LayerName=If("isProd", "CustomDependency1", "CustomDependency1Test"),
    RetentionPolicy="Retain",
    Description="Shared code for playbooks",
    CompatibleRuntimes=["python3.11"],
))

SOARLogGroup = t.add_resource(LogGroup(
    "SOARLogGroup",
    LogGroupName=If("isProd", "SOAR-App-logging", "SOAR-App-logging-test"),
    RetentionInDays=30,
))

PlaybookCommonPolicy = t.add_resource(ManagedPolicy(
    "PlaybookCommonPolicy",
    ManagedPolicyName=If("isProd", "prod-playbook-policy", "test-playbook-policy"),
    PolicyDocument={"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": ["ec2:CreateNetworkInterface",
                                                                                          "ec2:DescribeNetworkInterfaces",
                                                                                          "ec2:CreateTags",
                                                                                          "ec2:DeleteNetworkInterface"],
                                                            "Resource": "*"}, {"Effect": "Allow",
                                                                               "Action": ["logs:CreateLogStream",
                                                                                          "logs:PutLogEvents"],
                                                                               "Resource": [
                                                                                   "arn:aws:logs:us-east-1:{}:log-group:SOAR-App-logging-test".format(aws_account_id),
                                                                                   "arn:aws:logs:us-east-1:{}:log-group:SOAR-App-logging".format(aws_account_id)]},
                                                           {"Effect": "Allow",
                                                            "Action": ["secretsmanager:GetSecretValue"], "Resource": [
                                                               "arn:aws:secretsmanager:us-east-1:{}:secret:test/slackbot-*".format(aws_account_id),
                                                               "arn:aws:secretsmanager:us-east-1:{}:secret:prod/slackbot-*".format(aws_account_id)]},
                                                           {"Effect": "Allow",
                                                            "Action": ["dynamodb:BatchGetItem", "dynamodb:Query",
                                                                       "dynamodb:Scan", "dynamodb:GetItem",
                                                                       "dynamodb:DeleteItem", "dynamodb:BatchWriteItem",
                                                                       "dynamodb:PutItem", "dynamodb:UpdateItem"],
                                                            "Resource": [
                                                                "arn:aws:dynamodb:us-east-1:{}:table/*".format(aws_account_id)]}]},
))


processed_templates = ["template"]
for playbook_path, dirs, files in os.walk("./playbooks"):
    for file in files:
        if file == "playbook_settings.py":
            playbook_name = playbook_path.split('/')[-1]
            if playbook_name in processed_templates:
                # Avoid processing playbooks that have duplicate names
                continue
            # Import playbook settings
            spec = importlib.util.spec_from_file_location("playbook_settings", os.path.join(playbook_path, file))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            parent_name = "Default"
            t.add_resource(Function(
                str(parent_name + playbook_name),
                MemorySize=128,
                Timeout=60,
                Handler="playbook.playbook_start",
                CodeUri=playbook_path,
                Architectures=["x86_64"],
                Runtime="python3.11",
                Layers=[Ref(CustomLibrary), Ref(CustomDependency)],
                Environment=Environment(Variables={
                    "playbook_env": If("isProd", "prod", "test")
                }),
                VpcConfig=VPCConfig(SecurityGroupIds=[security_group_id],
                                    SubnetIds=[vpc_subnet_id],
                                    Ipv6AllowedForDualStack=False),
                Events={"Rule1": {"Type": "EventBridgeRule",
                                  "Properties": {"EventBusName": If("isProd", "soar", "soar-test"),
                                                 "Pattern": {
                                                     "detail": module.trigger_pattern
                                                 }}}},
                Policies=[Ref("PlaybookCommonPolicy")] + module.permissions + generate_secret(module.secret_access),
            ))



print(t.to_yaml())
