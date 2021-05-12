from sys import *
import csv

def locase(s): return s[:1].lower() + s[1:]

reader = csv.DictReader(stdin, delimiter=',')
for item in reader:
    itemstr = item.get('item')
    itemid = itemstr[itemstr.rfind('/')+1:]
    lang = item.get('itemLabel_lang')
    str1 = locase(item.get('str1'))
    str2 = locase(item.get('str2'))
    if (str1 == str2):
        print("{}|L{}|\"{}\"".format(itemid, lang, str1),
            file=stdout)
