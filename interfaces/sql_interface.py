import datetime
import json

from mysql.connector import (
    IntegrityError, MySQLConnection, ProgrammingError, connect)

from classes.Bills import Bills
from interfaces.api_interface import logger


def get_credentials() -> MySQLConnection:
    """
    A helper function used to get the credentials for the server, simplifying
    the process.
    """
    # Try to get the credentials for the server.
    credentials = []
    try:
        with open("sensitive/database_credentials", 'rt') as key:
            for item in key:
                credentials.append(str(item).strip())
    
    # If the file isn't there, exit.
    # TODO: If exception is raised, revert to manual input from user and save
    # output to the file.
    except FileNotFoundError as file_err:
        logger.error("database_credentials does not exist. ")
        logger.error(file_err)
        exit()

    # Try the connection.
    try:
        mydb = connect(
            host=credentials[0],
            user=credentials[1],
            password=credentials[2],
            database=credentials[3])
        
        return mydb

    # If the connection cannot be established due to input error, log and quit.
    except ProgrammingError as prog_err:
        logger.critical("There was an error with the credentials")
        logger.critical(prog_err)
        exit()

def insert_bill_values(digest: bytes):
    """
    First checks if the specified bill is in the table, theninserts the values
    for it into the database if it isn't.\n
    digest  = The document that is going to be placed into the table in a bytes
              format as it is directly from the web page.
    """

    # Digest the bill so it can be parsed easily.
    vals = Bills(json.loads(digest))
    
    # Separate the vals in the last_modified date to comply with SQL standards.
    vals.last_modified = str(vals.last_modified).replace("T", " ")
    vals.last_modified = str(vals.last_modified).replace("Z","")

    # TODO: Test if this line is necessary.
    vals.last_modified = datetime.datetime.strptime(vals.last_modified,
                                                    '%Y-%m-%d %H:%M:%S')

    # I hate SQL.
    # Create the prepared statement for the INSERT.
    sql = ("INSERT INTO bills (packageId,title,shortTitle,collectionCode,"+
           "collectionName,category,dateIssued,detailsLink,download,related,"+
           "branch,pages,governmentAuthor1,governmentAuthor2,suDocClassNumber,"+
           "billtype,congress,originChamber,currentChamber,docSession,"+
           "billNumber,billVersion,isAppropriation,isPrivate,publisher,"+
           "committees,members,otherIdentifier,docReferences,lastModified) "+
           "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"+
           "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")

    # Create the values that will be inserted into the table.
    values = (str(vals.package_ID),str(vals.title),str(vals.short_title),
              str(vals.collection_code),str(vals.collection_name),
              str(vals.category),vals.date_issued,str(vals.details_link),
              str(vals.download),str(vals.related),str(vals.branch),
              int(vals.pages),str(vals.government_author_1),
              str(vals.government_author_2),str(vals.SuDoc_class_number),
              str(vals.bill_type),int(vals.congress),str(vals.origin_chamber),
              str(vals.current_chamber),str(vals.session),int(vals.bill_number),
              str(vals.bill_version),bool(vals.is_appropriation),
              bool(vals.is_private),str(vals.publisher),str(vals.committees),
              str(vals.members),str(vals.other_identifier),str(vals.references),
              str(vals.last_modified))

    # Get the connection to the database.
    mydb = get_credentials()

    # Set the cursor.
    mycursor = mydb.cursor(buffered=True)

    # Try to execute the insert command.
    # TODO: After the existance check, if it exists, check it for changes.
    try:
        mycursor.execute(sql, values)
        mydb.commit()
        logger.info(f"{vals.package_ID} successfully inserted")

    # If it fails, log that the entry already exists and move on.
    except IntegrityError as integ_err:
        logger.info(f"{vals.package_ID} is already in the database")

def check_if_exists(Id: str) -> bool:
    """
    A function that will check to see whether a specified document exists within
    a table.\n
    Id  = The packageId of the document to be checked.
    """
    # Try to get the credentials for the server.
    credentials = []
    try:
        with open("sensitive/database_credentials", 'rt') as key:
            for item in key:
                credentials.append(str(item).strip())
    
    # If the file isn't there, exit.
    # TODO: If exception is raised, revert to manual input from user and save
    # output to the file.
    except FileNotFoundError as file_err:
        logger.error("database_credentials does not exist. ")
        logger.error(file_err)
        exit()

    # Connect to the server
    mydb = get_credentials()

    # Set the cursor to the beginning.
    mycursor = mydb.cursor(buffered=True)

    # Notify the logger.
    logger.debug(f"Trying {Id}")

    # Execute the command.
    mycursor.execute(f"SELECT * FROM bills WHERE packageId=\"{Id}\";")

    # Get the value, if any.
    myresult = mycursor.fetchone()

    # If you get a result
    if(myresult):
        # Notify the logger that the document exists already and return true.
        logger.warning(f"{Id} exists in the database. Skipping.")
        return True
    
    # Otherwise, return false.
    else:
        return False

def check_all(doc_list: list, doc_type: str):
    """
    Pulls the packageId's of all of the entries in the table specified by
    doc_type then compares them to the doc_list and removes any that are already
    in the table.\n
    doc_list    = A list of documents that are to be checked to see whether
                  they're in the table yet or not.\n
    doc_type    = The type of document that is being checked. E.g. BILLS
    """
    # Get the credentials of the database.
    mydb = get_credentials()

    # Establish a cursor at the beginning of the database.
    cursor = mydb.cursor()

    # Execute the command to select all of the packageId's from the table.
    cursor.execute(f"SELECT packageId FROM {doc_type.lower()};")

    # Get the results of the search.
    result = cursor.fetchall()

    # Search through each item in the result.
    for item in result:
        # Compare each packageId to items in the list and remove it from the
        # list if it does exist in the table already.
        while item[0] in doc_list:
            doc_list.remove(item[0])
