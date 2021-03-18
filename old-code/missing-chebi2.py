
import csv
from sys import *

cids = set(l.rstrip() for l in open('structclasses-in-wd', 'r').readlines())
reader = csv.DictReader(open('t.csv', 'r'), delimiter=',')
for item in reader:
    ik = item.get('ik')
    if ik is None or len(ik)==0:
        continue
    print("CREATE")
    print('LAST|Len|"{}"'.format(item.get('name')))
    print('LAST|P235|"{}"|S248|Q74165615'.format(ik))
    print('LAST|P683|"{}"'.format(item.get('CHEBI')))
    c = item.get('charge')
    if c is not None and len(c)>0:
        if int(c)>0:
            print('LAST|Den|"cation"')
            print("LAST|P31|Q43457636|S248|Q74165615")
        if int(c)<0:
            print('LAST|Den|"anion"')
            print("LAST|P31|Q43457632|S248|Q74165615")
        if int(c)==0:
            print('LAST|Den|"chemical compound"')
            print("LAST|P31|Q11173|S248|Q74165615")
    s = item.get('sub1')
    if s is not None and len(s)>0:
        if s not in cids:
            print('https://www.wikidata.org/wiki/{}'.format(s))
        print("LAST|P31|{}".format(s))
    s = item.get('sub2')
    if s is not None and len(s)>0:
        if s not in cids:
            print('https://www.wikidata.org/wiki/{}'.format(s))
        print("LAST|P31|{}".format(s))
    s = item.get('sub3')
    if s is not None and len(s)>0:
        if s not in cids:
            print('https://www.wikidata.org/wiki/{}'.format(s))
        print("LAST|P31|{}".format(s))
    s = item.get('Reaxys')
    if s is not None and len(s)>0:
        print('LAST|P1579|"{}"|S248|Q74165615'.format(s[7:]))
