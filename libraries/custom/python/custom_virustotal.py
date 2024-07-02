import vt
import logging
import base64

logger = logging.getLogger()
logger.setLevel("INFO")


def get_ip_reputation(creds, indicator):
    # Get the IP reputation from VirusTotal and return the raw response
    client = vt.Client(creds.get('token', 'NA'))
    try:
        result = client.get_json("/ip_addresses/{}".format(indicator))
    except vt.error.APIError:
        logging.error("Error looking up the IP address {}".format(indicator))
        result = {}
    client.close()
    return result


def get_domain_reputation(creds, indicator):
    # Get the domain reputation from VirusTotal and return the raw response
    client = vt.Client(creds.get('token', 'NA'))
    result = client.get_json("/domains/{}".format(indicator))
    client.close()
    return result


def get_hash_reputation(creds, indicator):
    # Get a hash reputation from VirusTotal and return the raw response
    client = vt.Client(creds.get('token', 'NA'))
    result = client.get_json("/files/{}".format(indicator))
    client.close()
    return result


def get_url_reputation(creds, indicator):
    # Get a URL reputation from VirusTotal and return the raw response
    client = vt.Client(creds.get('token', 'NA'))
    result = client.get_json("/urls/{}".format(base64.urlsafe_b64encode(indicator).strip("=")))
    client.close()
    return result
