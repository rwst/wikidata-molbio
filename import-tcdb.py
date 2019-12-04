from sys import *
import csv

reader = csv.DictReader(open('uniprot-wd.tab', 'r'), delimiter='\t')
unips = {}
dups = set()
for item in reader:
    uid = item.get('unip')
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    git = unips.get(uid)
    if git is None or git == it:
        unips[uid] = it
    else:
        #print('more than one value: {} ({}, {})'.format(uid, git, it))
        dups.add(uid)
for k in dups:
    unips.pop(k)

uids = set(unips.keys())
tups = []
for line in stdin.readlines():
    l = line.rstrip()
    u = l[:6]
    if u not in uids:
        print(u)
        #tups.append((u, l[7:]))

#for tup in tups:
    #print('{}|P7260|"{}"'.format(unips.get(tup[0]), tup[1]))
#    print('{}|P7260|"{}"|S248|Q142667|S813|+2019-09-06T00:00:00Z/11'.format(unips.get(tup[0]), tup[1]))
