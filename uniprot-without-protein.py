from sys import *
import csv

reader = csv.DictReader(stdin, delimiter=',')
items = {}
for item in reader:
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    #print("{}|P31|Q8054".format(it))
    print("-{}|P279|Q8054".format(it))
