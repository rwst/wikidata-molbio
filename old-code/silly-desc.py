from sys import *
import csv

reader = csv.DictReader(stdin, delimiter='\t')
for item in reader:
    itemstr = item.get('item')
    itemid = itemstr[itemstr.rfind('/')+1:]
    label = item.get('itemLabel')
    desc = item.get('itemDesc')
    if desc[:12] == "proteïne in " and desc[12:] == label:
        print("{}|Dnl|\"{}\"".format(itemid, "proteïne in Echinococcus multilocularis"),
            file=stdout)
