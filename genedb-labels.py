from sys import *
import csv

reader = csv.DictReader(stdin, delimiter='\t')
for item in reader:
    itemstr = item.get('item')
    itemid = itemstr[itemstr.rfind('/')+1:]
    label = item.get('itemLabel')
    al = item.get('itemAl')
    if (al[:9] != "expressed"
            and al[:9] != "conserved"
            and al[:12] != "hypothetical"):
        print("{}|Len|\"{}\"".format(itemid, al),
            file=stdout)
        print("{}|Aen|\"{}\"".format(itemid, label),
            file=stdout)
