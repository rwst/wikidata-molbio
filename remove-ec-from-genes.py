from sys import *
import csv

reader = csv.DictReader(open('wd-genes-with-ec.tab', 'r'), delimiter='\t')
genes = {}
for item in reader:
    ec = item.get('ec')
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    print('-{}|P591|"{}"'.format(it, ec))
