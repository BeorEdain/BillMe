import datetime
import json
import logging
import os
import urllib.request

# Create custom logger and set the level
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create formatter, create handler, and assign the format to the handler
# TODO: Add an option to have a config file for the logger
formatter = logging.Formatter('%(filename)s: %(levelname)s: %(funcName)s: ' +
                              '%(message)s')
handler = logging.FileHandler('Bill_The.log','w')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Set the site base. It should never change.
siteBase = "https://api.govinfo.gov/"

# Set the save location.
# TODO: Set as an optional passable variable from commandline
saveLocation = "content/"

def getPage(link) -> bytes:
    """
    A helper definition to gather the web page and return it as a bytes stream
    """
    # Inform the logger that the page is being retrieved
    logger.info("Getting the page")

    # Get the site passed in from the link
    site = urllib.request.urlopen(link)

    # Read the site
    response = site.read()

    # If the site isn't loading for any reason
    # TODO: Set a finite amount of retries before failing.
    while not site:
        # Warn the logger
        logger.warning("Need to repull the page")

        # Attempt to retrieve the site again
        site = urllib.request.urlopen(link)

        # Read the site
        response = site.read()

    # If the API returns the website successfully, but there is no data
    if json.loads(response).get('message') == "No results found":
        # Inform the logger that there is no data
        logger.info("The page requested is empty")

    # Return the data as a bytes stream
    return response

    logger.info("Checking for content")
    while site.get('message') == "No results found":
        logger.warning("Needed collection repull")
        site = getPage(site)

    return site

def saveToJson(jsonIn: bytes, name: str):
    """
    A generic save definition. Intakes both the JSON list and the collection
    type, be it the meta list of collections, or the individual collection lists
    """
    # Inform the logger of the location and name of the file
    logger.info(f"Saving to \'{saveLocation}{name}.json\'")

    # Open the specified save location and save the file there
    with open(saveLocation + name + '.json', 'wb') as jsonFile:
        jsonFile.write(jsonIn)

def getAPIKey() -> str:
    """
    A helper definition to grab the API key from its file. This is used so the
    API never needs to be stored within the program itself and can be changed
    as needed.
    """
    # Check to see if the save location exists. It is here because this is
    # always going to be the definition that is called before any other that
    # would require the save location.
    if not os.path.isdir(saveLocation):
        # If it doesn't exist, inform the logger
        logger.info(f"\'{saveLocation}\' does not exist. Creating it now.")

        # Create the directory
        os.mkdir(saveLocation)

    # Inform the logger that the API key is being retrieved
    logger.info("Getting API key and returning")

    # Open and return the API key
    f = open("apiKey", 'rt')
    with open("apiKey", 'rt') as key:
        return key.read()

def getCollections() -> json:
    """
    Return a JSON list of all of the different collections
    """
    # Inform the logger that the collections are being downloaded
    logger.info("Getting the collections")

    #Build the site.  This one is simple as it requires only the API key
    site = siteBase + "collections"

    # Inform the logger that the site is being accessed
    logger.info(f"Accessing {site}")

    # Append the API key after the logger call so it isn't leaked into the logs.
    site = site + "?api_key=" + getAPIKey()

    # Inform the logger that the page is being returned.
    logger.debug("Returning getPage")

    # Return the page
    return getPage(site)

def getCollection(collection: str, startDate: str, endDate: str = 'none', 
                  offset: int = 0, pageSize: int = 10, congress: int = -1,
                  docClass: str = 'none') -> json:
    """
    Get the packages from a specific collection starting from a specific date
    and time.  Can optionally define an end time as well.\n
    collection  = The collection you're looking for.\n
    startDate   = The start date in the YYYY-MM-DD'T'HH:MM:SS'Z' format.\n
    endDate     = The end date in the YYYY-MM-DD'T'HH:MM:SS'Z' format.  Not
                  necessary to run.\n
    offset      = The number of items to skip before it starts displaying.
                  Starting at 0 is normal and default.  Not necessary to run.\n
    pageSize    = The number of items to return on a page.  10 is default.  Not
                  necessary to run.\n
    congress    = The number of the congress to search in.  Not necessary to 
                  run.\n
    docClass    = The type of classification for the item you're looking for.
                  e.g. s, hr, hres, sconres, et cetera.\n

    This will eventually return the JSON of the collection that's being searched
    for instead of saving it.
    """

    # Begin appending the URL together
    # Add the collection and the start date in the correct format
    site = (siteBase + "collections/" + collection + "/"
                + startDate.replace(':', '%3A'))

    # If there is an end date, append it in the correct format
    if endDate != 'none':
        site = site + "/" + endDate.replace(':', '%3A')

    # Add the offset
    site = site + "?offset=" + str(offset)

    # Add the page size
    site = site + "&pageSize=" + str(pageSize)

    # If there is a specific congress being searched for
    if congress != -1:
        site = site + "&congress=" + str(congress)

    # If there is a specific docClass being searched for
    if docClass != 'none':
        site = site + "&docClass=" + docClass
    
    # Add the API key
    site = site + "&api_key="

    # Inform the logger that the site is being accessed
    logger.info(f"Accessing {site}")

    # Append the API key after the logger call so it isn't leaked into the logs.
    site = site + getAPIKey()

    # Return the page
    return getPage(site)

def getPackageSummary(pkgID: str) -> json:
    """
    Get package summary.\n
    pkgID   = The specific ID of the item you're looking for,
              e.g. BILLS-116s3398is
    """
    # Build the site URL.  Simple for this one as its only variables are required
    site = siteBase + "packages/" + pkgID + "/summary"

    # Inform the logger that the site is being accessed.
    logger.info(f"Accessing {site}")

    # Append the API key after the logger call so it isn't leaked into the logs.
    site = site + "?api_key=" + getAPIKey()

    return getPage(site)

def getPackage(pkgID: str, contentType: str):
    """
    Get the specific package in the specified format.\n
    pkgID       = The specific ID of the itme you're looking for,
                  e.g. BILLS-116s3398is.\n
    contentType = The specific format for the content that you're looking for,
                  e.g. pdf, xml, htm, xls, mods, premis, zip.
    """
    # Build the site URL.  Simple for this one as its only variables are
    # required.
    site = siteBase + "packages/" + pkgID + "/" + contentType

    # Inform the logger that the site is being accessed
    logger.debug(f"Accessing {site}")

    # Append the API key after the logger call so it isn't leaked into the logs.
    site = site + "?api_key=" + getAPIKey()

    # Inform the logger that the file is being downloaded
    logger.info(f"Saving to \'{saveLocation}{pkgID}.{contentType}\'")

    # Download the file with the specified name and type
    urllib.request.urlretrieve(site, saveLocation + pkgID + "." + contentType)

def getPublished(dateIssuedStart: str,collection: str, 
                 dateIssuedEndDate: str = 'none', offset: int = 0,
                 pageSize: int = 10, congress: int = -1, docClass: str = 'none',
                 modifiedSince: str = 'none') -> json:
    """
    Get a list of packages based on when they were issued.\n
    dateIssuedStart     = The start date to look for published items.\n
    dateIssuedEndDate   = The end date to look for published items\n 
    collection          = The collection that the item is in e.g. BILLS.\n
    offset              = The number of items to skip before it starts
                          displaying. Starting at 0 is normal and default. Not
                          necessary to run.\n
    congress            = The number of the congress to search in.  Not 
                          necessary to run.\n
    docClass            = The type of classification for the item you're looking
                          for. E.g. s, hr, hres, sconres, et cetera.\n
    modifiedSince       = The date after which the item was modified in the
                          YYYY-MM-DD'T'HH:MM:SS'Z' format.  Not necessary to
                          run.\n
    """

    # Begin putting the site together with the required variables
    site = (siteBase + "published/" + dateIssuedStart)

    # If there is an end date, append it
    if dateIssuedEndDate != 'none':
        site = site + "/" + dateIssuedEndDate

    # Append the required parts of the site
    site = (site + "?offset=" + str(offset) + "&pageSize=" + str(pageSize) +
            "&collection=" + collection)

    # If a congress is specified, append it
    if congress != -1:
        site = site + "&congress" + str(congress)

    # If a docClass is specified, append it
    if docClass != 'none':
        site = site + "&docClass=" + docClass
    
    # If a modifiedSince date is specified, append it
    if modifiedSince != 'none':
        site = site + "&modifiedSince=" + modifiedSince.replace(":","%3A")

    # Inform the logger that the site is being accessed
    logger.info(f"Accessing {site}")

    # Append the API key after the logger call so it isn't leaked into the logs.
    site = site + "&api_key=" + getAPIKey()

    # Return the page
    return getPage(site)
