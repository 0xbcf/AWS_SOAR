
# For events from Splunk, the key "search_name" is used, and it will hold the name of the Splunk
# alert that triggered the event.
trigger_pattern = {
    "search_name": ["An example alert name from Splunk"]
}
# To run a playbook on a schedule (One Hour, 30 minutes, 10 minutes), instead of via an event trigger, use:
# trigger_pattern = {
#     "schedule": "One Hour"
# }

# List secrets that the playbook should have access to. For a list of available secrets, check /documentation/Permissions.md
secret_access = ["shodan"]

# List additional AWS permissions the playbook should have access to
permissions = []