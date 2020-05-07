
import csv
from sys import *

reader = csv.DictReader(open('t.tsv', 'r'), delimiter='\t')
d = {}
for item in reader:
    sp1 = item.get('sp1')
    sp2 = item.get('sp2')
    if sp1 != sp2:
        continue
    it1url = item.get('item1')
    qit1 = it1url[it1url.rfind('/')+1:]
    it2url = item.get('item2')
    qit2 = it2url[it2url.rfind('/')+1:]
    up = item.get('value')
    entry = d.get(up)
    if entry is None:
        sset = set()
        qset = set()
    else:
        sset, qset = entry
    sset.add(sp1)
    sset.add(sp2)
    qset.add(qit1)
    qset.add(qit2)
    if entry is None:
        d[up] = (sset, qset)

for (sset,qset) in d.values():
    if len(sset) > 1:
        print(qset)
        exit()
    base = qset.pop()
    try:
        while(True):
            n = qset.pop()
            print('MERGE|{}|{}'.format(n, base))
    except KeyError:
        pass
