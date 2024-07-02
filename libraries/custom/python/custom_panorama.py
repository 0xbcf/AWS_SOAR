"""
This library interfaces with the Palo Alto Panorama device
Author: Jason Gates
Requirements: PAN-OS 9.0+
Created: 3-19-2024
"""
import logging
from panos.panorama import Panorama, DeviceGroup, PanoramaCommit, PanoramaCommitAll
from panos.objects import AddressObject, CustomUrlCategory

logger = logging.getLogger()
logger.setLevel("INFO")


def block_ipaddress(palo_creds, device_group, addr, tag="soar_block_list", comment="IP added by SOAR"):
    """
    This function will add an address object to a device group in panorama and tag it with "soar_block_list"
    :parameter: palo_creds - This is a dict returned by custom_aws.get_aws_secret
    :parameter: device_group - The device group name
    :parameter: addr - the IP address (in netmask form) to block
    :parameter: tag - the tag to apply to the address, which will be associated to a dynamic address group
    :parameter: comment - the comment for the address object
    """
    pano = Panorama(palo_creds.get('host'), palo_creds.get('user'), palo_creds.get('pass'))
    if pano.check_commit_locks() or pano.check_config_locks():
        logging.info("a commit lock is in place")
        return {"status": False, "message": "There is a commit lock"}
    dg = DeviceGroup(device_group)
    pano.add(dg)  # Make changes within the specified device group
    obj_name = "soar-badip-" + addr.replace('/', '_')
    obj = AddressObject(obj_name, addr, type="ip-netmask",
                        description=comment[:100],
                        tag=[tag])  # Create the address object
    dg.add(obj)  # Add the object
    try:
        obj.create()  # Try to create or update an existing object
    except:
        return {"status": False, "message": "Failed to add to Panorama"}
    # Commit changes
    palo_commit = PanoramaCommit(description=comment,
                                 device_groups=[device_group],
                                 admins=[palo_creds.get('user')])
    try:
        job_id = pano.commit(cmd=palo_commit, sync=True, exception=True)
    except:
        logging.info("Failed to commit changes")
        return {"status": False, "message": "Failed to commit change"}
    logging.info("Submitted Panorama commit ID {}".format(job_id))
    # Push changes - Not recommended by Defense This is done 2-3am tues, wed, thurs
    # palo_push = PanoramaCommitAll("device group", device_group, admins=[palo_creds.get('user')])
    # job_push = pano.commit(cmd=palo_push)
    # logging.info("Submitted Panorama push ID {}".format(job_push))
    return {"status": True, "message": ""}


def block_url(palo_creds, device_group, url, url_category, comment="URL added by SOAR"):
    """
    This function adds a URL to a specified URL category in a device group
    :parameter: palo_creds - This is a dict returned by custom_aws.get_aws_secret
    :parameter: device_group - The device group name
    :parameter: url - the url to add (eg www.yahoo.com)
    :parameter: url_category - the name of the url category to add the url to
    """
    pano = Panorama(palo_creds.get('host'), palo_creds.get('user'), palo_creds.get('pass'))
    if pano.check_commit_locks() or pano.check_config_locks():
        logging.info("a commit lock is in place")
        return {"status": False, "message": "A commit lock is preventing changes"}
    dg = DeviceGroup(device_group)
    pano.add(dg)
    obj = CustomUrlCategory(name=url_category, url_value=[url])
    dg.add(obj)  # Add the object
    try:
        obj.create()
    except:
        return {"status": False, "message": "Failed to add IP"}
    # Commit changes
    palo_commit = PanoramaCommit(description=comment,
                                 device_groups=[device_group],
                                 admins=[palo_creds.get('user')])
    logging.info("Submitted Panorama commit ID {}".format(palo_commit))
    try:
        job_id = pano.commit(cmd=palo_commit, sync=True, exception=True)
    except:
        logging.info("Failed to commit changes")
        return {"status": False, "message": "Failed to commit change"}
    # Push changes - Not recommended by Defense. This is done 2-3am tues, wed, thurs
    # palo_push = PanoramaCommitAll("device group", device_group, admins=[palo_creds.get('user')])
    # job_push = pano.commit(cmd=palo_push)
    # logging.info("Submitted Panorama push ID {}".format(job_push))
    return {"status": True}


def logoff_vpn_user(palo_creds, device_group, user):
    """
    This function will check if the user is currently on vpn, then kick the user off. Function is not complete and tested yet!
    """
    pano = Panorama(palo_creds.get('host'), palo_creds.get('user'), palo_creds.get('pass'))
    dg = DeviceGroup(device_group)
    result = pano.op(cmd="show global-protect-gateway current-user")
    # Iterate through VPN users
    found_records = []
    for item in result.find('./result'):
        palo_user = item.find('username').text
        # Find the user we want to disconnect
        if user == palo_user:
            palo_computer = item.find('computer').text
            public_ip = item.find('public-ip').text
            virtual_ip = item.find('virtual-ip').text
            cmd_result = pano.op(cmd="request global-protect-gateway client-logout user {0} gateway gateway-name-N reason force-logout computer {1}".format(
                    palo_user, palo_computer))
            status = cmd_result.find('./result/response')
            logging.info(status.value)
            # Verify command executed successfully
            found_records.append({"user": palo_user, "computer": palo_computer, "public_ip": public_ip,
                                  "virtual_ip": virtual_ip})
    return found_records

