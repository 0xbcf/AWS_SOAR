import splunklib.client as splunk_client
import requests
from splunklib import results as splunk_results


def connect(creds):
    service = splunk_client.connect(host=creds.get('host', 'localhost'), port=8089, username=creds.get('user', 'NA'),
                             password=creds.get('pass', 'NA'))
    return service


def query(svc: splunk_client.Service, search: str, earliest: str, latest="now"):
    """
    Submit a Splunk search query and get the results as a list
    Params:
    :svc: - service object for Splunk connect
    :search: - Search query (include a | fields parameter to extract fields)
    :earliest: - the earliest time stamp
    """
    kwargs_oneshot = {"earliest_time": earliest, "latest_time": latest}
    oneshot_results = svc.jobs.oneshot(search, **kwargs_oneshot, output_mode="json")
    results = []
    for result in splunk_results.JSONResultsReader(oneshot_results):
        if isinstance(result, dict):
            # We are ignoring Splunk Messages
            results.append(result)
    return results


def results(creds, search_id):
    headers = {'Authorization': "Bearer {}".format(creds.get('token'))}
    path = "https://{}:8089/services/search/v2/jobs/{}/results?output_mode=json".format(creds.get('host'), search_id)
    response = requests.get(path, headers=headers, timeout=5)
    return response.json()
