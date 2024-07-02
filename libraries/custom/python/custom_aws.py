import logging
import boto3
from botocore.exceptions import ClientError
import json


logger = logging.getLogger()
logger.setLevel("INFO")


def get_aws_secret(secret_name, env, region="us-east-1"):
    """
    Get an AWS secret from secrets manager
    :param secret_name: The name of the secret (don't include a slash)
    :param env: The name of the environment (prod|test)
    :param region: Defaults to us-east-1
    :return: Return a dictionary of the credential
    """
    session = boto3.session.Session()  # Create a Secrets Manager client
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId="{}/{}".format(env, secret_name)
        )
    except ClientError as e:
        logger.error(e)  # Log any errors
        raise e
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)


def get_dynamodb_item(table_name, search_key, region_name="us-east-1"):
    """
    Get an item from AWS DynamoDB
    :param table_name: DynamoDB table to search
    :param search_key: Dictionary with key name/value and optional secondary key
    :param region_name: Defaults to us-east-1
    :return:
    """
    aws_client = boto3.resource('dynamodb', region_name)
    dynamodb_table = aws_client.Table(table_name)
    try:
        response = dynamodb_table.get_item(Key=search_key)
    except ClientError as e:
        logger.error(e)  # Log any errors
        raise e
    return response


def put_dynamodb_item(table_name, item, region_name="us-east-1"):
    """
    Add an Item into a dynamodb table
    :param table_name: The name of the table
    :param item: A Dictionary of the item to add
    :param region_name: Defaults to us-east-1
    :return:
    """
    aws_client = boto3.resource('dynamodb', region_name)
    dynamodb_table = aws_client.Table(table_name)
    try:
        response = dynamodb_table.put_item(Item=item)
    except ClientError as e:
        logger.error(e)  # Log any errors
        raise e
    return response


def delete_dynamodb_item(table_name, search_key, region_name="us-east-1"):
    """
    Delete an Item into a dynamodb table
    :param table_name: The name of the table
    :param search_key: A Dictionary of the item to delete
    :param region_name: Defaults to us-east-1
    :return:
    """
    aws_client = boto3.resource('dynamodb', region_name)
    dynamodb_table = aws_client.Table(table_name)
    try:
        response = dynamodb_table.delete_item(Key=search_key)
    except ClientError as e:
        logger.error(e)  # Log any errors
        raise e
    return response
