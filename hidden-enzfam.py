from sys import *
import csv

reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
    print('{}|Den|"class of enzymes"'.format(it))
