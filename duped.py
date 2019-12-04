from sys import *
import csv

def upcase(s): return s[:1].upper() + s[1:]

reader = csv.DictReader(stdin, delimiter=',')
for item in reader:
    itemstr = item.get('item')
    itemid = itemstr[itemstr.rfind('/')+1:]
    lang = item.get('itemLabel_lang')
    if (str1 == str2):
        print("{}|L{}|\"{}\"".format(itemid, lang, str1),
            file=stdout)
