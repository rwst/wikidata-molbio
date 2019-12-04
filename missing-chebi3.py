
import csv
from sys import *

cids = set(l.rstrip() for l in open('structclasses-in-wd', 'r').readlines())
reader = csv.DictReader(open('t.csv', 'r'), delimiter=',')
for item in reader:
    ik = item.get('ik')
    if ik is not None and len(ik)>0:
        continue
    print("CREATE")
    print('LAST|Len|"{}"'.format(item.get('name')))
    print('LAST|P683|"{}"'.format(item.get('CHEBI')))
    c = item.get('charge')
    if c is not None and len(c)>0 and int(c)!=0:
        print('LAST|Den|"class of ions"')
        print("LAST|P31|Q72044356|S248|Q74165615")
    else:
        print('LAST|Den|"class of chemical compounds"')
        print("LAST|P31|Q47154513|S248|Q74165615")
    s = item.get('sub1')
    if s is not None and len(s)>0:
        if s not in cids:
            print('https://www.wikidata.org/wiki/{}'.format(s))
        print("LAST|P279|{}|S248|Q74165615".format(s))
    s = item.get('sub2')
    if s is not None and len(s)>0:
        if s not in cids:
            print('https://www.wikidata.org/wiki/{}'.format(s))
        print("LAST|P279|{}|S248|Q74165615".format(s))
    s = item.get('sub3')
    if s is not None and len(s)>0:
        if s not in cids:
            print('https://www.wikidata.org/wiki/{}'.format(s))
        print("LAST|P279|{}|S248|Q74165615".format(s))
