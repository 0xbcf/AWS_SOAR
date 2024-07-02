"""
Author:
Date:
Description:
"""
import os
import json
import logging
import custom_aws
import custom_slack
import custom_virustotal


# Setup logging and other global variables
logger = logging.getLogger(os.path.abspath(__file__))
environment = os.environ.get('playbook_env', 'test')
logger.setLevel({"test": "INFO", "prod": "WARNING"}.get(environment))  # If Prod, set logging to WARNING


def playbook_start(event, context):
    """
    Entry point for the playbook
    :param event: Contains a dictionary of details about the event that triggered the lambda function
    :param context: Required to launch lambda functions, but not needed within the program
    :return:
    """
    logger.info(event.get('detail', {}))  # For debug purposes
    ip = event.get('detail', {}).get('address')  # Get IP address of the source
    vt_creds = custom_aws.get_aws_secret("virustotal", environment)  # Get credential
    results = custom_virustotal.get_ip_reputation(vt_creds, ip)  # Get results from VirusTotal
    logger.info(results)
    creds = custom_aws.get_aws_secret("slackbot", environment)  # Get credential
    country_code = results.get('data', {}).get('attributes', {}).get('country')
    custom_slack.send_slack_msg(creds, "The IP {} belongs to: {}".format(ip, country_code), "xxxx")


if __name__ == '__main__':
    # To test this playbook, run the playbook.py file from the command line,
    # and it will use test_event.json for testing
    logging.basicConfig(level=logging.INFO)
    logger.info("Running from command line")
    with open("test_event.json", 'r') as f:
        playbook_start(json.load(f), "not used")
