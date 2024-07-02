import json
import boto3
import logging
import time
from datetime import datetime, timedelta
import custom_aws
import custom_slack

logger = logging.getLogger()
logger.setLevel("INFO")
client = boto3.client('logs')


def playbook_start(event, context):
    logging.info(event)
    creds = custom_aws.get_aws_secret("slackbot", "prod")
    query = "filter @message like /(?i)(ERROR|WARNING)/ | fields @timestamp, @message | sort @timestamp desc | limit 5"
    start_query = client.start_query(
        logGroupName="SOAR-App-logging",
        startTime=int((datetime.today() - timedelta(minutes=15)).timestamp()),
        endTime=int(datetime.now().timestamp()),
        queryString=query
        )
    logging.info(start_query)
    query_id = start_query['queryId']
    response = None
    while response == None or response['status'] == 'Running':
        logger.info("Waiting for query to complete..")
        time.sleep(1)
        response = client.get_query_results(queryId=query_id)
    logging.info(response)
    results = response.get('results', [])
    event_list = []
    for item in results:
        event_list.append(item[0].get('value', 'NA') + " " + item[1].get('value', 'NA'))
    name = event.get('alarmData', {}).get('alarmName', 'NA')
    if event_list:
        msg = """
        {0}
        ```
        {1}
        ```
        """.format(name, "\n".join(event_list))
        custom_slack.send_slack_msg(creds, msg, "xxxx")
