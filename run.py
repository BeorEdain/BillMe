# TODO: Make a config that shows the last successful run to remove need to pull
#       all of them every time.
# TODO: Make system arguments that can be entered for what kind of documents
#       to pull. E.g. BILLS, BUDGET, etc.
# TODO: Make an if or case array when system args are implemented to allow for
#       each different type.

import json
from datetime import datetime, timedelta

from api_interface import *
from requests import *
from sql_interface import *

# Build the logger.
logger = build_logger()

# Set the time format. This is according to ISO8601 (yyyy-MM-dd'T'HH:mm:ss'Z').
time_format = "%Y-%m-%dT%H:%M:%SZ"

# An initialized base value for current_entries. Used to see how many need to be
# pulled.
current_entries = 0

# Get the time that the program starts.
run_start = datetime.datetime.now().strftime(time_format)

# Create a config variable to store the values pulled from the file.
config = {}
with open("config.json", 'rt') as config_file:
    config = json.load(config_file)

# Find out how much time has elapsed since the last run.
tdelta = (datetime.datetime.strptime(run_start, time_format)-
          datetime.datetime.strptime(config.get("last_pulled"), time_format))

# Pull the most recent list of collections if one or more days have elapsed
# since the last run.
if tdelta.days >= 1:
    # Log the age
    logger.info(f"Collection is {tdelta.days} days old. Repulling.")

    # Pull the new list of collections and save it.
    save_to_json(get_collections(), "collections")

    # Find the specific collection that the user is searching for.
    with open(f"{save_location}collections.json", 'rb') as collection:
            collections = collection.read()

    # TODO: Change to allow granularity with system arguments.
    for item in json.loads(collections).get('collections'):
        if item.get('collectionCode') == "BILLS":
            current_entries = item.get('packageCount')

    # Compute the number of documents that have been created since the last
    # pull.
    entries_to_get = current_entries - config.get("num_entries")

    # Get all of the document ID's of the specified type.
    get_list_of_type("BILLS", True, entries_to_get)

# Placeholder for a list of documents.
list_of_docs = []

# Open the specified document list.
with open("content/BILLS_list.txt", "rt") as list_doc:
    for item in list_doc:
        list_of_docs.append(item.strip("\n"))

# Iterate over each item added to the list.
for item in list_of_docs:
    # Check to see if the current item exists in the database.
    if not check_if_exists(item):
        # If it does not, insert it.
        insert_bill_values(get_package_summary(item))

# Update both the last_pulled and the num_entries fields in the config.
config.update({"last_pulled":run_start})
config.update({"num_entries":current_entries})

# Write the changes to the config file.
with open("config.json", 'wt') as config_file:
    config_file = json.dump(config, config_file, indent=4)

# Set the end date so it's easy to see how long the program ran.
run_end = datetime.now().strftime(time_format)

# Output the start and end times to the logger.
logger.info(f"Run complete. Started {run_start} and ended at {run_end}")
