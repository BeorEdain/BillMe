import json
from time import gmtime, strftime
from urllib.error import HTTPError

from BillMe import *


def getAllofType(docuType: str):
    """
    Get all of the specified type of items. For example, "BILLS" will retrieve
    the packageId of all bills
    """

    # Retrieves the total list so the program knows how many entries to expect
    collections = getCollections()
    saveToJson(collections)

    # Set the initial unit count to zero here so it's accessable throughout
    unitCount = 0

    # Find the specific collection that the user is searching for
    for item in json.loads(collections).get('collections'):
        if item.get('collectionCode') == type:
            unitCount = item.get('packageCount')

    # Get the values of the times individually so they can be individually
    # changed if need be. Initially cast as integers so they can be increased
    # or decreased.
    year = int(strftime("%Y", gmtime()))
    month = int(strftime("%m", gmtime()))
    day = int(strftime("%d", gmtime()))
    hour = int(strftime("%H", gmtime()))
    minute = int(strftime("%M", gmtime()))
    second = int(strftime("%S", gmtime()))

    # Set the end date in the "YYYY-MM-DDTHH:MM:SSZ" format to ensure
    # compatibility with the API. The endDate is the date that is closest to
    # the present.
    endDate = (str(year) + "-" + str(month) + "-" + str(day) + "T" + str(hour) +
               ":" + str(minute) + ":" + str(second) + "Z")

    # Build an initially empty list to hold the packageId's
    itemList = []

    # Instantiate an initially empty integer to track the total number of
    # entries done.
    totalNum = 0

    # A short loop counter to ensure we're getting all of the entries we need
    # before moving on.
    j = 0

    # The while loop where all of the logic is done
    while True:
        # Check to see if the current month is January. If it is, set it to
        # be December instead and put the year back by one.
        if month - 1 == 0:
            month = 12
            year = year - 1
        
        # If the current month is not January, just set it to the previous month
        else:
            month = month - 1

        # Set the start date in the "YYYY-MM-DDTHH:MM:SSZ" format to ensure
        # compatibility with the API. The startDate is the date that is further
        # from the present.
        startDate = (str(year) + "-" + str(month) + "-" + str(day) + "T" +
                     str(hour) + ":" + str(minute) + ":" + str(second) + "Z")

        # Get the initial list of published documents.
        pubList = getPublished(startDate, docuType, endDate, pageSize=100)

        # Get the number of documents in the current listing. Will be the total
        # number of entries in the current selection and is not necessarily
        # equal to unitCount
        count = json.loads(pubList).get('count')

        # Get the next page from the listing.
        nextPage = json.loads(pubList).get('nextPage')

        # If the number of entries recorded, "j", is less than the total number
        # of entries in the current selection, "count", then continue to iterate
        # over it
        while j < count:
            # Get the packageId's for each of the entries in the current
            # selection
            for item in json.loads(pubList).get('packages'):
                itemList.append(item.get('packageId'))
                
                # Iterate the small counter
                j = j + 1

                # Iterate the overall counter
                totalNum = totalNum + 1

            # If there is no next page, go on to the next list
            if nextPage == None:
                break

            # If there is a next page, notify the logger, gather the page, and
            # move on to it.
            else:
                logger.info(f"Moving to page {nextPage}")
                link = nextPage + "&api_key=" + getAPIKey()
                pubList = getPage(link)

                # Set the new nextPage so the program can gather the last page
                # of entries within the set
                nextPage = json.loads(pubList).get('nextPage')
        
        # Reset the inner counter so it can be used to track the current number
        # of gathered entries.
        j = 0

        # Set the new end date to be the old start date. This ensures there is
        # no gaps in the data being gathered.
        endDate = startDate

        # Inform the logger of the number of entries gathered up to this point
        logger.info(f"Gathered {totalNum} entries so far.")

        # if all of the entries have been gathered, break the loop. It's done.
        if totalNum == unitCount:
            break

    # Write all of the packageId's to a file for use later
    with open(f"{docuType}_List.txt", 'w') as docList:
        for item in itemList:
            docList.write(f"{item}\n")

# 1. Get collection meta-list
# 2. Get specific collection list in full
# 3. Get specific article