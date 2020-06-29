# TODO: Make system arguments that can be entered for what kind of documents
#       to pull. E.g. BILLS, BUDGET, etc.
# TODO: Make an if or case array when system args are implemented to allow for
#       each different type.

import json
from datetime import datetime, timedelta

from interfaces.api_interface import *
from interfaces.sql_interface import *

# from api_interface import *
from requests import *
# from sql_interface import *

# Set the time format. This is according to ISO8601 (yyyy-MM-dd'T'HH:mm:ss'Z').
time_format = "%Y-%m-%dT%H:%M:%SZ"

# Placeholder "sys.arg" that will be fully instantiated later.
# TODO: Build this so it's real not just a variable.
doc_type = "BILLS"

# An initialized base value for current_entries. Used to see how many need to be
# pulled.
current_entries = 0

# Get the time that the program starts.
run_start = datetime.datetime.now().strftime(time_format)

# Create a config variable to store the values pulled from the file.
config = {}

# Try to open the config file.
try:
    with open("configs/config.json", 'rt') as config_file:
        config = json.load(config_file)

# If the file doesn't exist for whatever reason.
except FileNotFoundError as error:
    # Check if the configs/ folder exists.
    if not os.path.isdir("configs/"):
        # If it doesn't, create it.
        os.mkdir("configs/")

    # Log that the config file does not exist.
    logger.info("config.json does not exist. Creating.")
    
    # Create an empty set for the data.
    data = {}

    # Insert the appropriate template data.
    data.update({"last_pulled":"0001-01-01T00:00:01Z"})
    data.update({"num_entries":0})

    # Write it to the config.json file.
    with open("configs/config.json", 'w') as config_file:
        json.dump(data, config_file, indent=4)

    # Use the templated data for the rest of the program.
    config = data

# Find out how much time has elapsed since the last run.
tdelta = (datetime.datetime.strptime(run_start, time_format)-
          datetime.datetime.strptime(config.get("last_pulled"), time_format))

# Placeholder for a list of documents.
list_of_docs = []

# Pull the most recent list of collections if one or more days have elapsed
# since the last run.
# TODO: TRUE IS JUST FOR TESTING. REMOVE TO AVOID RUNNING EVERY TIME
if tdelta.days >= 1 or True:
    # Log the age in days.
    logger.info(f"Collection is {tdelta.days} days old. Repulling.")

    # Pull the most recent list of collections and save it.
    save_to_json(get_collections(), "collections")

    # Find the specific collection that the user is searching for.
    with open(f"{save_location}collections.json", 'rb') as collection:
            collections = collection.read()

    for item in json.loads(collections).get('collections'):
        if item.get('collectionCode') == doc_type:
            current_entries = item.get('packageCount')
            break

    # Compute the number of documents that have been created since the last
    # pull.
    entries_to_get = current_entries - config.get("num_entries")
    logger.info(f"There are {entries_to_get} new entries.")

    # Get all of the document ID's of the specified type.
    list_of_docs = get_list_of_type(doc_type, False, entries_to_get)

# # Open the specified document list.
# with open(f"content/{doc_type}_list.txt", "rt") as list_doc:
#     for item in list_doc:
#         list_of_docs.append(item.strip("\n"))

# Check to see what values from the list are currently in the database so as to
# not end up performing double duty and inform the log.
logger.info("Comparing lists to see what's needed. Currently " + 
            f"{len(list_of_docs)} long.")
check_all(list_of_docs, doc_type)
logger.info(f"Done comparing. New amount {len(list_of_docs)}")

# A temporary list for any documents that aren't pullable for whatever reason.
list_of_unpullable = []

# Iterate over each item added to the list.
for item in list_of_docs:
    # Check to see if the current item exists in the database.
    # Kept in even after the check_all() call as a backup in case the check
    # missed some.
    if not check_if_exists(item):
        # If it does not, try to insert it.
        try:
            insert_bill_values(get_package_summary(item))
            # Some documents could not be pulled due to internal server error.
            # This is here to catch those problems and report them.
        except HTTPError as error:
            logger.critical(f"{item} returned an HTTPError. {error}")
            list_of_unpullable.append(item)

# Update both the last_pulled and the num_entries fields in the config.
config.update({"last_pulled":run_start})
config.update({"num_entries":current_entries})

# Write the changes to the config file.
with open("config.json", 'wt') as config_file:
    config_file = json.dump(config, config_file, indent=4)

# Write the list of unpullable documents to a file.
with open("content/unpullable.txt", 'wt') as unpullable:
    for item in list_of_unpullable:
        unpullable.write(f"{item}\n")

# Set the end date so it's easy to see how long the program ran.
run_end = datetime.datetime.now().strftime(time_format)

# Output the start and end times to the logger.
logger.info(f"Run complete. Started {run_start} and ended {run_end}.")
