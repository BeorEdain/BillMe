import datetime
import json
import urllib.request

siteBase = "https://api.govinfo.gov/"

saveLocation = "content/"

def getAPIKey():
    f = open("apiKey", 'rt')
    with open("apiKey", 'rt') as key:
        return key.read()

def getCollections():
    """
    Return a JSON list of all of the different collections
    """

    #Check if the API key is blank, if so, load it
    apiKey = getAPIKey()

    #Build the site.  This one is simple as it requires only the API key
    site = siteBase + "collections?api_key=" + apiKey

    #Load and save the site
    response = urllib.request.urlopen(site)
    webcontent = response.read()
    f = open(saveLocation + "Collections.json", 'wb')
    f.write(webcontent)
    f.close()

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

    #Check if the API key is blank, if so, load it
    apiKey = getAPIKey()

    #Begin appending the URL together
    #Add the collection and the start date in the correct format
    site = (siteBase + "collections/" + collection + "/"
                + startDate.replace(':', '%3A'))

    #If there is an end date, append it in the correct format
    if endDate != 'none':
        site = site + "/" + endDate.replace(':', '%3A')

    #Add the offset
    site = site + "?offset=" + str(offset)

    #Add the page size
    site = site + "&pageSize=" + str(pageSize)

    #If there is a specific congress being searched for
    if congress != -1:
        site = site + "&congress=" + str(congress)

    #IF there is a specific docClass being searched for
    if docClass != 'none':
        site = site + "&docClass=" + docClass
    
    #Add the API key
    site = site + "&api_key=" + apiKey

    #Load and save the site
    response = urllib.request.urlopen(site)
    webcontent = response.read()
    f = open(saveLocation + collection + ".json", 'wb')
    f.write(webcontent)
    f.close()

    #Outputs the current time in the YYYY-MM-DD'T'HH:MM:SS'Z' format
    #datetime.datetime.now().replace(microsecond=0).isoformat() + 'Z'

def getPackageSummary(pkgID: str):
    """
    Get package summary.\n
    pkgID   = The specific ID of the item you're looking for,
              e.g. BILLS-116s3398is
    """

    #Check if the API key is blank, if so, load it
    apiKey = getAPIKey()

    #Build the site URL.  Simple for this one as its only variables are required
    site = siteBase + "packages/" + pkgID + "/summary?api_key=" + apiKey

    #Load and save the site
    response = urllib.request.urlopen(site)
    webcontent = response.read()
    f = open(saveLocation + pkgID + ".json", 'wb')
    f.write(webcontent)
    f.close()

def getPackage(pkgID: str, contentType: str):
    """
    Get the specific package in the specified format.\n
    pkgID       = The specific ID of the itme you're looking for,
                  e.g. BILLS-116s3398is.\n
    contentType = The specific format for the content that you're looking for,
                  e.g. pdf, xml, htm, xls, mods, premis, zip.
    """

    #Check if the API key is blank, if so, load it
    apiKey = getAPIKey()

    #Build the site URL.  Simple for this one as its only variables are required
    site = (siteBase + "packages/" + pkgID + "/" + contentType + "?api_key="
            + apiKey)

    #Load and save the site
    response = urllib.request.urlopen(site)
    webcontent = response.read()
    f = open(saveLocation + pkgID + "." + contentType, 'wb')
    f.write(webcontent)
    f.close()

def getPublished(dateIssuedStart: str, collection: str, offset: int = 0,
                 pageSize: int = 10, congress: int = -1, docClass: str = 'none',
                 modifiedSince: str = 'none'):
    """
    Get a list of packages based on when they were issued.\n
    dateIssuedStart = The start date for to look for published items.\n
    collection      = The collection that the item is in e.g. BILLS.\n
    offset          = The number of items to skip before it starts displaying.
                      Starting at 0 is normal and default.  Not necessary to run.\n
    congress        = The number of the congress to search in.  Not necessary to 
                      run.\n
    docClass        = The type of classification for the item you're looking for.
                      e.g. s, hr, hres, sconres, et cetera.\n
    modifiedSince   = The date after which the item was modified in the
                      YYYY-MM-DD'T'HH:MM:SS'Z' format.  Not necessary to run.\n
    """
    
    #Check if the API key is blank, if so, load it
    apiKey = getAPIKey()

    #Begin putting the site together with the required variables
    site = (siteBase + "published/" + dateIssuedStart + "?offset="
            + str(offset) + "&pageSize=" + str(pageSize) + "&collection="
            + collection)

    #If a congress is specified, append it
    if congress != -1:
        site = site + "&congress" + str(congress)

    #If a docClass is specified, append it
    if docClass != 'none':
        site = site + "&docClass=" + docClass
    
    #If a modifiedSince date is specified, append it
    if modifiedSince != 'none':
        site = site + "&modifiedSince=" + modifiedSince.replace(":","%3A")

    #Append the api key
    site = site + "&api_key=" + apiKey

    response = urllib.request.urlopen(site)
    webcontent = response.read()
    f = open(saveLocation + "Published" + ".json", 'wb')
    f.write(webcontent)
    f.close()

getCollections()