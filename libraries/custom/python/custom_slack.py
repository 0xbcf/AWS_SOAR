import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json


logger = logging.getLogger()
logger.setLevel("INFO")


def send_slack_msg(creds, message, channel, timestamp=None):
    # Send a message to a Slack channel
    # Example send_slack_msg(creds, "hello world", "xxxx")
    client = WebClient(token=creds['bot'])  # Connect to Slack
    try:
        if timestamp:
            response = client.chat_postMessage(
                channel=channel,
                text=message,
                thread_ts=timestamp,
                unfurl_links=False
            )
        else:
            response = client.chat_postMessage(
                channel=channel,
                text=message,
                unfurl_links=False
            )
    except SlackApiError as e:
        logger.error(e)  # Log any errors
        raise e
    return response


def update_slack_msg(creds, message, channel, timestamp=None):
    # Send a message to a Slack channel
    # Example send_slack_msg(creds, "hello world", "xxxx")
    client = WebClient(token=creds['bot'])  # Connect to Slack
    try:
        if timestamp:
            response = client.chat_update(
                channel=channel,
                text=message,
                ts=timestamp
            )
        else:
            response = client.chat_postMessage(
                channel=channel,
                text=message
            )
    except SlackApiError as e:
        logger.error(e)  # Log any errors
        raise e
    return response


def send_slack_block(creds, message, channel, timestamp=None, metadata=None):
    # Send a block text to a Slack channel
    # Example send_slack_msg(creds, [{}], "xxxx")
    if metadata is None:
        metadata = {}
    client = WebClient(token=creds['bot'])  # Connect to Slack
    try:
        if timestamp:
            response = client.chat_postMessage(
                channel=channel,
                text="",
                blocks=message,
                thread_ts=timestamp,
                metadata=metadata,
                unfurl_links=False
            )
        else:
            response = client.chat_postMessage(
                channel=channel,
                text="",
                blocks=json.dumps(message),
                metadata=metadata,
                unfurl_links=False
            )
    except SlackApiError as e:
        logger.error(e)  # Log any errors
        raise e
    return response
