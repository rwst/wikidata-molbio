from sys import *
import csv

reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    l = item.get('itemLabel')
    print('{}|Len|"{}"'.format(it, l.replace(';',',')))
