import BillMe
from BillMe import *

getCollections()

with open("content/Collections.json", 'r') as collections:
    collect = collections.read()

asdf = json.loads(collect)

for item in asdf.get("collections"):
    print(item.get("collectionName"))