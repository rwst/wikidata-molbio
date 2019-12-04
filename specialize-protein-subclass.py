from sys import *
import csv

s = set()
reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    if it in s:
        continue
    s.add(it)
    insturl = item.get('inst')
    inst = insturl[insturl.rfind('/')+1:]
    name = item.get('itemLabel')
    iname = item.get('instLabel')
    print('{}|P279|Q2449730'.format(it, inst))
    print('-{}|P279|Q8054'.format(it))
