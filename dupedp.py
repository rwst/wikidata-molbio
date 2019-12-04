from sys import *
import csv

def locase(s): return s[:1].lower() + s[1:]

reader = csv.DictReader(stdin, delimiter='\t')
for item in reader:
    itemstr = item.get('itemLabel')
    if itemstr is None:
        continue
    pos = itemstr.find(' ')
    if pos<0:
        continue
    str1 = itemstr[:pos]
    str2 = itemstr[pos+1:]
    if (str1 == str2):
        print(itemstr)
#        print("{}|L{}|\"{}\"".format(itemid, lang, str1),
#            file=stdout)
