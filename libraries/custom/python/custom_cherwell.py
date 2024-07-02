from CherwellAPI import CherwellClient


def connect(creds):
    # Create a new CherwellClient Connection
    cherwell_client = CherwellClient.Connection(creds.get('host'), creds.get('clientid'),
                                                creds.get('username'), creds.get('password'))
    return cherwell_client
