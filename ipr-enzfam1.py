import csv
from sys import *

reader = csv.DictReader(open('goid.tab', 'r'), delimiter='\t')
efs = {}
for item in reader:
    go = item.get('goid')
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    git = efs.get(go)
    if git is None:
        efs[go] = it
    else:
        print('============= {}'.format(go))

reader = csv.DictReader(open('tt', 'r'), delimiter=',')
for item in reader:
    ipr = item.get('ipr')
    go = item.get('go')
    g = efs.get(go)
    if g is None:
        print(go)
        continue
    print('{}|P31|Q67015883|S248|Q77546004'.format(ipr))
    print('{}|P680|{}|P4390|Q39894595|S248|Q77546004'.format(ipr, g))
