import json
from datetime import datetime, timedelta
from time import gmtime, strftime

from api_interface import *


def get_list_of_type(doc_type: str, write_to_file: bool,
                     num_entries) -> list:
    """
    Get all of the specified type of items. For example, "BILLS" will retrieve
    the packageId of all bills.\n
    doc_type        = The type of document you want to retrieve. E.g. BILLS\n
    write_to_file   = Whether or not you want to write the list to a file or
                      have it returned as a list.
    """

    # Set the current format to the ISO8601 format.
    time_format = "%Y-%m-%dT%H:%M:%SZ"

    # Set the end date to the current time.
    end_date = datetime.datetime.strftime(datetime.datetime.now(), time_format)

    # Build an initially empty list to hold the packageId's.
    item_list = []

    # Instantiate an initially empty integer to track the total number of
    # entries done.
    total_num = 0

    # A short loop counter to ensure we're getting all of the entries we need
    # before moving on.
    j = 0

    # The while loop where all of the logic is done.
    while True:
        # Set the start date to a time exactly one week prior to the end_date.
        # Small intervals are used to ensure the program does not exceed the
        # 10,000 item limit of the API.
        start_date = (datetime.datetime.strptime(end_date, time_format)-
                      timedelta(weeks=1)).__format__(time_format)

        # Get the initial list of published documents.
        pub_list = get_published(start_date, doc_type, end_date, page_size=100)

        # Get the number of documents in the current listing. Will be the total
        # number of entries in the current selection and is not necessarily
        # equal to unit_count.
        count = json.loads(pub_list).get('count')

        # Get the next page from the listing.
        next_page = json.loads(pub_list).get('nextPage')

        # If the number of entries recorded, "j", is less than the total number
        # of entries in the current selection, "count", then continue to iterate
        # over it.
        while j < count:
            # Get the packageId's for each of the entries in the current
            # selection.
            for item in json.loads(pub_list).get('packages'):
                item_list.append(item.get('packageId'))

                # Iterate the small counter.
                j = j + 1

                # Iterate the overall counter.
                total_num = total_num + 1

            # If there is no next page, go on to the next list.
            if next_page == None:
                break

            # If there is a next page, notify the logger, gather the page, and
            # move on to it.
            else:
                logger.debug(f"Moving to page {next_page}")
                link = next_page + "&api_key=" + get_API_key()
                pub_list = get_page(link)

                # Set the new nextPage so the program can gather the last page
                # of entries within the set.
                next_page = json.loads(pub_list).get('nextPage')

        # Reset the inner counter so it can be used to track the current number
        # of gathered entries.
        j = 0

        # Set the new end date to be the old start date. This ensures there is
        # no gaps in the data being gathered.
        end_date = start_date

        # Inform the logger of the number of entries gathered up to this point.
        logger.info(f"Gathered {total_num} entries so far.")

        # if all of the entries have been gathered, break the loop. It's done.
        if total_num == num_entries:
            logger.info("Goal reached, exiting loop.")
            break

    # Check whether the user wants to write the list to a file or simply return
    # it to be manipulated further.
    if write_to_file:
        # Write all of the packageId's to a file for use later
        with open(f"{save_location}/{doc_type}_list.txt", 'w') as doc_list:
            for item in item_list:
                doc_list.write(f"{item}\n")

    # If the user simply wants to return the list.
    else:
        return item_list
